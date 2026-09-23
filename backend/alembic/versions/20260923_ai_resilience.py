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
    op.add_column("audit_events", sa.Column("input_summary", sa.String(), nullable=True))
    op.add_column("audit_events", sa.Column("result_summary", sa.String(), nullable=True))
    op.add_column("audit_events", sa.Column("approval_state", sa.String(), nullable=True))
    op.add_column("audit_events", sa.Column("reason", sa.String(), nullable=True))
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
