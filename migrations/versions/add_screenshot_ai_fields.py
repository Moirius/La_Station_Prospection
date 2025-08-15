"""Ajout des champs pour captures d'écran et analyse IA

Revision ID: add_screenshot_ai_fields
Revises: 2347601bfb52
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_screenshot_ai_fields'
down_revision = '2347601bfb52'
branch_labels = None
depends_on = None


def upgrade():
    # Ajouter les nouveaux champs pour les captures d'écran et l'analyse IA
    op.add_column('leads', sa.Column('instagram_screenshot_path', sa.String(length=500), nullable=True))
    op.add_column('leads', sa.Column('facebook_screenshot_path', sa.String(length=500), nullable=True))
    op.add_column('leads', sa.Column('ai_extraction_status', sa.String(length=50), nullable=True, server_default='en_attente'))
    op.add_column('leads', sa.Column('ai_extraction_log', sa.Text(), nullable=True))


def downgrade():
    # Supprimer les nouveaux champs
    op.drop_column('leads', 'ai_extraction_log')
    op.drop_column('leads', 'ai_extraction_status')
    op.drop_column('leads', 'facebook_screenshot_path')
    op.drop_column('leads', 'instagram_screenshot_path') 