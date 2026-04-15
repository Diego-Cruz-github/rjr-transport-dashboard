# RJR Reliable Transport - Operations Dashboard (USA)

Operations dashboard for a US vehicle transport company. Automates data extraction, integrations, task management, and email alerts.

## Stack

- **Backend:** Python, FastAPI
- **Database:** PostgreSQL
- **Scraping:** Playwright (ShipCars/SuperDispatch integration)
- **Data:** PDF parser (pdfplumber + regex), Google Sheets API (bi-directional sync)
- **Infra:** Hetzner VPS, Nginx, Docker, Cloudflare
- **Monitoring:** Automated email alerts for deadline violations and pending payments
- **Backups:** Automated daily backups with retention policy

## Features

- Automated data extraction from Central Dispatch orders (PDF parsing)
- Google Sheets bi-directional sync with existing operational spreadsheets
- Employee task management with productivity tracking
- ShipCars/SuperDispatch status sync via Playwright
- Daily/weekly automated reports
- Email alerts for deadline violations and pending payments

## Scripts

- `scripts/health_check.py` - Production health monitoring
- `scripts/db_maintenance.py` - Database maintenance and optimization

---

*Private repository - client project*
