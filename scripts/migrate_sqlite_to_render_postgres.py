#!/usr/bin/env python3
"""
Migration des leads de SQLite (local) vers PostgreSQL (Render)
Usage:
  python scripts/migrate_sqlite_to_render_postgres.py "<EXTERNAL_DATABASE_URL>"

- Le script lit la base locale SQLite: ./prospection.db
- Il insère/ignore (upsert do-nothing) dans la table 'leads' de PostgreSQL
- Il préserve les IDs existants
"""

import sys
from typing import List, Dict
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.engine import Engine
from sqlalchemy.dialects.postgresql import insert as pg_insert

SQLITE_DB_URL = 'sqlite:///prospection.db'
CHUNK_SIZE = 1000

def get_engine(db_url: str) -> Engine:
	engine = create_engine(db_url)
	return engine

def reflect_table(engine: Engine, table_name: str) -> Table:
	metadata = MetaData()
	table = Table(table_name, metadata, autoload_with=engine)
	return table

def fetch_rows_in_chunks(engine: Engine, table: Table, chunk_size: int):
	with engine.connect() as conn:
		result = conn.execute(select(table))
		buffer = []
		for row in result:
			buffer.append(dict(row._mapping))
			if len(buffer) >= chunk_size:
				yield buffer
				buffer = []
		if buffer:
			yield buffer


def upsert_chunk_pg(engine: Engine, table: Table, rows: List[Dict]):
	if not rows:
		return 0
	# On insère et on ignore en cas de conflit sur la PK 'id'
	stmt = pg_insert(table).values(rows).on_conflict_do_nothing(index_elements=['id'])
	with engine.begin() as conn:
		result = conn.execute(stmt)
		# result.rowcount peut être -1 selon le driver; on retourne la taille d'input
		return len(rows)


def main():
	if len(sys.argv) != 2:
		print("Usage: python scripts/migrate_sqlite_to_render_postgres.py \"<EXTERNAL_DATABASE_URL>\"")
		print("Astuce: révèle l'External Database URL sur la page Render de ta DB et colle-la ici.")
		sys.exit(1)

	external_pg_url = sys.argv[1]
	print("[1/4] Connexion aux bases...")
	sqlite_engine = get_engine(SQLITE_DB_URL)
	pg_engine = get_engine(external_pg_url)

	print("[2/4] Réflexion des tables 'leads'...")
	sqlite_leads = reflect_table(sqlite_engine, 'leads')
	pg_leads = reflect_table(pg_engine, 'leads')

	print("[3/4] Transfert des lignes (par paquets)...")
	total = 0
	for chunk in fetch_rows_in_chunks(sqlite_engine, sqlite_leads, CHUNK_SIZE):
		inserted = upsert_chunk_pg(pg_engine, pg_leads, chunk)
		total += inserted
		print(f"  -> {inserted} lignes transférées (cumul: {total})")

	print(f"[4/4] Terminé. Lignes transférées (tentées): {total}")
	print("Tu peux maintenant ouvrir /contacts sur Render.")

if __name__ == '__main__':
	main()
