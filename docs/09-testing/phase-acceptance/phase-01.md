# Fase 1 — Fundação Técnica

**Veredito**: 🟢 **Aprovada** (fechada em 2026-09-09, retroativamente documentada aqui — a
estrutura de Phase Acceptance só passou a existir no fechamento da Fase 2).

## Resumo

Esqueleto executável dos quatro repositórios (`crm-spec`, `crm-backend`, `crm-frontend`,
`crm-workspace`), validado contra Postgres/Redis reais e Docker. Registro completo do que foi
feito, corrigido e decidido está em [`crm-spec/CLAUDE.md`](../../../CLAUDE.md) — seções
"Fechamento operacional da Fase 1" e "Fase 1 — Fundação técnica" — não duplicado aqui.

## Critérios de aceite (do roadmap)

| Critério | Resultado |
|---|---|
| Backend e frontend sobem localmente via Docker Compose | ✅ |
| Health check responde | ✅ (`/health`, `/health/ready`) |
| CI roda lint/test com sucesso | ✅ — verde nos dois repositórios de código |

## Divergências corrigidas nesta fase

- UUID v4 → v7 em toda entidade (D-001/ADR-009).
- Refresh token TTL 30 dias → 7 dias (D-004).
- `docker-compose.yml`/scripts do workspace nascidos aninhados, corrigidos para layout de
  pastas irmãs (a pedido explícito do dono do projeto).

## Não coberto por MAT

A estrutura de Manual Acceptance Test não existia ainda nesta fase — não há MAT retroativo
para a Fase 1. A validação foi feita por smoke test manual via `curl`/Docker, registrada em
`crm-backend/CLAUDE.md`.

## Pendência transferida

`auth`, `tenants` e `users` foram construídos como adiantamento nesta fase, mas explicitamente
**não** foram considerados prontos — a Fase 2 começou revisando-os formalmente (ver
[phase-02.md](phase-02.md)).
