#!/usr/bin/env python3
"""
health_check.py - Monitoramento dos servicos do dashboard RJR
Verifica API, banco de dados e integracao com Google Sheets.
"""

import requests
import sys
from datetime import datetime


ENDPOINTS = {
    "api": "/api/health",
    "orders": "/api/orders/recent",
    "sheets_sync": "/api/sheets/status",
}


def check_service(base_url, name, path, timeout=15):
    """Verifica disponibilidade de um servico."""
    url = f"{base_url}{path}"
    try:
        resp = requests.get(url, timeout=timeout)
        elapsed = int(resp.elapsed.total_seconds() * 1000)
        status = "OK" if resp.status_code == 200 else "WARN"
        print(f"  [{status}] {name}: HTTP {resp.status_code} ({elapsed}ms)")
        return resp.status_code == 200
    except requests.exceptions.Timeout:
        print(f"  [FAIL] {name}: Timeout after {timeout}s")
        return False
    except requests.exceptions.ConnectionError:
        print(f"  [FAIL] {name}: Connection refused")
        return False
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        return False


def check_database(base_url):
    """Verifica conexao com o banco PostgreSQL."""
    try:
        resp = requests.get(f"{base_url}/api/health/db", timeout=10)
        data = resp.json()
        status = "OK" if data.get("connected") else "FAIL"
        print(f"  [{status}] PostgreSQL: {data.get('message', 'unknown')}")
        return data.get("connected", False)
    except Exception as e:
        print(f"  [FAIL] PostgreSQL: {e}")
        return False


def run_checks(base_url):
    """Executa todas as verificacoes."""
    print(f"\n[{datetime.utcnow().isoformat()}] RJR Dashboard Health Check")
    print(f"  Target: {base_url}")
    print("-" * 50)

    results = []
    for name, path in ENDPOINTS.items():
        results.append(check_service(base_url, name, path))

    results.append(check_database(base_url))

    all_ok = all(results)
    print("-" * 50)
    print(f"  Result: {'ALL HEALTHY' if all_ok else 'ISSUES DETECTED'}")
    return all_ok


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    ok = run_checks(url)
    sys.exit(0 if ok else 1)
