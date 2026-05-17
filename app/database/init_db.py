from app.database.connection import engine
from app.models.base import Base
import app.models.organisations  # noqa: F401 — registers Organisation with Base
import app.models.employees      # noqa: F401 — registers Employee with Base
import app.models.users          # noqa: F401 — registers User with Base


def init_db() -> None:
    """Create all tables that are not yet present in the database."""
    Base.metadata.create_all(bind=engine)