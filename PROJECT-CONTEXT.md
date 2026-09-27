# Project Context

> Checkpoint operacional de continuidade do projeto. **Não substitui** o [Decision Register](docs/00-governance/decision-register.md), o [Roadmap](docs/10-roadmap/roadmap.md), o [Requirements](docs/01-product/requirements.md) ou qualquer outro documento oficial do `crm-spec` — em caso de conflito, os documentos oficiais prevalecem. Serve apenas para que uma nova sessão/agente entenda rapidamente onde o projeto parou, sem reauditar tudo do zero.

## Última atualização
- **Data**: 27/09/2026
- **Commit/referência**: `0a5f681` (crm-backend)
- **Repositório**: crm-backend
- **Ação realizada**: alinhamento do README com o escopo de produto definido em D-070.

## Estado atual

Fase 3 — CRM Comercial em implementação incremental. Os incrementos 3.1 a 3.5 (Fundação Frontend Auth/RBAC, Customers/Contacts, Leads com round-robin, Pipelines, Opportunities) estão concluídos e com commits fechados nos três repositórios (`crm-backend`, `crm-frontend`, `crm-spec`). Em 2026-09-21 houve um ajuste de escopo de produto (D-070/D-071) que redefiniu o significado funcional das Fases 3–6 (CRM Comercial + Atendimento/Conversas + WhatsApp + futuro Omnichannel, sem Call Center telefônico) — esse ajuste é documental, não alterou código nem decisões já fechadas (D-031 a D-069). A documentação do `crm-backend` foi revisada em 2026-09-27 para remover a menção residual a "Call Center". O incremento 3.6 (Notes/Tasks/Appointments) ainda não foi iniciado.

## Última ação realizada

- **O que foi feito**: revisão documental do `crm-backend` para eliminar inconsistências com D-070/D-071. O README descrevia o produto como "CRM + Call Center SaaS"; passou a "CRM Comercial + Atendimento/Conversas + WhatsApp SaaS".
- **Repositório**: crm-backend
- **Commit**: `0a5f681` — `docs(product): align backend docs with crm scope`
- **Arquivos/áreas afetadas**: `README.md` (1 linha). `docs/architecture-mvp.md` foi revisado e não precisou de alteração (já não continha referência a telefonia/URA/PSTN/discador/gravação).
- **Resultado**: documentação alinhada ao escopo atual do produto. Nenhum código, Prisma/schema, migration ou funcionalidade foi alterado.
- **Push**: sim, para `origin/main`.

## Próxima etapa

- **Fase**: 3 — CRM Comercial
- **Incremento**: 3.6 — Follow-up (Notes, Tasks & Appointments)
- **Objetivo**: implementar/validar Notes, Tasks e Appointments, reutilizando modelos/módulos já existentes (não criar estruturas paralelas), integrados ao CRM existente, com tenant isolation, RBAC, soft delete, audit e OpenAPI conforme especificações; implementar o frontend correspondente; testar backend e frontend.
- **Repositório(s) envolvidos**: crm-backend, crm-frontend, crm-spec (documentação de API quando aplicável).

## Próximas ações

1. Verificar o estado real do módulo `tasks` já existente em `crm-backend` (`src/modules/tasks`) e dos modelos de Note/Task/Appointment no `schema.prisma` antes de criar qualquer estrutura nova.
2. Confirmar em `docs/04-database/entities.md` e D-031 o modelo polimórfico (`entity_type` + `entity_id`) a ser seguido para Notes/Tasks/Appointments.
3. Implementar/completar backend de Notes, Tasks e Appointments reaproveitando o módulo `tasks` existente, com validação de vínculo (`entity_type`/`entity_id` pertencentes ao mesmo tenant) coberta por teste automatizado.
4. Manter tenant isolation, RBAC, soft delete e auditoria consistentes com o restante do CRM (mesmos padrões de Customers/Leads/Opportunities).
5. Atualizar `crm-spec/docs/05-api/openapi.yaml` com o contrato de API correspondente.
6. Implementar o frontend correspondente em `crm-frontend`.
7. Rodar testes de backend e frontend (unit/integration/e2e conforme aplicável).
8. Ao concluir, atualizar este arquivo (`PROJECT-CONTEXT.md`) com data, commits dos repositórios envolvidos, resultado e a próxima etapa.

## Decisões pendentes

| ID | Decisão necessária | Impacto | Fase limite | Status |
|----|---------------------|---------|--------------|--------|
| D-071 | Modelagem de disponibilidade de consultor/atendente (estado atual vs. histórico, conjunto de estados, quem altera, escopo por fila/canal, relação com `business_hours`, fallback) | Distribuição automática de leads/conversas por disponibilidade | Antes de implementar disponibilidade (Fase 4) | `VALIDAÇÃO DE NEGÓCIO` (regra já `DECIDIDO`) |
| D-070 (pendências) | O que caracteriza uma Conversa/atendimento "finalizado"; limite de pausa e destinatário do alerta; pontos de medição do SLA; se "filas" de atendimento existem já na Fase 4 ou só na Fase 5; terminologia dos papéis "Supervisor/Operador de Call Center" | BR-15, BR-16, BR-18 e nomenclatura de papéis (Fase 4/5) | Antes da fase que as implementa (Fase 4/5) | `VALIDAÇÃO DE NEGÓCIO` |

**Nenhuma das decisões acima bloqueia o incremento 3.6** (Notes/Tasks/Appointments segue D-031, já `DECIDIDO` desde a Fase 3). Não há decisões pendentes bloqueantes para a próxima etapa.

## Restrições importantes

- Não implementar telefonia, PSTN, URA, discador ou gravação de chamadas — fora de escopo do produto (D-070).
- Não implementar disponibilidade de consultor/atendente na F3.6 — a modelagem depende de D-071, ainda em validação de negócio, e pertence à Fase 4.
- Reutilizar o módulo `tasks` e os modelos já existentes de Note/Task/Appointment antes de criar qualquer estrutura nova; manter o modelo polimórfico `entity_type` + `entity_id` (D-031), sem colunas de FK dedicadas por tipo de entidade.
- Manter tenant isolation, RBAC, soft delete e auditoria consistentes com os padrões já implementados em Customers/Leads/Opportunities.
- Não avançar automaticamente para a próxima fase (Fase 4) sem fechamento formal do incremento/fase atual.
- Não reabrir decisões já fechadas (D-031 a D-069) nem o ajuste de escopo D-070/D-071.
- `crm-spec` continua sendo a fonte oficial de especificações e decisões; este arquivo é apenas um checkpoint operacional.

## Histórico recente

| Data | Repositório | Ação | Commit | Resultado |
|------|-------------|------|--------|-----------|
| 2026-09-20 | crm-backend | Implementação de Opportunities + Pipeline (F3.5) | `d2ee3b3` | Módulo de funil implementado |
| 2026-09-20 | crm-frontend | Implementação de Opportunities + Pipeline (F3.5) | `e0063d2` | UI de funil implementada |
| 2026-09-20 | crm-spec | Documentação da API de Opportunities/Pipeline | `0387ae5` | OpenAPI atualizado |
| 2026-09-21 | crm-spec | Ajuste de escopo de produto — D-070/D-071 (CRM Comercial + Atendimento/Conversas + WhatsApp, sem Call Center telefônico) | `651b2c9` | Roadmap, business-rules e decision-register atualizados; código e decisões fechadas (D-031–D-069) preservados |
| 2026-09-27 | crm-backend | Alinhamento do README com D-070 | `0a5f681` | Documentação alinhada; nenhum código alterado; push feito |

## Roadmap atual

- **Fase atual**: Fase 3 — CRM Comercial (incrementos 3.1–3.5 concluídos; 3.6 — Notes/Tasks/Appointments — próximo)
- **Próxima fase**: Fase 4 — Atendimento/Conversas (histórico unificado de interações, disponibilidade de consultor/atendente — depende de D-071)
- **Fases posteriores (resumo)**:
  - Fase 5 — WhatsApp/Conversas (integração com provedor oficial/BSP, conversas distribuídas por disponibilidade)
  - Fase 6 — Omnichannel (novos canais além do WhatsApp em caixa de entrada unificada)
  - Fase 7 — Dashboard (indicadores de vendas e atendimento)
  - Fase 8 — Automações (campanhas, regras simples de automação)
  - Fase 9 — Escalabilidade (mediante evidência real de necessidade)
  - Fase 10+ — conforme [roadmap.md](docs/10-roadmap/roadmap.md)

## Regra de continuidade

Ao iniciar uma nova etapa:

1. Ler este arquivo primeiro.
2. Consultar os documentos oficiais referenciados quando necessário (Decision Register, Roadmap, Requirements, entities.md, etc.).
3. Verificar o estado real do repositório antes de implementar (não presumir que algo já existe ou já foi feito).
4. Não repetir trabalho já concluído.
5. Não alterar decisões já fechadas.
6. Ao finalizar uma etapa, atualizar este arquivo com a nova data, ação, commit, resultado e próxima etapa.
