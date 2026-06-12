# RJR Reliable Transport - Dashboard Operacional (EUA)

> [English](README.md) | **Português (BR)**

Dashboard operacional para uma transportadora de veículos americana, em produção desde 2026.

> **Visão geral do case** - o código de produção é privado (projeto de cliente). Esta página
> documenta o problema, a arquitetura e as decisões de engenharia.

## O problema

A operação rodava em PDFs do Central Dispatch e planilhas manuais: ordens redigitadas
à mão, status de veículo cobrado por telefone, pagamentos pendentes e prazos controlados
de memória. Lento, sujeito a erro e impossível de escalar.

## A solução

Um dashboard web que automatiza o fluxo de dados de ponta a ponta:

- **Parser de PDF** (pdfplumber + regex) extrai as ordens dos despachos do Central
  Dispatch automaticamente - sem redigitação.
- **Integração com a API do ShipCars**: ordens casadas por load id e VIN, com job
  agendado mantendo o status dos veículos sincronizado (90+ cargas ativas).
- **Motor de pendências automáticas**: camada de regras que cria e escala pendências
  (coletas atrasadas, pagamentos faltando, prazos vencendo) sem acionamento humano.
- **Controle de acesso por papel** (admin / operação) com middleware de audit log -
  toda ação é rastreável.
- **Notificações em tempo real** via bot do Telegram para eventos críticos.
- A segunda fase adicionou portal mobile do motorista, automação de SMS via OpenPhone
  (webhooks assinados com HMAC) e módulo financeiro com comissões.

## Arquitetura

```
PDFs Central Dispatch --> [ Parser (pdfplumber/regex) ]--+
                                                         |
API ShipCars <--- job de sync (APScheduler) ---> [ Backend FastAPI ] ---> PostgreSQL 16
                                                         |
                            +----------------------------+--------------+
                            |                            |              |
                     [ Dashboard web ]            [ Bot Telegram ]  [ Audit log ]
                     (RBAC: admin/ops)            (alertas em tempo real)
```

Hospedado em VPS Hetzner atrás de Nginx com TLS Let's Encrypt e DNS Cloudflare;
backups diários automatizados com retenção.

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.12, FastAPI |
| Banco | PostgreSQL 16 |
| Integrações | API ShipCars, Central Dispatch (PDF), OpenPhone (SMS), Google Sheets |
| Scraping/automação | Playwright, APScheduler |
| Infra | VPS Hetzner, Nginx, Let's Encrypt, Cloudflare, Docker |
| Notificações | Telegram Bot API |

## Notas de engenharia

- **Read-only por projeto em conta de terceiros**: a integração ShipCars roda
  estritamente em operações GET contra a conta real do broker do cliente - uma
  fronteira de segurança deliberada.
- **Sync idempotente**: a sincronização de status pode rodar repetidamente sem
  duplicar dados; falhas são logadas e expostas, nunca silenciosas.
- **Segurança de webhook**: a automação de SMS valida assinatura HMAC antes de
  processar qualquer coisa.

## Status

Em produção, atendendo a operação diária do cliente no mercado americano.
Engenheiro único: arquitetura, backend, integrações, infraestrutura e deploy.
