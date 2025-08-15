import os
import logging
from google.cloud import bigquery
from app.utils.logger import SystemLogger

def get_gcp_monthly_cost(project_id, table_id, credentials_path):
    """Récupérer le coût mensuel Google Cloud Platform"""
    try:
        SystemLogger.info(f"💰 [GCP BILLING] Début de la récupération du coût mensuel")
        SystemLogger.info(f"💰 [GCP BILLING] Project ID: {project_id}")
        SystemLogger.info(f"💰 [GCP BILLING] Table ID: {table_id}")
        SystemLogger.info(f"💰 [GCP BILLING] Credentials path: {credentials_path}")
        
        # Vérifier si le fichier de credentials existe
        if not os.path.exists(credentials_path):
            SystemLogger.error(f"❌ [GCP BILLING] Fichier de credentials non trouvé: {credentials_path}")
            raise FileNotFoundError(f"Fichier de credentials non trouvé: {credentials_path}")
        
        SystemLogger.info(f"✅ [GCP BILLING] Fichier de credentials trouvé")
        
        # Configurer les credentials
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        SystemLogger.info(f"✅ [GCP BILLING] Credentials configurés")
        
        # Créer le client BigQuery
        client = bigquery.Client(project=project_id)
        SystemLogger.info(f"✅ [GCP BILLING] Client BigQuery créé")
        
        # Construire la requête
        query = f'''
        SELECT
          SUM(cost) as total_cost
        FROM
          `{table_id}`
        WHERE
          EXTRACT(YEAR FROM usage_start_time) = EXTRACT(YEAR FROM CURRENT_DATE())
          AND EXTRACT(MONTH FROM usage_start_time) = EXTRACT(MONTH FROM CURRENT_DATE())
          AND project.id = '{project_id}'
        '''
        
        SystemLogger.info(f"🔍 [GCP BILLING] Exécution de la requête BigQuery")
        SystemLogger.info(f"🔍 [GCP BILLING] Query: {query}")
        
        # Exécuter la requête
        results = client.query(query).result()
        SystemLogger.info(f"✅ [GCP BILLING] Requête exécutée avec succès")
        
        # Récupérer le résultat
        row = next(results)
        cost = float(row.total_cost) if row.total_cost else 0.0
        
        SystemLogger.info(f"💰 [GCP BILLING] Coût mensuel récupéré: {cost:.2f} €")
        return cost
        
    except FileNotFoundError as e:
        SystemLogger.error(f"❌ [GCP BILLING] Erreur fichier credentials: {str(e)}")
        raise
    except Exception as e:
        SystemLogger.error(f"❌ [GCP BILLING] Erreur lors de la récupération du coût: {str(e)}")
        SystemLogger.error(f"❌ [GCP BILLING] Type d'erreur: {type(e).__name__}")
        raise 