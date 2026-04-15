#!/usr/bin/env python3
"""
db_maintenance.py - Manutencao e otimizacao do banco PostgreSQL
Executa VACUUM, ANALYZE e verifica tamanho das tabelas.
"""

import psycopg2
import sys
from datetime import datetime


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "rjr_db",
    "user": "rjr_user",
    "password": "",  # Usar variavel de ambiente em producao
}


def get_table_sizes(cursor):
    """Retorna tamanho de cada tabela no banco."""
    cursor.execute("""
        SELECT
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname || '.' || tablename)) as size,
            pg_total_relation_size(schemaname || '.' || tablename) as size_bytes
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size(schemaname || '.' || tablename) DESC
    """)
    return cursor.fetchall()


def run_vacuum(cursor, conn):
    """Executa VACUUM ANALYZE em todas as tabelas."""
    conn.autocommit = True
    cursor.execute("""
        SELECT tablename FROM pg_tables WHERE schemaname = 'public'
    """)
    tables = cursor.fetchall()

    for (table,) in tables:
        try:
            cursor.execute(f"VACUUM ANALYZE {table}")
            print(f"  [OK] VACUUM ANALYZE {table}")
        except Exception as e:
            print(f"  [WARN] {table}: {e}")


def check_connections(cursor):
    """Verifica conexoes ativas no banco."""
    cursor.execute("""
        SELECT count(*) as total,
               count(*) FILTER (WHERE state = 'active') as active,
               count(*) FILTER (WHERE state = 'idle') as idle
        FROM pg_stat_activity
        WHERE datname = current_database()
    """)
    row = cursor.fetchone()
    print(f"  Conexoes: {row[0]} total, {row[1]} ativas, {row[2]} idle")


def run_maintenance():
    """Executa manutencao completa do banco."""
    print(f"\n[{datetime.utcnow().isoformat()}] Database Maintenance")
    print("-" * 50)

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print("\n  Table sizes:")
        for table, size, _ in get_table_sizes(cursor):
            print(f"    {table}: {size}")

        print("\n  Connections:")
        check_connections(cursor)

        print("\n  VACUUM ANALYZE:")
        run_vacuum(cursor, conn)

        cursor.close()
        conn.close()

        print("\n" + "-" * 50)
        print("  Result: MAINTENANCE COMPLETE")
        return True

    except Exception as e:
        print(f"  [FAIL] Database connection: {e}")
        return False


if __name__ == "__main__":
    ok = run_maintenance()
    sys.exit(0 if ok else 1)
