"""ajout champ business_type dans lead

Revision ID: add_business_type_to_leads
Revises: 2347601bfb52
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_business_type_to_leads'
down_revision = '2347601bfb52'
branch_labels = None
depends_on = None


def upgrade():
    # Ajouter le champ business_type à la table leads
    with op.batch_alter_table('leads', schema=None) as batch_op:
        batch_op.add_column(sa.Column('business_type', sa.String(length=100), nullable=True))


def downgrade():
    # Supprimer le champ business_type de la table leads
    with op.batch_alter_table('leads', schema=None) as batch_op:
        batch_op.drop_column('business_type') 