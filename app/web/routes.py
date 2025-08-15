"""
Routes Flask pour l'interface web
"""

from flask import render_template, request, jsonify, redirect, url_for, current_app, send_file
from app.services.scraping_service import ScrapingService
from app.services.screenshot_service import ScreenshotService
from app.services.ai_analysis_service import AIAnalysisService
from app.utils.logger import get_logger, get_logs, get_logs_summary, clear_logs, SystemLogger, WebLogger
from app.database.models import Lead
from app.database.database import db
import os
from app.utils.gcp_billing import get_gcp_monthly_cost
from app.prompts import WEBSITE_ANALYSIS_PROMPT, SCREENSHOT_ANALYSIS_PROMPT, LEAD_SCORING_PROMPT, SYSTEM_PROMPT
import json

logger = get_logger('web_routes')

def register_routes(app):
    """Enregistrer toutes les routes"""
    
    @app.route('/')
    def dashboard():
        """Page d'accueil - Dashboard"""
        WebLogger.info("Accès à la page dashboard")
        return render_template('dashboard.html')
    
    @app.route('/simple')
    def dashboard_simple():
        """Page de test simple"""
        WebLogger.info("Accès à la page dashboard simple")
        return render_template('dashboard_simple.html')
    
    @app.route('/scraping-map')
    def scraping_map():
        """Page de l'interface cartographique"""
        WebLogger.info("Accès à la page de scraping cartographique")
        return render_template('scraping_map.html')
    
    @app.route('/logs')
    def logs_page():
        """Page des logs centralisés"""
        WebLogger.info("Accès à la page des logs")
        return render_template('logs.html')
    
    @app.route('/contacts')
    def contacts_page():
        """Page de gestion des contacts"""
        WebLogger.info("Accès à la page de gestion des contacts")
        return render_template('contacts.html')
    
    @app.route('/prompts')
    def prompts_page():
        """Page de gestion des prompts"""
        return render_template('prompts.html')

    @app.route('/api/prompts', methods=['GET'])
    def get_prompts():
        """Récupérer tous les prompts"""
        prompts = {
            'website_analysis': {
                'name': 'Analyse des sites web',
                'description': 'Prompt pour analyser le contenu HTML des sites web',
                'content': WEBSITE_ANALYSIS_PROMPT,
                'variables': ['{url}', '{html_content}']
            },
            'screenshot_analysis': {
                'name': 'Analyse des captures d\'écran',
                'description': 'Prompt pour analyser les captures d\'écran des réseaux sociaux',
                'content': SCREENSHOT_ANALYSIS_PROMPT,
                'variables': ['{platform}']
            },
            'lead_scoring': {
                'name': 'Scoring des leads',
                'description': 'Prompt pour évaluer et scorer les leads',
                'content': LEAD_SCORING_PROMPT,
                'variables': []
            },
            'system_prompt': {
                'name': 'Prompt système',
                'description': 'Prompt système pour l\'API OpenAI',
                'content': SYSTEM_PROMPT,
                'variables': []
            }
        }
        return jsonify(prompts)

    @app.route('/api/prompts/<prompt_type>', methods=['PUT'])
    def update_prompt(prompt_type):
        """Mettre à jour un prompt"""
        try:
            data = request.get_json()
            new_content = data.get('content')
            
            if not new_content:
                return jsonify({'success': False, 'message': 'Contenu manquant'}), 400
            
            # Ici on pourrait sauvegarder dans un fichier ou une base de données
            # Pour l'instant, on retourne juste un succès
            return jsonify({'success': True, 'message': 'Prompt mis à jour'})
            
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/api/start-scraping-smart', methods=['POST'])
    def start_scraping_smart():
        """Démarrer le scraping optimisé"""
        logger.info("🚀 [API] Démarrage du scraping optimisé")
        
        try:
            data = request.get_json()
            
            location = data.get('location')
            business_type = data.get('business_type', '')
            radius = data.get('radius', 5000)
            min_rating = data.get('min_rating', 4.0)
            min_reviews = data.get('min_reviews', 10)
            max_results = data.get('max_results', 20)
            anti_hotels = bool(int(data.get('anti_hotels', 0)))
            wide_search = bool(int(data.get('wide_search', 0)))
            
            logger.info(f"📍 [API] Paramètres reçus:")
            logger.info(f"   - Localisation: {location}")
            logger.info(f"   - Type d'entreprise: {business_type}")
            logger.info(f"   - Rayon: {radius}m")
            logger.info(f"   - Note minimum: {min_rating}")
            logger.info(f"   - Avis minimum: {min_reviews}")
            logger.info(f"   - Max résultats: {max_results}")
            logger.info(f"   - Recherche large: {wide_search}")
            
            if not location:
                logger.error("❌ [API] Localisation manquante")
                return jsonify({
                    'success': False,
                    'message': 'Localisation requise'
                }), 400
            
            scraping_service = ScrapingService()
            result = scraping_service.start_scraping_smart(
                location=location,
                business_type=business_type,
                radius=radius,
                min_rating=min_rating,
                min_reviews=min_reviews,
                max_results=max_results,
                anti_hotels=anti_hotels,
                wide_search=wide_search
            )
            
            if result['success']:
                logger.info(f"✅ [API] Scraping optimisé terminé avec succès")
                logger.info(f"📊 [API] Résultats: {result}")
            else:
                logger.error(f"❌ [API] Échec du scraping optimisé: {result['message']}")
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"❌ [API] Erreur lors du scraping optimisé: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Erreur: {str(e)}'
            }), 500
    
    @app.route('/api/business-types')
    def get_business_types():
        """API pour récupérer les types d'entreprises disponibles"""
        try:
            WebLogger.debug("Récupération des types d'entreprises")
            
            with app.app_context():
                scraping_service = ScrapingService()
                business_types = scraping_service.get_business_types()
            
            # Créer une liste formatée pour l'interface
            formatted_types = []
            for business_type in business_types:
                # Convertir le type en nom lisible
                readable_name = business_type.replace('_', ' ').title()
                formatted_types.append({
                    'value': business_type,
                    'label': readable_name
                })
            
            WebLogger.debug(f"Types d'entreprises récupérés: {len(formatted_types)} types")
            return jsonify({
                'success': True,
                'business_types': formatted_types
            })
            
        except Exception as e:
            WebLogger.error(f"Erreur API business types: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Erreur: {str(e)}'
            }), 500
    
    @app.route('/api/leads')
    def get_leads():
        """Récupérer tous les leads avec leurs coordonnées GPS"""
        logger.info("📋 [API] Récupération de tous les leads")
        
        try:
            leads = Lead.query.all()
            leads_data = []
            
            for lead in leads:
                lead_dict = lead.to_dict()
                leads_data.append(lead_dict)
            
            logger.info(f"✅ [API] {len(leads_data)} leads récupérés")
            
            return jsonify({
                'success': True,
                'leads': leads_data
            })
            
        except Exception as e:
            logger.error(f"❌ [API] Erreur lors de la récupération des leads: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Erreur: {str(e)}'
            }), 500
    
    @app.route('/api/lead/<int:lead_id>')
    def get_lead(lead_id):
        """API pour récupérer un lead spécifique"""
        try:
            WebLogger.debug(f"Récupération du lead {lead_id}")
            
            with app.app_context():
                scraping_service = ScrapingService()
                lead = scraping_service.get_lead_by_id(lead_id)
            
            if not lead:
                WebLogger.warning(f"Lead {lead_id} non trouvé")
                return jsonify({
                    'success': False,
                    'message': 'Lead non trouvé'
                }), 404
            
            return jsonify({
                'success': True,
                'lead': lead.to_dict()
            })
            
        except Exception as e:
            WebLogger.error(f"Erreur API lead {lead_id}: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Erreur: {str(e)}'
            }), 500
    
    @app.route('/api/status')
    def get_status():
        """API pour obtenir le statut de l'application"""
        try:
            with app.app_context():
                scraping_service = ScrapingService()
                leads = scraping_service.get_leads(limit=1)
            
            return jsonify({
                'success': True,
                'status': 'running',
                'database_connected': True,
                'leads_count': len(leads) if leads else 0
            })
            
        except Exception as e:
            WebLogger.error(f"Erreur API status: {str(e)}")
            return jsonify({
                'success': False,
                'status': 'error',
                'message': f'Erreur: {str(e)}'
            }), 500
    
    # Nouvelles routes pour les logs
    @app.route('/api/logs')
    def get_logs_api():
        """API pour récupérer les logs"""
        try:
            limit = int(request.args.get('limit', 100))
            level = request.args.get('level', '')
            source = request.args.get('source', '')
            
            logs = get_logs(limit=limit, level=level, source=source)
            
            return jsonify({
                'success': True,
                'logs': logs,
                'count': len(logs)
            })
            
        except Exception as e:
            WebLogger.error(f"Erreur API logs: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Erreur: {str(e)}'
            }), 500
    
    @app.route('/api/logs/summary')
    def get_logs_summary_api():
        """API pour récupérer le résumé des logs"""
        try:
            summary = get_logs_summary()
            
            return jsonify({
                'success': True,
                'summary': summary
            })
            
        except Exception as e:
            WebLogger.error(f"Erreur API logs summary: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Erreur: {str(e)}'
            }), 500
    
    @app.route('/api/logs/clear', methods=['POST'])
    def clear_logs_api():
        """API pour vider les logs"""
        try:
            clear_logs()
            WebLogger.info("Logs vidés via l'interface")
            
            return jsonify({
                'success': True,
                'message': 'Logs vidés avec succès'
            })
            
        except Exception as e:
            WebLogger.error(f"Erreur API clear logs: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Erreur: {str(e)}'
            }), 500
    
    @app.route('/api/sessions/facebook', methods=['POST'])
    def facebook_session():
        """API pour créer une session Facebook"""
        try:
            WebLogger.info("Démarrage de la création de session Facebook")
            
            # Note: L'ancien scraper Facebook a été remplacé par le système de capture d'écran + IA
            # Les sessions sont maintenant gérées automatiquement par le ScreenshotService
            
            return jsonify({
                'success': True,
                'message': 'Sessions Facebook gérées automatiquement par le système de capture d\'écran'
            })
                
        except Exception as e:
            WebLogger.error(f"Erreur création session Facebook: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Erreur: {str(e)}'
            }), 500
    
    @app.route('/api/sessions/instagram', methods=['POST'])
    def instagram_session():
        """API pour créer une session Instagram"""
        try:
            WebLogger.info("Démarrage de la création de session Instagram")
            
            from app.scrapers.instagram_session_manager import InstagramSessionManager
            
            session_manager = InstagramSessionManager()
            success = session_manager.login_instagram()
            
            if success:
                WebLogger.info("Session Instagram créée avec succès")
                return jsonify({
                    'success': True,
                    'message': 'Session Instagram créée avec succès'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Échec de la création de session Instagram'
                })
                
        except Exception as e:
            WebLogger.error(f"Erreur création session Instagram: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Erreur: {str(e)}'
            }), 500
    
    @app.route('/api/sessions/status')
    def sessions_status():
        """API pour vérifier le statut des sessions"""
        try:
            from app.scrapers.instagram_session_manager import InstagramSessionManager
            
            # Vérifier Facebook (maintenant géré automatiquement)
            fb_exists = os.path.exists('fb_cookies.pkl')
            
            # Vérifier Instagram
            insta_manager = InstagramSessionManager()
            insta_info = insta_manager.get_session_info()
            
            return jsonify({
                'success': True,
                'sessions': {
                    'facebook': {
                        'exists': fb_exists,
                        'valid': fb_exists,  # On suppose valide si existe
                        'message': 'Session Facebook disponible (gérée automatiquement)' if fb_exists else 'Aucune session Facebook'
                    },
                    'instagram': insta_info
                }
            })
            
        except Exception as e:
            WebLogger.error(f"Erreur vérification sessions: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Erreur: {str(e)}'
            }), 500
    
    # Nouvelles routes pour captures d'écran et IA
    @app.route('/api/lead/<int:lead_id>/screenshot', methods=['POST'])
    def capture_screenshot(lead_id):
        """API pour capturer les écrans d'un lead"""
        try:
            WebLogger.info(f"Capture d'écran demandée pour le lead {lead_id}")
            
            with app.app_context():
                # Récupérer le lead
                lead = Lead.query.get(lead_id)
                if not lead:
                    return jsonify({
                        'success': False,
                        'message': 'Lead non trouvé'
                    }), 404
                
                # Préparer les données
                lead_data = {
                    'id': lead.id,
                    'facebook_url': lead.facebook_url,
                    'instagram_url': lead.instagram_url
                }
                
                # Capture d'écran
                screenshot_service = ScreenshotService()
                screenshots = screenshot_service.capture_social_media(lead_data)
                
                # Sauvegarder les chemins
                if screenshots.get('facebook_screenshot'):
                    lead.facebook_screenshot_path = screenshots['facebook_screenshot']
                
                if screenshots.get('instagram_screenshot'):
                    lead.instagram_screenshot_path = screenshots['instagram_screenshot']
                
                db.session.commit()
                
                WebLogger.info(f"Captures d'écran terminées pour le lead {lead_id}")
                return jsonify({
                    'success': True,
                    'screenshots': screenshots,
                    'message': 'Captures d\'écran réalisées avec succès'
                })
                
        except Exception as e:
            WebLogger.error(f"Erreur capture d'écran lead {lead_id}: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Erreur: {str(e)}'
            }), 500
    
    @app.route('/api/lead/<int:lead_id>/analyze', methods=['POST'])
    def analyze_screenshots(lead_id):
        """API pour analyser les captures d'écran d'un lead"""
        try:
            WebLogger.info(f"Analyse IA demandée pour le lead {lead_id}")
            
            with app.app_context():
                # Récupérer le lead
                lead = Lead.query.get(lead_id)
                if not lead:
                    return jsonify({
                        'success': False,
                        'message': 'Lead non trouvé'
                    }), 404
                
                # Vérifier qu'il y a des captures d'écran
                screenshots = {}
                if lead.facebook_screenshot_path and os.path.exists(lead.facebook_screenshot_path):
                    screenshots['facebook_screenshot'] = lead.facebook_screenshot_path
                
                if lead.instagram_screenshot_path and os.path.exists(lead.instagram_screenshot_path):
                    screenshots['instagram_screenshot'] = lead.instagram_screenshot_path
                
                if not screenshots:
                    return jsonify({
                        'success': False,
                        'message': 'Aucune capture d\'écran disponible'
                    }), 400
                
                # Analyse IA
                lead.set_ai_status('en_cours')
                lead.update_ai_log("Début de l'analyse IA")
                db.session.commit()
                
                ai_service = AIAnalysisService()
                
                # Analyser chaque screenshot séparément
                ai_results = {}
                if screenshots.get('facebook_screenshot'):
                    fb_result = ai_service.analyze_social_media_screenshots(screenshots['facebook_screenshot'], 'facebook')
                    ai_results['facebook_data'] = fb_result
                
                if screenshots.get('instagram_screenshot'):
                    insta_result = ai_service.analyze_social_media_screenshots(screenshots['instagram_screenshot'], 'instagram')
                    ai_results['instagram_data'] = insta_result
                
                # Traiter les résultats Facebook
                if ai_results.get('facebook_data'):
                    fb_data = ai_results['facebook_data']
                    if fb_data.get('facebook_stats') or fb_data.get('description'):
                        lead.facebook_stats = fb_data.get('facebook_stats', '')
                        lead.description_facebook = fb_data.get('description', '')
                        lead.intro_facebook = fb_data.get('intro', '')
                        # Extraction des likes/followers depuis facebook_stats
                        if lead.facebook_stats:
                            try:
                                stats_parts = lead.facebook_stats.split('•')
                                if len(stats_parts) >= 2:
                                    likes_part = stats_parts[0].strip()
                                    followers_part = stats_parts[1].strip()
                                    import re
                                    likes_match = re.search(r'(\d+(?:\.\d+)?)\s*[KMB]?', likes_part)
                                    followers_match = re.search(r'(\d+(?:\.\d+)?)\s*[KMB]?', followers_part)
                                    if likes_match:
                                        likes_str = likes_match.group(1)
                                        if 'K' in likes_part:
                                            lead.nb_likes_facebook = int(float(likes_str) * 1000)
                                        elif 'M' in likes_part:
                                            lead.nb_likes_facebook = int(float(likes_str) * 1000000)
                                        else:
                                            lead.nb_likes_facebook = int(likes_str)
                                    if followers_match:
                                        followers_str = followers_match.group(1)
                                        if 'K' in followers_part:
                                            lead.nb_followers_facebook = int(float(followers_str) * 1000)
                                        elif 'M' in followers_part:
                                            lead.nb_followers_facebook = int(float(followers_str) * 1000000)
                                        else:
                                            lead.nb_followers_facebook = int(followers_str)
                            except Exception as e:
                                WebLogger.warning(f"Erreur extraction likes/followers Facebook: {str(e)}")
                        lead.update_ai_log(f"Analyse Facebook IA réussie: {lead.facebook_stats}")
                
                # Traiter les résultats Instagram
                if ai_results.get('instagram_data'):
                    insta_data = ai_results['instagram_data']
                    if insta_data.get('nb_followers') is not None or insta_data.get('bio'):
                        lead.nb_followers_instagram = insta_data.get('nb_followers', 0)
                        lead.nb_posts_instagram = insta_data.get('nb_posts', 0)
                        lead.nb_following_instagram = insta_data.get('nb_following', 0)
                        lead.bio_instagram = insta_data.get('bio', '')
                        lead.update_ai_log(f"Analyse Instagram IA réussie: {lead.nb_followers_instagram} followers")
                
                # Finaliser le statut
                if ai_results.get('analysis_success'):
                    lead.set_ai_status('succès')
                    lead.update_ai_log("Analyse IA terminée avec succès")
                else:
                    lead.set_ai_status('erreur')
                    lead.update_ai_log("Erreur lors de l'analyse IA")
                
                db.session.commit()
                
                WebLogger.info(f"Analyse IA terminée pour le lead {lead_id}")
                return jsonify({
                    'success': True,
                    'ai_results': ai_results,
                    'message': 'Analyse IA terminée avec succès'
                })
                
        except Exception as e:
            WebLogger.error(f"Erreur analyse IA lead {lead_id}: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Erreur: {str(e)}'
            }), 500
    
    @app.route('/api/lead/<int:lead_id>/screenshot/<platform>')
    def get_screenshot(lead_id, platform):
        """API pour récupérer une capture d'écran"""
        try:
            if platform not in ['facebook', 'instagram']:
                return jsonify({
                    'success': False,
                    'message': 'Plateforme non supportée'
                }), 400
            
            with app.app_context():
                lead = Lead.query.get(lead_id)
                if not lead:
                    return jsonify({
                        'success': False,
                        'message': 'Lead non trouvé'
                    }), 404
                
                screenshot_path = None
                if platform == 'facebook':
                    screenshot_path = lead.facebook_screenshot_path
                else:
                    screenshot_path = lead.instagram_screenshot_path
                
                if not screenshot_path or not os.path.exists(screenshot_path):
                    return jsonify({
                        'success': False,
                        'message': 'Capture d\'écran non trouvée'
                    }), 404
                
                return send_file(screenshot_path, mimetype='image/png')
                
        except Exception as e:
            WebLogger.error(f"Erreur récupération screenshot {platform} lead {lead_id}: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Erreur: {str(e)}'
            }), 500
    
    @app.route('/api/leads/recalculate-scores', methods=['POST'])
    def recalculate_opportunity_scores():
        """API pour recalculer les scores d'opportunité de tous les leads"""
        try:
            WebLogger.info("Recalcul des scores d'opportunité demandé")
            with app.app_context():
                from app.services.scraping_service import ScrapingService
                from app.services.ai_analysis_service import AIAnalysisService
                scraping_service = ScrapingService()
                ai_service = AIAnalysisService()
                leads = scraping_service.get_leads(limit=10000)  # Tous les leads
                updated = 0
                errors = 0
                for lead in leads:
                    try:
                        ai_service.score_lead_with_rag(lead)
                        updated += 1
                    except Exception as e:
                        errors += 1
                        WebLogger.error(f"Erreur recalcul lead {lead.id}: {str(e)}")
                return jsonify({
                    'success': True,
                    'message': f'Recalcul terminé',
                    'leads_updated': updated,
                    'errors': errors
                })
        except Exception as e:
            WebLogger.error(f"Erreur recalcul scores: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Erreur: {str(e)}'
            }), 500
    
    @app.route('/api/billing/month')
    def api_billing_month():
        """API pour récupérer le coût mensuel Google Cloud"""
        try:
            WebLogger.info("💰 [API BILLING] Demande de récupération du coût mensuel GCP")
            
            project_id = "lastationprospection"
            table_id = "lastationprospection.googleprice.gcp_billing_export_v1_0105A9_326158_B135A9"
            credentials_path = "lastationprospection-64ca8df5cdaf.json"
            
            WebLogger.info(f"💰 [API BILLING] Paramètres: project_id={project_id}, table_id={table_id}")
            
            cost = get_gcp_monthly_cost(project_id, table_id, credentials_path)
            
            WebLogger.info(f"💰 [API BILLING] Coût récupéré avec succès: {cost:.2f} €")
            return jsonify({"success": True, "month_cost": cost})
            
        except Exception as e:
            WebLogger.error(f"❌ [API BILLING] Erreur lors de la récupération du coût: {str(e)}")
            WebLogger.error(f"❌ [API BILLING] Type d'erreur: {type(e).__name__}")
            return jsonify({"success": False, "error": str(e)})
    
    # ===== NOUVELLES ROUTES POUR GESTION DES CONTACTS =====
    
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
                WebLogger.info(f"Lead {lead_id} marqué comme contacté par {contact_type}")
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
            WebLogger.error(f"Erreur marquage contact lead {lead_id}: {str(e)}")
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
                WebLogger.info(f"Contact {contact_type} décroché pour le lead {lead_id}")
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
            WebLogger.error(f"Erreur décrochage contact {contact_type} lead {lead_id}: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Erreur: {str(e)}'
            }), 500
    
    @app.route('/api/lead/<int:lead_id>/has-info', methods=['POST'])
    def update_lead_has_info(lead_id):
        """API pour mettre à jour si on a récupéré une information"""
        try:
            data = request.get_json()
            info_type = data.get('info_type')
            has_info = data.get('has_info', True)
            
            if not info_type:
                return jsonify({
                    'success': False,
                    'message': 'Type d\'information requis'
                }), 400
            
            lead = Lead.query.get(lead_id)
            if not lead:
                return jsonify({
                    'success': False,
                    'message': 'Lead non trouvé'
                }), 404
            
            # Mettre à jour l'information
            success = lead.update_has_info(info_type, has_info)
            
            if success:
                db.session.commit()
                WebLogger.info(f"Information {info_type} mise à jour pour le lead {lead_id}: {has_info}")
                return jsonify({
                    'success': True,
                    'message': f'Information {info_type} mise à jour',
                    'lead': lead.to_dict()
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f'Type d\'information invalide: {info_type}'
                }), 400
                
        except Exception as e:
            WebLogger.error(f"Erreur mise à jour info {info_type} lead {lead_id}: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Erreur: {str(e)}'
            }), 500
    
    @app.route('/api/leads/contacts-summary')
    def get_contacts_summary():
        """API pour obtenir un résumé des contacts"""
        try:
            leads = Lead.query.all()
            
            summary = {
                'total_leads': len(leads),
                'contact_types': {
                    'email': {'has_info': 0, 'contacted': 0},
                    'phone': {'has_info': 0, 'contacted': 0},
                    'address': {'has_info': 0, 'contacted': 0},
                    'instagram': {'has_info': 0, 'contacted': 0},
                    'facebook': {'has_info': 0, 'contacted': 0},
                    'contact_form': {'has_info': 0, 'contacted': 0}
                }
            }
            
            for lead in leads:
                # Compter les informations récupérées
                if lead.has_email:
                    summary['contact_types']['email']['has_info'] += 1
                if lead.has_phone:
                    summary['contact_types']['phone']['has_info'] += 1
                if lead.has_address:
                    summary['contact_types']['address']['has_info'] += 1
                if lead.has_instagram:
                    summary['contact_types']['instagram']['has_info'] += 1
                if lead.has_facebook:
                    summary['contact_types']['facebook']['has_info'] += 1
                if lead.has_contact_form:
                    summary['contact_types']['contact_form']['has_info'] += 1
                
                # Compter les contacts effectués
                if lead.contacted_by_email:
                    summary['contact_types']['email']['contacted'] += 1
                if lead.contacted_by_phone:
                    summary['contact_types']['phone']['contacted'] += 1
                if lead.contacted_by_address:
                    summary['contact_types']['address']['contacted'] += 1
                if lead.contacted_by_instagram:
                    summary['contact_types']['instagram']['contacted'] += 1
                if lead.contacted_by_facebook:
                    summary['contact_types']['facebook']['contacted'] += 1
                if lead.contacted_by_contact_form:
                    summary['contact_types']['contact_form']['contacted'] += 1
            
            return jsonify({
                'success': True,
                'summary': summary
            })
            
        except Exception as e:
            WebLogger.error(f"Erreur récupération résumé contacts: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Erreur: {str(e)}'
            }), 500 