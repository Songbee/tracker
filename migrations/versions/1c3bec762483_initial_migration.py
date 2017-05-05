"""initial migration

Revision ID: 1c3bec762483
Revises:
Create Date: 2017-05-05 19:14:14.313073

"""
# flake8: noqa

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '1c3bec762483'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('artists',
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('search_vector', sqlalchemy_utils.types.ts_vector.TSVectorType(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('torrents',
        sa.Column('id', sa.String(length=40), nullable=False),
        sa.Column('info', sa.PickleType(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('albums',
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('tracks', sqlalchemy_utils.types.json.JSONType(), nullable=True),
        sa.Column('search_vector', sqlalchemy_utils.types.ts_vector.TSVectorType(), nullable=True),
        sa.Column('torrent_id', sa.String(length=40), nullable=True),
        sa.Column('artist_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=True),
        sa.ForeignKeyConstraint(['artist_id'], ['artists.id'], ),
        sa.ForeignKeyConstraint(['torrent_id'], ['torrents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('albums')
    op.drop_table('torrents')
    op.drop_table('artists')
