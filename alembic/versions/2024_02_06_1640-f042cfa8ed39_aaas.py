"""AAAs

Revision ID: f042cfa8ed39
Revises: 3550b0c13b95
Create Date: 2024-02-06 16:40:59.030708

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f042cfa8ed39"
down_revision: Union[str, None] = "3550b0c13b95"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user_conversation",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_fk", sa.Uuid(), nullable=False),
        sa.Column("conversation_fk", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["conversation_fk"], ["conversation.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_fk"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("user_conversation")
    # ### end Alembic commands ###
