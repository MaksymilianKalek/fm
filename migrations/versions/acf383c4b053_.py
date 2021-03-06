"""empty message

Revision ID: acf383c4b053
Revises: 
Create Date: 2020-08-08 13:37:14.199719

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'acf383c4b053'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cat',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('description', sa.String(length=400), nullable=True),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.Column('period', sa.String(length=16), nullable=True),
    sa.Column('sex', sa.String(length=32), nullable=True),
    sa.Column('fur', sa.String(length=32), nullable=True),
    sa.Column('when_came', sa.String(length=32), nullable=True),
    sa.Column('picture', sa.String(length=64), nullable=True),
    sa.Column('googlePhoto1', sa.String(length=256), nullable=True),
    sa.Column('googlePhoto2', sa.String(length=256), nullable=True),
    sa.Column('googlePhoto3', sa.String(length=256), nullable=True),
    sa.Column('isActive', sa.Boolean(), nullable=True),
    sa.Column('isYoung', sa.Boolean(), nullable=True),
    sa.Column('readyToBeAdopted', sa.Boolean(), nullable=True),
    sa.Column('currentlyOnMeds', sa.Boolean(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cat_timestamp'), 'cat', ['timestamp'], unique=False)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_cat_timestamp'), table_name='cat')
    op.drop_table('cat')
    # ### end Alembic commands ###
