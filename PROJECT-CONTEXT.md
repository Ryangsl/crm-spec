# Project Context

> Checkpoint operacional de continuidade do projeto. **Não substitui** o [Decision Register](docs/00-governance/decision-register.md), o [Roadmap](docs/10-roadmap/roadmap.md), o [Requirements](docs/01-product/requirements.md) ou qualquer outro documento oficial do `crm-spec` — em caso de conflito, os documentos oficiais prevalecem. Serve apenas para que uma nova sessão/agente entenda rapidamente onde o projeto parou, sem reauditar tudo do zero.

## Última atualização
- **Data**: 27/09/2026
- **Commit/referência**: `ec63390` (crm-backend) · `dacf723` (crm-frontend) · `dcb4189` (crm-spec)
- **Repositório**: crm-backend, crm-frontend, crm-spec
- **Ação realizada**: implementação da F3.6 — Follow-up (Notes, Tasks & Appointments) completa (backend + OpenAPI + frontend), incluindo testes.

## Estado atual

Fase 3 — CRM Comercial em implementação incremental. Os incrementos 3.1 a 3.6 estão concluídos e com commits fechados nos três repositórios (`crm-backend`, `crm-frontend`, `crm-spec`): Fundação Frontend Auth/RBAC, Customers/Contacts, Leads com round-robin, Pipelines, Opportunities e agora Follow-up (Notes/Tasks/Appointments). Em 2026-09-21 houve um ajuste de escopo de produto (D-070/D-071) que redefiniu o significado funcional das Fases 3–6 (CRM Comercial + Atendimento/Conversas + WhatsApp + futuro Omnichannel, sem Call Center telefônico) — ajuste documental, sem alterar código nem decisões já fechadas (D-031 a D-069). A Fase 3 está concluída; a Fase 4 (Atendimento/Conversas) ainda não foi iniciada.

## Última ação realizada

- **O que foi feito**: F3.6 — Follow-up (Notes, Tasks & Appointments), seguindo D-031 (entity_type + entity_id, sem novos tipos). Diagnóstico prévio confirmou que os models `Note`/`Task`/`Appointment` e as permissões `notes:*`/`tasks:*`/`appointments:*` já existiam (schema.prisma e seed.ts) e que só o módulo `tasks` estava implementado. Implementados os módulos `notes` e `appointments` (controller/service/repository/DTOs) reaproveitando integralmente o padrão do módulo `tasks` (tenant isolation via `TenantContextStorage`, RBAC via `RequirePermissions`, soft delete, `AuditService`). Appointments valida `starts_at < ends_at` (nova exceção `AppointmentInvalidRangeException`, 422 `APPOINTMENT_INVALID_RANGE`). Documentado o contrato OpenAPI (`/notes`, `/tasks`, `/appointments`) no crm-spec. Implementado o frontend (`src/features/follow-up`: types/services/hooks/componentes `NotesSection`/`TasksSection`/`AppointmentsSection`, mais um novo componente `Textarea`), integrado como novas seções em `CustomerDetailPage`, `LeadDetailPage` e `OpportunityDetailPage` — mesmo padrão já usado por `ContactsSection`. `assigned_to`/`user_id` são sempre o usuário autenticado (sem seletor de usuário — mesma decisão já tomada para `owner_id` de Lead, deferida para incremento futuro).
- **Repositórios/commits**:
  - crm-backend: `ec63390` — `feat(follow-up): implement Notes and Appointments; add e2e coverage for Follow-up (F3.6)`
  - crm-frontend: `dacf723` — `feat(follow-up): add Notes/Tasks/Appointments UI integrated into Customer/Lead/Opportunity detail (F3.6)`
  - crm-spec: `dcb4189` — `docs(api): document Notes/Tasks/Appointments endpoints (Fase 3.6)`
- **Arquivos/áreas afetadas**: `crm-backend/src/modules/notes/**`, `crm-backend/src/modules/appointments/**`, `crm-backend/src/app.module.ts`, `crm-backend/src/common/exceptions/domain.exception.ts`, `crm-backend/test/e2e/follow-up.e2e-spec.ts`; `crm-frontend/src/features/follow-up/**`, `crm-frontend/src/components/ui/Textarea.tsx`, e os três `*DetailPage.tsx` (Customer/Lead/Opportunity); `crm-spec/docs/05-api/openapi.yaml`. **Nenhuma migration** — `Note`/`Task`/`Appointment` já existiam no schema.
- **Resultado**: backend — 175 testes passando (35 unit + 140 e2e, incluindo 12 novos e2e de Follow-up), lint e build limpos. Frontend — 128 testes passando (15 novos de Follow-up), lint, type-check e build limpos. OpenAPI validado (YAML parseável, todos os `$ref` resolvidos).
- **Push**: sim, `origin/main` nos três repositórios.

## Próxima etapa

- **Fase**: 4 — Atendimento/Conversas
- **Objetivo**: histórico unificado de interações (Lead/Cliente/Oportunidade) e modelagem de disponibilidade de consultor/atendente — **depende de D-071 (validação de negócio) antes de iniciar a parte de disponibilidade**.
- **Repositório(s) envolvidos**: crm-backend, crm-frontend, crm-spec.

## Próximas ações

1. Antes de iniciar a Fase 4: validar com o responsável pelo produto as pendências de negócio de D-071 (estado atual vs. histórico, conjunto de estados, quem altera, escopo por fila/canal, relação com `business_hours`, fallback) e as pendências de D-070 (BR-15/16/18, terminologia de papéis).
2. Definir o desenho do módulo de Interações (histórico unificado) sem antecipar disponibilidade nem WhatsApp (Fase 5).
3. Só depois de D-071 fechado, modelar e implementar disponibilidade e sua aplicação ao Round Robin (evolução da F3.4, D-068).
4. Manter os mesmos padrões consolidados (tenant isolation, RBAC, soft delete, audit, OpenAPI, testes).
5. Ao concluir cada incremento da Fase 4, atualizar este arquivo (`PROJECT-CONTEXT.md`) com data, commits, resultado e próxima etapa.

## Decisões pendentes

| ID | Decisão necessária | Impacto | Fase limite | Status |
|----|---------------------|---------|--------------|--------|
| D-071 | Modelagem de disponibilidade de consultor/atendente (estado atual vs. histórico, conjunto de estados, quem altera, escopo por fila/canal, relação com `business_hours`, fallback) | Distribuição automática de leads/conversas por disponibilidade | Antes de implementar disponibilidade (Fase 4) | `VALIDAÇÃO DE NEGÓCIO` (regra já `DECIDIDO`) |
| D-070 (pendências) | O que caracteriza uma Conversa/atendimento "finalizado"; limite de pausa e destinatário do alerta; pontos de medição do SLA; se "filas" de atendimento existem já na Fase 4 ou só na Fase 5; terminologia dos papéis "Supervisor/Operador de Call Center" | BR-15, BR-16, BR-18 e nomenclatura de papéis (Fase 4/5) | Antes da fase que as implementa (Fase 4/5) | `VALIDAÇÃO DE NEGÓCIO` |

**Estas são as decisões que passam a bloquear a próxima etapa (Fase 4, parte de disponibilidade/atendimento)** — D-071 precisa ser resolvida com o responsável pelo produto antes de modelar disponibilidade. A Fase 3 (incluindo a F3.6, concluída) não dependia delas.

## Restrições importantes

- Não implementar telefonia, PSTN, URA, discador ou gravação de chamadas — fora de escopo do produto (D-070).
- Não implementar disponibilidade de consultor/atendente antes de D-071 ser resolvida (validação de negócio) — pertence à Fase 4, não à F3.6 (concluída sem isso).
- Reutilizar módulos/modelos já existentes antes de criar qualquer estrutura nova (ex.: F3.6 reaproveitou o padrão do módulo `tasks` para `notes`/`appointments`); manter o modelo polimórfico `entity_type` + `entity_id` (D-031), sem colunas de FK dedicadas por tipo de entidade.
- Manter tenant isolation, RBAC, soft delete e auditoria consistentes com os padrões já implementados em Customers/Leads/Opportunities/Notes/Tasks/Appointments.
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
| 2026-09-27 | crm-spec | Criação do checkpoint operacional `PROJECT-CONTEXT.md` | `60c2e22` | Arquivo criado; nenhuma decisão nova/reaberta |
| 2026-09-27 | crm-backend | F3.6 — Notes/Appointments implementados (Tasks já existia); e2e Follow-up | `ec63390` | 175 testes passando (35 unit + 140 e2e); lint/build limpos; push feito |
| 2026-09-27 | crm-frontend | F3.6 — UI de Notes/Tasks/Appointments integrada em Customer/Lead/Opportunity | `dacf723` | 128 testes passando; lint/type-check/build limpos; push feito |
| 2026-09-27 | crm-spec | F3.6 — OpenAPI de Notes/Tasks/Appointments | `dcb4189` | YAML validado, todos os $ref resolvidos; push feito |

## Roadmap atual

- **Fase atual**: Fase 3 — CRM Comercial — **concluída** (incrementos 3.1–3.6, incluindo Follow-up)
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
