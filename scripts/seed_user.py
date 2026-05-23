"""Add a user account to the users table for a given organisation."""

import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import bcrypt

from app.database.connection import SessionLocal
from app.models.organisations import Organisation
from app.models.users import User
import app.models.employees  # noqa: F401 — ensures all relationships are resolved


def _email_domain(email: str) -> str:
    return email.split("@", 1)[-1].lower()


def main() -> None:
    with SessionLocal() as session:
        # 1. org_id — must exist
        while True:
            raw = input("Enter org_id: ").strip()
            if not raw.isdigit():
                print("  org_id must be an integer.")
                continue
            org_id = int(raw)
            org = session.get(Organisation, org_id)
            if org is None:
                print(f"  No organisation with id={org_id} found.")
                continue
            break

        print(f"  Organisation: {org.org_name} (domain: {org.domain or 'not set'})")

        # 2. user_email — domain must match org domain
        while True:
            user_email = input("Enter user email: ").strip().lower()
            if "@" not in user_email:
                print("  Invalid email address.")
                continue
            if org.domain and _email_domain(user_email) != org.domain.lower():
                print(
                    f"  Email domain must match the organisation domain '{org.domain}'."
                )
                continue
            existing = session.query(User).filter_by(org_id=org_id, user_email=user_email).first()
            if existing:
                print("  A user with this email already exists for this organisation.")
                continue
            break

        # 3. password — plain text input, stored as bcrypt hash
        while True:
            password = getpass.getpass("Enter password: ")
            if len(password) < 8:
                print("  Password must be at least 8 characters.")
                continue
            confirm = getpass.getpass("Confirm password: ")
            if password != confirm:
                print("  Passwords do not match.")
                continue
            break

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        user = User(org_id=org_id, user_email=user_email, hashed_password=hashed_password)
        session.add(user)
        session.commit()
        org_name = org.org_name

    print(f"User '{user_email}' created successfully for organisation '{org_name}'.")


if __name__ == "__main__":
    main()
