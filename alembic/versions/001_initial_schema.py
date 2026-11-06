"""Create initial schema and required user roles."""

from alembic import op
import sqlalchemy as sa

from app.db.session import Base

revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all application tables and initial roles."""
    Base.metadata.create_all(bind=op.get_bind())
    user_groups = sa.table("user_groups", sa.column("name", sa.String))
    op.bulk_insert(
        user_groups,
        [{"name": "user"}, {"name": "moderator"}, {"name": "admin"}],
    )


def downgrade() -> None:
    """Remove application tables."""
    Base.metadata.drop_all(bind=op.get_bind())
