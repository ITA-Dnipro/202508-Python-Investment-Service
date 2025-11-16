"""create investment_requests table

Revision ID: 0001_init_investment_requests
Revises: 
Create Date: 2025-10-28T11:46:55.427543Z
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_init_investment_requests"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "investment_requests",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("project_id", sa.Integer, nullable=False),
        sa.Column("investor_id", sa.Integer, nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("message", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="Pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint("amount > 0", name="ck_amount_positive"),
    )
    op.create_index("ix_investment_requests_project_id", "investment_requests", ["project_id"])
    op.create_index("ix_investment_requests_investor_id", "investment_requests", ["investor_id"])

def downgrade() -> None:
    op.drop_index("ix_investment_requests_investor_id", table_name="investment_requests")
    op.drop_index("ix_investment_requests_project_id", table_name="investment_requests")
    op.drop_table("investment_requests")
