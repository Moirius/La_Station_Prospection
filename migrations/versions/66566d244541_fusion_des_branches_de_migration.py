"""Fusion des branches de migration

Revision ID: 66566d244541
Revises: add_business_type_to_leads, add_screenshot_ai_fields
Create Date: 2025-07-12 20:06:37.987585

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '66566d244541'
down_revision = ('add_business_type_to_leads', 'add_screenshot_ai_fields')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
