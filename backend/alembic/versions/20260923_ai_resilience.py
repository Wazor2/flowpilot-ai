"""Add AI provider attempts and structured audit fields.

Revision ID: 20260923_ai_resilience
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "20260923_ai_resilience"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())
    if "audit_events" in tables:
        columns = {column["name"] for column in inspector.get_columns("audit_events")}
        for name in ("input_summary", "result_summary", "approval_state", "reason"):
            if name not in columns:
                op.add_column("audit_events", sa.Column(name, sa.String(), nullable=True))
    if "ai_runs" not in tables:
        op.create_table(
            "ai_runs",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("workflow_id", sa.String(), sa.ForeignKey("workflows.id"), nullable=True),
            sa.Column("provider", sa.String(), nullable=False),
            sa.Column("attempt", sa.Integer(), nullable=False),
            sa.Column("status", sa.String(), nullable=False),
            sa.Column("error", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        )


def downgrade() -> None:
    op.drop_table("ai_runs")
    op.drop_column("audit_events", "reason")
    op.drop_column("audit_events", "approval_state")
    op.drop_column("audit_events", "result_summary")
    op.drop_column("audit_events", "input_summary")
