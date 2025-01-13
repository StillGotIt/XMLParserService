"""created models

Revision ID: 2860bb8cea1e
Revises: 
Create Date: 2025-01-13 04:24:37.692495

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2860bb8cea1e"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "activities",
        sa.Column("code", sa.String(length=10), nullable=True),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "contractors",
        sa.Column("full_name", sa.Text(), nullable=False),
        sa.Column("short_name", sa.Text(), nullable=True),
        sa.Column("inn", sa.String(length=12), nullable=False),
        sa.Column("kpp", sa.String(length=9), nullable=True),
        sa.Column("ogrn", sa.String(length=15), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("inn"),
        sa.UniqueConstraint("ogrn"),
    )
    op.create_table(
        "activities_contractors",
        sa.Column("contractor_id", sa.Integer(), nullable=False),
        sa.Column("activity_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["activity_id"], ["activities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["contractor_id"], ["contractors.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("contractor_id", "activity_id"),
    )
    op.create_table(
        "addresses",
        sa.Column("contractor_id", sa.Integer(), nullable=False),
        sa.Column("region", sa.Text(), nullable=True),
        sa.Column("locality", sa.Text(), nullable=True),
        sa.Column("municipality", sa.Text(), nullable=True),
        sa.Column("street", sa.Text(), nullable=True),
        sa.Column("building", sa.Text(), nullable=True),
        sa.Column("postal_code", sa.String(length=6), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(
            ["contractor_id"], ["contractors.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("addresses")
    op.drop_table("activities_contractors")
    op.drop_table("contractors")
    op.drop_table("activities")
    # ### end Alembic commands ###
