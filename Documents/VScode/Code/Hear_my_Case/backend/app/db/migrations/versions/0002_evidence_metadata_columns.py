"""Add evidence metadata columns."""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_evidence_metadata_columns"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add OCR and AI metadata columns to evidence."""
    op.add_column("evidence", sa.Column("auto_tags", sa.JSON(), nullable=True))
    op.add_column("evidence", sa.Column("extracted_text", sa.Text(), nullable=True))
    op.add_column("evidence", sa.Column("ai_summary", sa.Text(), nullable=True))


def downgrade() -> None:
    """Remove OCR and AI metadata columns from evidence."""
    op.drop_column("evidence", "ai_summary")
    op.drop_column("evidence", "extracted_text")
    op.drop_column("evidence", "auto_tags")

