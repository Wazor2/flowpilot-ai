"""Persist action IDs to prevent duplicate email sends.

Revision ID: 20260924_email_action_idem
Revises: 20260923_ai_resilience
"""
from alembic import op
import sqlalchemy as sa


revision = "20260924_email_action_idem"
down_revision = "20260923_ai_resilience"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())
    if "tool_executions" not in tables:
        return

    columns = {column["name"] for column in inspector.get_columns("tool_executions")}
    if "action_id" not in columns:
        op.add_column("tool_executions", sa.Column("action_id", sa.String(), nullable=True))

    indexes = {index["name"] for index in inspector.get_indexes("tool_executions")}
    index_name = "ix_tool_executions_action_id"
    if index_name not in indexes:
        op.create_index(index_name, "tool_executions", ["action_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_tool_executions_action_id", table_name="tool_executions")
    op.drop_column("tool_executions", "action_id")
