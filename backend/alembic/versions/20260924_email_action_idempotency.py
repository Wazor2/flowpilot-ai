"""Persist action IDs to prevent duplicate email sends.

Revision ID: 20260924_email_action_idempotency
Revises: 20260923_ai_resilience
"""
from alembic import op
import sqlalchemy as sa


revision = "20260924_email_action_idempotency"
down_revision = "20260923_ai_resilience"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tool_executions", sa.Column("action_id", sa.String(), nullable=True))
    op.create_index("ix_tool_executions_action_id", "tool_executions", ["action_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_tool_executions_action_id", table_name="tool_executions")
    op.drop_column("tool_executions", "action_id")
