# Roadmap

Cada fase só inicia com a anterior aceita (critérios de aceite cumpridos). Detalhamento do que compõe o MVP está em [mvp.md](mvp.md).

## Regra de bloqueio por decisão

> Nenhuma decisão pendente bloqueia uma fase quando não impacta diretamente seus critérios de aceite ou a arquitetura necessária para ela.

Decisões vivem no [Decision Register](../00-governance/decision-register.md), classificadas como `DECIDIDO`, `PROPOSTO`, `ADIADO`, `VALIDAÇÃO DE NEGÓCIO` ou `BLOQUEADOR`. Apenas `BLOQUEADOR` impede o início da fase correspondente — e **não há nenhum bloqueador aberto hoje**.

| Antes desta fase, resolver | Decisões |
|---|---|
| **Fase 1** | Fundação técnica: identificador, validação de DTO, estado global do frontend, E2E, CI, branches, ambiente local. Todas resolvidas. |
| **Fase 2** | Multi-tenancy, tenant context, JWT, refresh token, RBAC, auditoria (D-002, D-004, D-005, D-016, D-037 resolvidas; D-003 e D-006 a fechar até o fim da fase) |
| **Fase 3** | CRM, pipeline, campos personalizados, paginação (D-007, D-008, D-031, D-032, D-033, D-034, D-035, D-058, D-065, D-066, D-067, D-068, D-069 — todas `DECIDIDO`. Decision Gate e Implementation Gate fechados em 2026-09-16, nada pendente) |
| **Fase 5** | Provedor de telefonia (D-010), WebSocket (D-013), secrets (D-025), circuit breaker (D-039) |
| **Fase 6** | Provedor de WhatsApp (D-011) |
| **Antes do 1º cliente em produção** | Staging (D-027), retenção de backup (D-028), teste de restore (D-029), paleta de marca (D-043), fluxo LGPD (D-047) |

Fases 1 a 4 **não dependem** de telefonia, WhatsApp, IA, escalabilidade avançada, Kubernetes, microsserviços ou de qualquer provedor externo futuro.

## FASE 0 — Especificação ✅ *concluída*
- **Objetivo**: produzir a documentação completa que permita implementar o sistema com segurança (este repositório).
- **Funcionalidades**: nenhuma (documentação apenas).
- **Dependências**: nenhuma.
- **Critérios de aceite**: vision, personas, requisitos, arquitetura, modelo de dados, contrato de API inicial, roadmap e ADRs iniciais existentes e sem contradição entre si; toda decisão classificada no [Decision Register](../00-governance/decision-register.md), sem bloqueadores abertos para a Fase 1. **Atendidos.**
- **Riscos**: requisitos de negócio presumidos incorretamente por falta de validação com stakeholders — mitigado marcando `[VALIDAÇÃO DE NEGÓCIO NECESSÁRIA]` em vez de inventar.

## FASE 1 — Fundação técnica ✅ *concluída em 2026-09-08*
- **Objetivo**: esqueleto executável dos repositórios `crm-backend` e `crm-frontend`.
- **Funcionalidades**: setup de `crm-backend` (NestJS, Prisma com UUID v7, estrutura de módulos, health checks, logging estruturado, Redis/BullMQ disponíveis), setup de `crm-frontend` (Vite, Tailwind, roteamento, design system inicial com paleta placeholder, PWA), Docker Compose local, CI básico.
- **Não faz parte**: WebSocket ([D-013](../00-governance/decision-register.md#d-013--websocket)), adapters de canal, filas além do necessário ([D-012](../00-governance/decision-register.md#d-012--redis--bullmq)).
- **Dependências**: Fase 0 aceita. **Nenhuma decisão pendente bloqueia esta fase.**
- **Critérios de aceite**: backend e frontend sobem localmente (infra via Docker Compose, app via `npm run dev`); health check responde; CI roda lint/test com sucesso.
- **Riscos**: antecipar infraestrutura de fases futuras (WebSocket, canais, filas) — mitigado pela lista explícita de "não faz parte" acima.

## FASE 2 — Autenticação + Usuários + Tenants ✅ *fechada em 2026-09-09 — 🟡 apta com ressalvas*
- **Objetivo**: multi-tenancy e RBAC funcionando de ponta a ponta.
- **Ponto de partida atípico**: `auth`, `tenants` e `users` já foram construídos durante a Fase 1 (com E2E de isolamento entre tenants passando). Esta fase **começou revisando** esse código contra [personas.md](../01-product/personas.md), [ADR-008](../adr/ADR-008.md) e as regras de [business-rules.md](../02-business/business-rules.md) — não presumiu que estava pronto, e encontrou 3 divergências de segurança (corrigidas).
- **Funcionalidades**: login/refresh/logout/logout-all, CRUD de usuários, papéis de fábrica, isolamento de tenant, auditoria básica.
- **Dependências**: Fase 1.
- **Critérios de aceite**: testes automatizados de isolamento entre tenants e de permissão por papel passando (ver [../09-testing/testing-strategy.md](../09-testing/testing-strategy.md)); segundo tenant de teste não consegue, em nenhuma rota, ler dado do primeiro. **Atendidos** — relatório completo em [../09-testing/phase-acceptance/phase-02.md](../09-testing/phase-acceptance/phase-02.md).
- **Riscos**: vazamento cross-tenant — risco crítico, tratado com testes obrigatórios (13 casos e2e + MAT-007) antes de prosseguir para dados de negócio reais.
- **Ressalvas não bloqueantes**: RF-03 (redefinição de senha) e RF-07 (provisionamento de tenant pelo Super Admin) de [requirements.md](../01-product/requirements.md) não têm implementação nem fase declarada — não eram critério de aceite desta fase, mas precisam de dono antes de virarem dívida esquecida.

## FASE 3 — CRM ⬅ *decisões fechadas (Decision Gate 2026-09-16); aguarda autorização explícita para implementação*
- **Objetivo**: ciclo Lead → Oportunidade → Pipeline funcionando.
- **Funcionalidades**: Fundação Frontend de Auth/RBAC (primeira entrega, [D-066](../00-governance/decision-register.md#d-066--fundação-frontend-de-authrbac-faz-parte-da-fase-3)); Clientes (com Contacts como sub-recurso, [D-065](../00-governance/decision-register.md#d-065--contacts-sub-recurso-de-customer-não-módulo-próprio)), Leads (com distribuição round-robin), Oportunidades, Pipeline configurável, Tarefas, Notas, Agenda básica.
- **Dependências**: Fase 2.
- **Critérios de aceite**: fluxo completo de [../01-product/use-cases.md](../01-product/use-cases.md) UC-01 a UC-04 executável via API e UI.
- **Decisões de negócio/arquitetura fechadas nesta fase** (ver [Decision Register](../00-governance/decision-register.md)): D-031 (polimorfismo de notes/tasks/appointments), D-032 (movimentação livre no pipeline, com justificativa ao pular etapa), D-033 (lead desqualificado é reaberto, não duplicado), D-034 (valor da oportunidade opcional na criação, obrigatório por etapa individual marcada), D-035 (vendedor não exclui registros de negócio), D-058 (escopo permanece Tenant-only nesta fase), D-065 (Contacts como sub-recurso), D-066 (Fundação Frontend de Auth/RBAC), D-067 (deduplicação de Customer bloqueante), D-068 (round-robin via cursor em `tenant_settings`), D-069 (lead não atribuído gera só auditoria, sem antecipar Notificações).
- **Riscos**: modelo de campos personalizados subdimensionado — mitigado por decisão registrada em [../04-database/database.md](../04-database/database.md) seção 6.

## FASE 4 — Atendimento
- **Objetivo**: histórico unificado de interação por cliente, mesmo antes da telefonia completa.
- **Funcionalidades**: módulo de Interações (registro manual de atendimento), notas de atendimento, primeira versão de Notificações.
- **Dependências**: Fase 3.
- **Critérios de aceite**: histórico de interações de um cliente reflete leads, oportunidades e atendimentos manuais em uma linha do tempo única.
- **Riscos**: baixo — módulo majoritariamente de leitura/agregação.

## FASE 5 — Call Center
- **Objetivo**: telefonia mínima viável.
- **Funcionalidades**: Filas, status de operador, click-to-call/discagem manual, disposição de chamada, painel de supervisão em tempo real (WebSocket com fallback).
- **Dependências**: Fase 4; escolha de provedor de telefonia ([D-010](../00-governance/decision-register.md#d-010--provedor-de-telefonia), `ADIADO` — resolver **antes** desta fase, ver [../03-architecture/integrations.md](../03-architecture/integrations.md)) e implementação de WebSocket ([D-013](../00-governance/decision-register.md#d-013--websocket)).
- **Critérios de aceite**: fluxo UC-05/UC-06/UC-07 executável; SLA e status de fila visíveis em tempo real; fallback de polling testado com WebSocket desligado.
- **Riscos**: dependência de provedor externo — mitigado pela camada de abstração `ChannelAdapter` (ver [../03-architecture/architecture.md](../03-architecture/architecture.md)).

## FASE 6 — Omnichannel
- **Objetivo**: WhatsApp integrado ao histórico único do cliente.
- **Funcionalidades**: Conversas, Mensagens, Templates, webhooks de canal, idempotência e reprocessamento.
- **Dependências**: Fase 5 (reaproveita filas/atendimento); escolha do BSP de WhatsApp ([D-011](../00-governance/decision-register.md#d-011--provedor-de-whatsapp), `ADIADO` — resolver antes desta fase; direção já definida: API oficial/BSP).
- **Critérios de aceite**: UC-08 executável ponta a ponta; teste de reentrega de webhook não duplica mensagem (BR-20).
- **Riscos**: bloqueio de número por uso de provedor não oficial — mitigado pela decisão de usar API oficial/BSP como canal primário do produto (ver [integrations.md](../03-architecture/integrations.md)).

## FASE 7 — Dashboard
- **Objetivo**: indicadores confiáveis para gestores e supervisores.
- **Funcionalidades**: Dashboard de vendas (funil, conversão) e de atendimento (volume, SLA, produtividade), Relatórios exportáveis.
- **Dependências**: Fases 3-6 (dados a agregar já existem).
- **Critérios de aceite**: indicadores batem com contagem manual em cenário de teste controlado; performance de consulta não degrada a operação (RNF-01).
- **Riscos**: consulta analítica pesada impactar produção — mitigado por réplica de leitura/materialização quando necessário (ver [../03-architecture/scalability.md](../03-architecture/scalability.md)).

## FASE 8 — Automações
- **Objetivo**: reduzir trabalho manual repetitivo.
- **Funcionalidades**: Campanhas (disparo em massa via canais já integrados), regras simples de automação (ex.: notificar gerente se oportunidade parada há N dias).
- **Dependências**: Fase 6 (canais) e Fase 7 (dados para gatilhos).
- **Critérios de aceite**: campanha de teste executa via fila assíncrona sem impacto perceptível na operação síncrona.
- **Riscos**: uso indevido para spam — mitigado por limites de plano/rate limiting por tenant.

## FASE 9 — Escalabilidade
- **Objetivo**: preparar a operação para volume maior, com evidência real de necessidade.
- **Funcionalidades**: réplica de leitura, particionamento das tabelas de alto volume, adapter Redis para WebSocket multi-instância, revisão de índices com dado real de produção.
- **Dependências**: operação real gerando dado de uso suficiente para decisão informada.
- **Critérios de aceite**: RNF-01/RNF-02 sustentados sob a carga real observada.
- **Riscos**: otimizar prematuramente sem dado real — mitigado por só entrar nesta fase com evidência (ver [../03-architecture/scalability.md](../03-architecture/scalability.md) seção 8).

## FASE 10 — IA como funcionalidade do produto
- **Objetivo**: recursos de IA voltados ao usuário final (não confundir com uso de IA para desenvolver o software, ver [../../agents/](../../agents/)).
- **Funcionalidades candidatas**: sugestão de próxima ação em oportunidade, resumo automático de atendimento, transcrição de chamada. Escopo exato: [D-048](../00-governance/decision-register.md#d-048--escopo-de-ia-como-funcionalidade-do-produto) (`ADIADO`), a detalhar em documento próprio quando esta fase se aproximar.
- **Dependências**: volume de dado histórico suficiente (interações, chamadas) das fases anteriores.
- **Critérios de aceite**: a definir na especificação da fase.
- **Riscos**: custo de inferência, qualidade/alucinação, privacidade de dado de cliente usado em prompt — a tratar com o mesmo rigor de segurança do restante do sistema.
