"""
Routes Flask pour l'interface web - Version Render
"""

from flask import render_template, request, jsonify
from app import db
from app.database.models import Lead
from datetime import datetime
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_routes(app):
    """Enregistrer toutes les routes"""
    
    @app.route('/')
    def dashboard():
        """Page d'accueil - Dashboard"""
        return render_template('dashboard.html')
    
    @app.route('/contacts')
    def contacts_page():
        """Page de gestion des contacts"""
        return render_template('contacts.html')
    
    # ===== API POUR GESTION DES CONTACTS =====
    
    @app.route('/api/leads')
    def get_leads():
        """Récupérer tous les leads"""
        try:
            leads = Lead.query.all()
            leads_data = []
            
            for lead in leads:
                lead_dict = lead.to_dict()
                leads_data.append(lead_dict)
            
            logger.info(f"✅ {len(leads_data)} leads récupérés")
            
            return jsonify({
                'success': True,
                'leads': leads_data
            })
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération des leads: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Erreur: {str(e)}'
            }), 500
    
    @app.route('/api/lead/<int:lead_id>')
    def get_lead(lead_id):
        """API pour récupérer un lead spécifique"""
        try:
            lead = Lead.query.get(lead_id)
            
            if not lead:
                return jsonify({
                    'success': False,
                    'message': 'Lead non trouvé'
                }), 404
            
            return jsonify({
                'success': True,
                'lead': lead.to_dict()
            })
            
        except Exception as e:
            logger.error(f"Erreur API lead {lead_id}: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Erreur: {str(e)}'
            }), 500
    
    @app.route('/api/leads/contacts-summary')
    def get_contacts_summary():
        """API pour obtenir le résumé des contacts"""
        try:
            leads = Lead.query.all()
            
            # Compter les types de contact
            contact_types = {
                'email': {'contacted': 0, 'has_info': 0},
                'phone': {'contacted': 0, 'has_info': 0},
                'address': {'contacted': 0, 'has_info': 0},
                'instagram': {'contacted': 0, 'has_info': 0},
                'facebook': {'contacted': 0, 'has_info': 0},
                'contact_form': {'contacted': 0, 'has_info': 0}
            }
            
            for lead in leads:
                # Compter les contacts effectués
                if lead.contacted_by_email:
                    contact_types['email']['contacted'] += 1
                if lead.contacted_by_phone:
                    contact_types['phone']['contacted'] += 1
                if lead.contacted_by_address:
                    contact_types['address']['contacted'] += 1
                if lead.contacted_by_instagram:
                    contact_types['instagram']['contacted'] += 1
                if lead.contacted_by_facebook:
                    contact_types['facebook']['contacted'] += 1
                if lead.contacted_by_contact_form:
                    contact_types['contact_form']['contacted'] += 1
                
                # Compter les informations disponibles
                if lead.has_email:
                    contact_types['email']['has_info'] += 1
                if lead.has_phone:
                    contact_types['phone']['has_info'] += 1
                if lead.has_address:
                    contact_types['address']['has_info'] += 1
                if lead.has_instagram:
                    contact_types['instagram']['has_info'] += 1
                if lead.has_facebook:
                    contact_types['facebook']['has_info'] += 1
                if lead.has_contact_form:
                    contact_types['contact_form']['has_info'] += 1
            
            summary = {
                'total_leads': len(leads),
                'contact_types': contact_types
            }
            
            return jsonify({
                'success': True,
                'summary': summary
            })
            
        except Exception as e:
            logger.error(f"Erreur API contacts summary: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Erreur: {str(e)}'
            }), 500
    
    @app.route('/api/lead/<int:lead_id>/contact', methods=['POST'])
    def mark_lead_contacted(lead_id):
        """API pour marquer un lead comme contacté par un moyen spécifique"""
        try:
            data = request.get_json()
            contact_type = data.get('contact_type')
            
            if not contact_type:
                return jsonify({
                    'success': False,
                    'message': 'Type de contact requis'
                }), 400
            
            lead = Lead.query.get(lead_id)
            if not lead:
                return jsonify({
                    'success': False,
                    'message': 'Lead non trouvé'
                }), 404
            
            # Marquer comme contacté
            success = lead.mark_contacted(contact_type)
            
            if success:
                db.session.commit()
                logger.info(f"Lead {lead_id} marqué comme contacté par {contact_type}")
                return jsonify({
                    'success': True,
                    'message': f'Lead marqué comme contacté par {contact_type}',
                    'lead': lead.to_dict()
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f'Type de contact invalide: {contact_type}'
                }), 400
                
        except Exception as e:
            logger.error(f"Erreur marquage contact lead {lead_id}: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Erreur: {str(e)}'
            }), 500
    
    @app.route('/api/lead/<int:lead_id>/contact/<contact_type>', methods=['DELETE'])
    def unmark_lead_contacted(lead_id, contact_type):
        """API pour décocher un contact (marquer comme non contacté)"""
        try:
            lead = Lead.query.get(lead_id)
            if not lead:
                return jsonify({
                    'success': False,
                    'message': 'Lead non trouvé'
                }), 404
            
            # Décocher le contact
            success = lead.unmark_contacted(contact_type)
            
            if success:
                db.session.commit()
                logger.info(f"Contact {contact_type} décroché pour le lead {lead_id}")
                return jsonify({
                    'success': True,
                    'message': f'Contact {contact_type} décroché',
                    'lead': lead.to_dict()
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f'Type de contact invalide: {contact_type}'
                }), 400
                
        except Exception as e:
            logger.error(f"Erreur décrochage contact {contact_type} lead {lead_id}: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Erreur: {str(e)}'
            }), 500
    
    @app.route('/api/status')
    def get_status():
        """API pour obtenir le statut de l'application"""
        try:
            leads_count = Lead.query.count()
            
            return jsonify({
                'success': True,
                'status': 'running',
                'database_connected': True,
                'leads_count': leads_count
            })
            
        except Exception as e:
            logger.error(f"Erreur API status: {str(e)}")
            return jsonify({
                'success': False,
                'status': 'error',
                'message': f'Erreur: {str(e)}'
            }), 500
