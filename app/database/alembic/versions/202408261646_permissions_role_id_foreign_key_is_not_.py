"""permissions role_id foreign key is not nullable

Revision ID: 40dc4a75f49b
Revises: c18b1b493b3c
Create Date: 2024-08-26 16:46:18.030767

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "40dc4a75f49b"
down_revision: Union[str, None] = "c18b1b493b3c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "permissions", "role_id", existing_type=sa.INTEGER(), nullable=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("permissions", "role_id", existing_type=sa.INTEGER(), nullable=True)
    # ### end Alembic commands ###