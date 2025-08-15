"""ajout colonnes suivi contacts

Revision ID: add_contact_tracking_fields
Revises: add_business_type_to_leads
Create Date: 2024-01-15 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_contact_tracking_fields'
down_revision = 'add_business_type_to_leads'
branch_labels = None
depends_on = None


def upgrade():
    # Ajouter les colonnes pour suivi des informations récupérées
    with op.batch_alter_table('leads', schema=None) as batch_op:
        # Colonnes pour savoir si l'info a été récupérée
        batch_op.add_column(sa.Column('has_email', sa.Boolean(), nullable=True, default=False))
        batch_op.add_column(sa.Column('has_phone', sa.Boolean(), nullable=True, default=False))
        batch_op.add_column(sa.Column('has_address', sa.Boolean(), nullable=True, default=False))
        batch_op.add_column(sa.Column('has_instagram', sa.Boolean(), nullable=True, default=False))
        batch_op.add_column(sa.Column('has_facebook', sa.Boolean(), nullable=True, default=False))
        batch_op.add_column(sa.Column('has_contact_form', sa.Boolean(), nullable=True, default=False))
        
        # Colonnes pour savoir si le contact a été fait
        batch_op.add_column(sa.Column('contacted_by_email', sa.Boolean(), nullable=True, default=False))
        batch_op.add_column(sa.Column('contacted_by_phone', sa.Boolean(), nullable=True, default=False))
        batch_op.add_column(sa.Column('contacted_by_address', sa.Boolean(), nullable=True, default=False))
        batch_op.add_column(sa.Column('contacted_by_instagram', sa.Boolean(), nullable=True, default=False))
        batch_op.add_column(sa.Column('contacted_by_facebook', sa.Boolean(), nullable=True, default=False))
        batch_op.add_column(sa.Column('contacted_by_contact_form', sa.Boolean(), nullable=True, default=False))
        
        # Dates de contact pour chaque moyen
        batch_op.add_column(sa.Column('date_contacted_by_email', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('date_contacted_by_phone', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('date_contacted_by_address', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('date_contacted_by_instagram', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('date_contacted_by_facebook', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('date_contacted_by_contact_form', sa.DateTime(), nullable=True))


def downgrade():
    # Supprimer les colonnes ajoutées
    with op.batch_alter_table('leads', schema=None) as batch_op:
        # Supprimer les colonnes de dates
        batch_op.drop_column('date_contacted_by_contact_form')
        batch_op.drop_column('date_contacted_by_facebook')
        batch_op.drop_column('date_contacted_by_instagram')
        batch_op.drop_column('date_contacted_by_address')
        batch_op.drop_column('date_contacted_by_phone')
        batch_op.drop_column('date_contacted_by_email')
        
        # Supprimer les colonnes de contact
        batch_op.drop_column('contacted_by_contact_form')
        batch_op.drop_column('contacted_by_facebook')
        batch_op.drop_column('contacted_by_instagram')
        batch_op.drop_column('contacted_by_address')
        batch_op.drop_column('contacted_by_phone')
        batch_op.drop_column('contacted_by_email')
        
        # Supprimer les colonnes d'information
        batch_op.drop_column('has_contact_form')
        batch_op.drop_column('has_facebook')
        batch_op.drop_column('has_instagram')
        batch_op.drop_column('has_address')
        batch_op.drop_column('has_phone')
        batch_op.drop_column('has_email') 