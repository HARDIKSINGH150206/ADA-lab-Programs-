"""Initial schema for Hear My Case."""
from __future__ import annotations

import sys
from pathlib import Path

from alembic import op

BASE_DIR = Path(__file__).resolve().parents[4]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.db.database import Base  # noqa: E402
from app import models  # noqa: F401,E402

# revision identifiers, used by Alembic.
revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the current database schema."""
    connection = op.get_bind()
    Base.metadata.create_all(bind=connection)


def downgrade() -> None:
    """Drop the current database schema."""
    connection = op.get_bind()
    Base.metadata.drop_all(bind=connection)
