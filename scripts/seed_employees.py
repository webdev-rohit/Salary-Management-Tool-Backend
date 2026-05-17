"""Seed 10,000 employees for a given organisation into the database."""

import random
import sys
import zipfile
import xml.etree.ElementTree as ET
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import insert

from app.database.connection import SessionLocal
from app.models.employees import Employee
from app.models.organisations import Organisation
import app.models.users  # noqa: F401 — needed so SQLAlchemy can resolve Organisation.users relationship

SCRIPTS_DIR = Path(__file__).parent
TARGET_COUNT = 10_000
COUNTRIES = ["India", "USA", "Great Britain", "Brazil", "Japan"]


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------

def _read_lines(path: Path) -> list[str]:
    return [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def _read_dept_mapping(org_dir: Path) -> list[dict]:
    """Parse Dept_Job_Salary_mapping.xlsx without openpyxl (xlsx = zip of XML)."""
    NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    xlsx = org_dir / "Dept_Job_Salary_mapping.xlsx"

    with zipfile.ZipFile(xlsx) as z:
        with z.open("xl/sharedStrings.xml") as f:
            shared = [
                (si.find(f"{{{NS}}}t").text or "")
                for si in ET.parse(f).getroot()
            ]
        with z.open("xl/worksheets/sheet1.xml") as f:
            all_rows = list(ET.parse(f).getroot().find(f"{{{NS}}}sheetData"))

    def cell_val(c):
        v = c.find(f"{{{NS}}}v")
        if v is None:
            return ""
        return shared[int(v.text)] if c.get("t") == "s" else v.text

    records, current_dept = [], ""
    for row in all_rows[1:]:  # skip header row
        cols = [cell_val(c) for c in row]
        while len(cols) < 3:
            cols.append("")
        dept, job_title, salary_range = cols[0], cols[1], cols[2]
        if dept:
            current_dept = dept  # forward-fill merged cells
        low_str, high_str = salary_range.split(" - ")
        records.append({
            "department": current_dept,
            "job_title": job_title,
            "low": int(low_str.replace(",", "")),
            "high": int(high_str.replace(",", "")),
        })

    return records


# ---------------------------------------------------------------------------
# Employee record builder
# ---------------------------------------------------------------------------

def _build_employee_records(
    first_names: list[str],
    last_names: list[str],
    dept_mapping: list[dict],
    org_id: int,
    org_name: str,
) -> list[dict]:
    seen_emails: set[str] = set()
    records: list[dict] = []

    for _ in range(TARGET_COUNT):
        first = random.choice(first_names)
        last = random.choice(last_names)

        # guarantee unique email within the batch
        for _ in range(200):
            email = f"{first.lower()}{last.lower()}{random.randint(10, 99)}@{org_name.lower()}.com"
            if email not in seen_emails:
                seen_emails.add(email)
                break

        row = random.choice(dept_mapping)
        salary = Decimal(str(random.randint(row["low"], row["high"])))

        records.append({
            "org_id": org_id,
            "full_name": f"{first} {last}",
            "email": email,
            "job_title": row["job_title"],
            "department": row["department"],
            "country": random.choice(COUNTRIES),
            "salary": salary,
        })

    return records


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # 1. Validate organisation folder
    while True:
        org_name = input("Enter organisation name: ").strip()
        org_dir = SCRIPTS_DIR / org_name
        if org_dir.is_dir():
            break
        print(f"  No folder found at scripts/{org_name}/. Please enter a valid organisation name.")

    currency = input("Enter currency: ").strip()

    # 2. Load data files
    first_names = _read_lines(org_dir / "first_names.txt")
    last_names = _read_lines(org_dir / "last_names.txt")
    dept_mapping = _read_dept_mapping(org_dir)

    with SessionLocal() as session:
        # 3. Get or create organisation
        org = session.query(Organisation).filter_by(org_name=org_name).first()
        if org is None:
            org = Organisation(org_name=org_name, org_address="N/A", currency=currency)
            session.add(org)
            session.flush()
            print(f"Created organisation '{org_name}' (id={org.id}).")
        else:
            print(f"Reusing existing organisation '{org_name}' (id={org.id}).")

        # 4. Generate employee records
        print(f"Generating {TARGET_COUNT:,} employee records...")
        employee_data = _build_employee_records(
            first_names, last_names, dept_mapping, org.id, org_name
        )

        # 5. Bulk insert — single round-trip to DB
        session.execute(insert(Employee), employee_data)
        session.commit()

    print(f"Done. {TARGET_COUNT:,} employees seeded successfully.")


if __name__ == "__main__":
    main()