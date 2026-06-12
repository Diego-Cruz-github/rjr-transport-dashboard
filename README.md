# RJR Reliable Transport - Operations Dashboard (USA)
> **English** | [Português (BR)](README.pt-BR.md)

Operations dashboard for a US vehicle transport company, in production since 2026.

> **Case overview** - the production code is private (client engagement). This page
> documents the problem, the architecture and the engineering decisions.

## The problem

The company ran its dispatch operation on PDFs from Central Dispatch and manual
spreadsheets: orders re-typed by hand, vehicle status chased over the phone,
pending payments and deadlines tracked from memory. Slow, error-prone, and
impossible to scale.

## The solution

A web dashboard that automates the data pipeline end to end:

- **PDF parser** (pdfplumber + regex) extracts orders from Central Dispatch
  dispatch sheets automatically - no re-typing.
- **ShipCars API integration**: orders are matched by load id and VIN, with a
  scheduled job keeping vehicle status in sync (90+ active loads).
- **Automatic pending-task engine**: a rule layer that creates and escalates
  pendencies (late pickups, missing payments, expiring deadlines) without
  human triggering.
- **Role-based access control** (admin / operations) with a full audit log
  middleware - every action is traceable.
- **Real-time notifications** via Telegram bot for critical events.
- Second phase added a mobile driver portal, SMS automation via OpenPhone
  (HMAC-signed webhooks) and a financial module with commission handling.

## Architecture

```
Central Dispatch PDFs --> [ Parser (pdfplumber/regex) ]--+
                                                         |
ShipCars API <--- sync job (APScheduler) ---> [ FastAPI backend ] ---> PostgreSQL 16
                                                         |
                            +----------------------------+--------------+
                            |                            |              |
                     [ Web dashboard ]            [ Telegram bot ]  [ Audit log ]
                     (RBAC: admin/ops)            (real-time alerts)
```

Hosted on a Hetzner VPS behind Nginx with Let's Encrypt TLS and Cloudflare DNS;
automated daily backups with retention.

## Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI |
| Database | PostgreSQL 16 |
| Integrations | ShipCars API, Central Dispatch (PDF), OpenPhone (SMS), Google Sheets |
| Scraping/automation | Playwright, APScheduler |
| Infra | Hetzner VPS, Nginx, Let's Encrypt, Cloudflare, Docker |
| Notifications | Telegram Bot API |

## Engineering notes

- **Read-only by design on third-party production accounts**: the ShipCars
  integration runs strictly on GET operations against the client's live broker
  account - a deliberate safety boundary.
- **Idempotent sync**: status sync can run repeatedly without duplicating data;
  failures are logged and surfaced, never silent.
- **Webhook security**: SMS automation validates HMAC signatures before
  processing anything.

## Status

In production, serving daily operations for the client in the US market.
Sole engineer: architecture, backend, integrations, infrastructure and deploy.
