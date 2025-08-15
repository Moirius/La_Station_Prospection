"""
Système de logging centralisé pour l'application
"""

import logging
import os
import json
from datetime import datetime
from typing import Dict, List, Any
from app.config import Config

# Dictionnaire global pour stocker les logs en mémoire
_logs_buffer = []
_max_logs = 1000  # Limite de logs en mémoire

def setup_logger(name='prospection', level=None):
    """Configurer le logger principal"""
    
    # Créer le dossier logs s'il n'existe pas
    log_dir = os.path.dirname(Config.LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configuration du logger
    logger = logging.getLogger(name)
    logger.setLevel(level or getattr(logging, Config.LOG_LEVEL.upper()))
    
    # Éviter les handlers dupliqués
    if not logger.handlers:
        # Handler pour fichier
        file_handler = logging.FileHandler(Config.LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Handler pour console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

def get_logger(name='prospection'):
    """Obtenir le logger configuré"""
    return logging.getLogger(name)

def add_to_logs_buffer(level: str, message: str, source: str = 'system', lead_id: int = 0, lead_name: str = ''):
    """Ajouter un log au buffer en mémoire"""
    global _logs_buffer
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'level': level.upper(),
        'message': message,
        'source': source,
        'lead_id': lead_id,
        'lead_name': lead_name
    }
    
    _logs_buffer.append(log_entry)
    
    # Limiter la taille du buffer
    if len(_logs_buffer) > _max_logs:
        _logs_buffer = _logs_buffer[-_max_logs:]
    
    # Écrire aussi dans le fichier de log
    logger = get_logger()
    if level.upper() == 'ERROR':
        logger.error(f"[{source}] {message}")
    elif level.upper() == 'WARNING':
        logger.warning(f"[{source}] {message}")
    elif level.upper() == 'DEBUG':
        logger.debug(f"[{source}] {message}")
    else:
        logger.info(f"[{source}] {message}")

def get_logs(limit: int = 100, level: str = '', source: str = '') -> List[Dict[str, Any]]:
    """Récupérer les logs du buffer"""
    global _logs_buffer
    
    logs = _logs_buffer.copy()
    
    # Filtrer par niveau
    if level:
        logs = [log for log in logs if log['level'] == level.upper()]
    
    # Filtrer par source
    if source:
        logs = [log for log in logs if log['source'] == source]
    
    # Limiter le nombre de résultats
    return logs[-limit:] if limit else logs

def clear_logs():
    """Vider le buffer de logs"""
    global _logs_buffer
    _logs_buffer = []

def get_logs_summary() -> Dict[str, Any]:
    """Obtenir un résumé des logs"""
    global _logs_buffer
    
    if not _logs_buffer:
        return {
            'total_logs': 0,
            'error_count': 0,
            'warning_count': 0,
            'info_count': 0,
            'debug_count': 0,
            'last_log': None
        }
    
    error_count = len([log for log in _logs_buffer if log['level'] == 'ERROR'])
    warning_count = len([log for log in _logs_buffer if log['level'] == 'WARNING'])
    info_count = len([log for log in _logs_buffer if log['level'] == 'INFO'])
    debug_count = len([log for log in _logs_buffer if log['level'] == 'DEBUG'])
    
    return {
        'total_logs': len(_logs_buffer),
        'error_count': error_count,
        'warning_count': warning_count,
        'info_count': info_count,
        'debug_count': debug_count,
        'last_log': _logs_buffer[-1] if _logs_buffer else None
    }

class LeadLogger:
    """Logger spécialisé pour les leads"""
    
    def __init__(self, lead_id, lead_name):
        self.lead_id = lead_id
        self.lead_name = lead_name
        self.logger = get_logger(f'lead.{lead_id}')
    
    def info(self, message):
        """Log info pour le lead"""
        add_to_logs_buffer('INFO', message, 'lead', self.lead_id, self.lead_name)
        self.logger.info(f"[Lead {self.lead_id}:{self.lead_name}] {message}")
    
    def error(self, message):
        """Log error pour le lead"""
        add_to_logs_buffer('ERROR', message, 'lead', self.lead_id, self.lead_name)
        self.logger.error(f"[Lead {self.lead_id}:{self.lead_name}] {message}")
    
    def warning(self, message):
        """Log warning pour le lead"""
        add_to_logs_buffer('WARNING', message, 'lead', self.lead_id, self.lead_name)
        self.logger.warning(f"[Lead {self.lead_id}:{self.lead_name}] {message}")
    
    def debug(self, message):
        """Log debug pour le lead"""
        add_to_logs_buffer('DEBUG', message, 'lead', self.lead_id, self.lead_name)
        self.logger.debug(f"[Lead {self.lead_id}:{self.lead_name}] {message}")

class SystemLogger:
    """Logger pour les événements système"""
    
    @staticmethod
    def info(message):
        """Log info système"""
        add_to_logs_buffer('INFO', message, 'system')
    
    @staticmethod
    def error(message):
        """Log error système"""
        add_to_logs_buffer('ERROR', message, 'system')
    
    @staticmethod
    def warning(message):
        """Log warning système"""
        add_to_logs_buffer('WARNING', message, 'system')
    
    @staticmethod
    def debug(message):
        """Log debug système"""
        add_to_logs_buffer('DEBUG', message, 'system')

class WebLogger:
    """Logger pour les événements web"""
    
    @staticmethod
    def info(message):
        """Log info web"""
        add_to_logs_buffer('INFO', message, 'web')
    
    @staticmethod
    def error(message):
        """Log error web"""
        add_to_logs_buffer('ERROR', message, 'web')
    
    @staticmethod
    def warning(message):
        """Log warning web"""
        add_to_logs_buffer('WARNING', message, 'web')
    
    @staticmethod
    def debug(message):
        """Log debug web"""
        add_to_logs_buffer('DEBUG', message, 'web')

# Logger principal
main_logger = setup_logger() 