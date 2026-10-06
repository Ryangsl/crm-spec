# Roadmap

Cada fase só inicia com a anterior aceita (critérios de aceite cumpridos). Detalhamento do que compõe o MVP está em [mvp.md](mvp.md).

## Regra de bloqueio por decisão

> Nenhuma decisão pendente bloqueia uma fase quando não impacta diretamente seus critérios de aceite ou a arquitetura necessária para ela.

> **Definição de produto ([D-070](../00-governance/decision-register.md#d-070--definição-de-produto-crm-comercial--atendimentoconversas--whatsapp-sem-call-center-telefônico), 2026-09-21)**: o produto é **CRM Comercial + Atendimento/Conversas + WhatsApp + futuro Omnichannel** — não um Call Center telefônico (sem URA, PSTN, gravação de chamadas, infraestrutura de telefonia ou filas de chamadas). O ajuste abaixo muda o **significado funcional** das Fases 3 a 6; a numeração e as Fases 7–10 são preservadas.

Decisões vivem no [Decision Register](../00-governance/decision-register.md), classificadas como `DECIDIDO`, `PROPOSTO`, `ADIADO`, `VALIDAÇÃO DE NEGÓCIO` ou `BLOQUEADOR`. Apenas `BLOQUEADOR` impede o início da fase correspondente — e **não há nenhum bloqueador aberto hoje**.

| Antes desta fase, resolver | Decisões |
|---|---|
| **Fase 1** | Fundação técnica: identificador, validação de DTO, estado global do frontend, E2E, CI, branches, ambiente local. Todas resolvidas. |
| **Fase 2** | Multi-tenancy, tenant context, JWT, refresh token, RBAC, auditoria (D-002, D-004, D-005, D-016, D-037 resolvidas; D-003 e D-006 a fechar até o fim da fase) |
| **Fase 3** | CRM, pipeline, campos personalizados, paginação (D-007, D-008, D-031, D-032, D-033, D-034, D-035, D-058, D-065, D-066, D-067, D-068, D-069 — todas `DECIDIDO`. Decision Gate e Implementation Gate fechados em 2026-09-16, nada pendente) |
| **Fase 4** | Regras de negócio de disponibilidade fechadas (D-071, `DECIDIDO` em 2026-09-29; estado inicial, tenant sem disponibilidade, carteira e quem altera cada estado em 2026-10-05), Lead sem proprietário (D-075) e diretrizes A1–A3 (D-076) — **F4.0–F4.2 concluídos e integrados ao `main` em 2026-10-06; F4.3 (distribuição com disponibilidade) implementado em 2026-10-06 (branch `feat/f4-3-availability-distribution`, sem push)** (`VN-17` e comportamento com a flag desabilitada decididos — D-071/D-077). Pendentes, a decidir no incremento que os implementar: política de distribuição posterior de leads sem proprietário (`VN-16`, não definida no F4.3), `business_hours` (detalhes), ociosidade de atendimento de Cliente (D-071), BR-15/16/18 (D-070) |
| **Fase 5** | Provedor de WhatsApp (D-011), WebSocket (D-013), secrets (D-025), circuit breaker (D-039), **Gate de entrada de D-072** (arquitetura, modelo de dados, fluxos, regras de negócio, decisões críticas, provedor, fronteira F4/F5) integração por tenant/conta de canal (D-074) e reconciliação do módulo `communications` legado, **congelado**, na F5.0 (D-073). Telefonia (D-010) e discador (D-045) estão **fora de escopo** (D-070) |
| **Fase 6** | Nenhuma decisão definida hoje; provedores de canais futuros (ex.: D-040) são decididos quando entrarem no roadmap |
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

## FASE 3 — CRM Comercial ✅ *concluída (incrementos 3.1–3.6; Decision Gate 2026-09-16)*
- **Significado funcional (D-070)**: CRM Comercial — Customers, Leads, Opportunities, Pipeline e Follow-up (Tarefas/Notas/Agenda).
- **Objetivo**: ciclo Lead → Oportunidade → Pipeline funcionando.
- **Funcionalidades**: Fundação Frontend de Auth/RBAC (primeira entrega, [D-066](../00-governance/decision-register.md#d-066--fundação-frontend-de-authrbac-faz-parte-da-fase-3)); Clientes (com Contacts como sub-recurso, [D-065](../00-governance/decision-register.md#d-065--contacts-sub-recurso-de-customer-não-módulo-próprio)), Leads (com distribuição round-robin), Oportunidades, Pipeline configurável, Tarefas, Notas, Agenda básica.
- **Dependências**: Fase 2.
- **Critérios de aceite**: fluxo completo de [../01-product/use-cases.md](../01-product/use-cases.md) UC-01 a UC-04 executável via API e UI.
- **Decisões de negócio/arquitetura fechadas nesta fase** (ver [Decision Register](../00-governance/decision-register.md)): D-031 (polimorfismo de notes/tasks/appointments), D-032 (movimentação livre no pipeline, com justificativa ao pular etapa), D-033 (lead desqualificado é reaberto, não duplicado), D-034 (valor da oportunidade opcional na criação, obrigatório por etapa individual marcada), D-035 (vendedor não exclui registros de negócio), D-058 (escopo permanece Tenant-only nesta fase), D-065 (Contacts como sub-recurso), D-066 (Fundação Frontend de Auth/RBAC), D-067 (deduplicação de Customer bloqueante), D-068 (round-robin via cursor em `tenant_settings`), D-069 (lead não atribuído gera só auditoria, sem antecipar Notificações).
- **Divergência registrada ([D-071](../00-governance/decision-register.md#d-071--disponibilidade-de-consultoratendente-para-distribuição-automática))**: a distribuição round-robin implementada na Fase 3.4 considera **usuário ativo + tenant + permissão `leads:update`**, sem disponibilidade. A regra de produto (BR-05/BR-14) é **ativo + disponível + permissão**, sem vincular a disponibilidade a um papel. Nenhuma correção é feita na Fase 3: as regras de negócio de disponibilidade foram fechadas em D-071 (2026-09-29 e 2026-10-05) e sua aplicação entra na Fase 4. Lead sem proprietário é um estado legítimo ([D-075](../00-governance/decision-register.md#d-075--lead-sem-proprietário-é-um-estado-legítimo-do-negócio)).
- **Riscos**: modelo de campos personalizados subdimensionado — mitigado por decisão registrada em [../04-database/database.md](../04-database/database.md) seção 6.

## FASE 4 — Atendimento / Conversas
- **Significado funcional (D-070)**: atendimento comercial — conversas/interações ligadas a Lead/Cliente, follow-up, disponibilidade e primeiras funções de gestão de atendimento.
- **Objetivo**: histórico unificado de interação por cliente, antes da integração com WhatsApp.
- **Funcionalidades**: módulo de Interações (registro manual de atendimento), notas de atendimento, follow-up, **disponibilidade de consultor/atendente** ([D-071](../00-governance/decision-register.md#d-071--disponibilidade-de-consultoratendente-para-distribuição-automática); regras de negócio fechadas, implementação técnica a planejar), primeiras funções de gestão de atendimento, primeira versão de Notificações (quando definida). Aplicar a disponibilidade à distribuição de leads (BR-05/BR-14) é a evolução do Round Robin da Fase 3.4 — **feita no F4.3** (com a flag do tenant ligada só quem está Disponível recebe novos Leads; [D-078](../00-governance/decision-register.md#d-078--distribuição-automática-de-leads-com-disponibilidade-td-11)).
- **Dependências**: Fase 3; regras de disponibilidade fechadas em D-071 e Lead sem proprietário em D-075. Ainda a validar, no incremento correspondente: política de distribuição posterior de leads sem proprietário (`VN-16`), detalhes da ociosidade de atendimento de Cliente (D-071, BR-28) e pendências de BR-15/16/18 ([D-070](../00-governance/decision-register.md#d-070--definição-de-produto-crm-comercial--atendimentoconversas--whatsapp-sem-call-center-telefônico)) para a parte de disponibilidade/atendimento.
- **Planejamento técnico (discovery de 2026-09-30, `PROPOSTO`)**: [phase-4-plan.md](phase-4-plan.md) — módulos, modelo de dados, APIs, frontend, testes, incrementos F4.0–F4.8 (F4.6 a F4.8 condicionais a decisões de negócio), pendências `VN-xx`/`TD-xx` e análise da fronteira F4/F5. **F4.0 (fechamento de decisões) concluído**; **F4.1 — Configurações do tenant — implementado em 2026-10-05** (integrado ao `main` em 2026-10-06): `GET/PUT /v1/tenant-settings/business-hours` e `/availability`, tela `/settings/business-hours`, sem efeito operacional. **Gate de entrada do F4.2 fechado em 2026-10-05** ([D-077](../00-governance/decision-register.md#d-077--disponibilidade-modelo-de-dados-e-permissões-td-01-td-08)); **F4.2 — Disponibilidade — implementado em 2026-10-05** (integrado ao `main` em 2026-10-06): estado atual + histórico, seletor e painel da equipe. **F4.3 — Distribuição v2 — implementado em 2026-10-06** (branch `feat/f4-3-availability-distribution`, commits locais, sem push; aguardando revisão): o Round Robin de Leads passa a considerar a disponibilidade quando a flag do tenant está ligada (flag desligada = Fase 3), sem migration, rota ou UI nova. **Nenhum incremento F4.4+ iniciado.**
- **Critérios de aceite**: histórico de interações de um cliente reflete leads, oportunidades e atendimentos manuais em uma linha do tempo única.
- **Riscos**: baixo — módulo majoritariamente de leitura/agregação.

## FASE 5 — WhatsApp / Conversas
- **Significado funcional (D-070)**: WhatsApp como canal de conversa do CRM — não telefonia.
- **Objetivo**: WhatsApp integrado ao histórico único do cliente, com conversas distribuídas por disponibilidade.
- **Funcionalidades**: integração com o provedor de WhatsApp, webhooks de canal (idempotência e reprocessamento), envio e recebimento de mensagens, Conversas, Mensagens, Templates, associação de Conversa a Lead/Cliente (BR-19), **distribuição de conversas por disponibilidade** (BR-14), filas de atendimento e supervisão em tempo real (WebSocket com fallback) quando aplicável.
- **Dependências**: Fase 4 (reaproveita atendimento e disponibilidade); escolha do BSP de WhatsApp ([D-011](../00-governance/decision-register.md#d-011--provedor-de-whatsapp), `ADIADO` — resolver **antes** desta fase; direção já definida: API oficial/BSP, ver [../03-architecture/integrations.md](../03-architecture/integrations.md)) e implementação de WebSocket ([D-013](../00-governance/decision-register.md#d-013--websocket)).
- **Gate de entrada (D-072)**: a implementação **não inicia** antes de o Gate estar integralmente atendido — ver [../03-architecture/whatsapp-architecture.md §10](../03-architecture/whatsapp-architecture.md#10-gate-de-entrada-para-implementação). Discovery, arquitetura de referência, pendências (`WA-01`–`WA-30`) e incrementos propostos (F5.0–F5.7) estão no mesmo documento.
- **Fronteira F4/F5 ([D-076](../00-governance/decision-register.md#d-076--fronteira-f4f5-diretrizes-de-planejamento-da-fase-4-aprovadas-a1a3), diretrizes de planejamento aprovadas em 2026-10-05)**: o núcleo `Conversation`/`Message` agnóstico pode ser entregue no **F4.6** — e, se suas regras não estiverem fechadas, **desloca-se para o F5.0**; disponibilidade, distribuição e `business_hours` são da **Fase 4**; `channel_account_id`, `file_assets`, `ChannelAdapter`, credenciais e infraestrutura de WhatsApp ficam na **Fase 5**. Em "Funcionalidades" acima, **Conversas/Mensagens** devem ser lidas conforme esta diretriz. A aprovação do critério G7 do Gate da Fase 5 continua pendente.
- **Integração por tenant ([D-074](../00-governance/decision-register.md#d-074--integração-de-whatsapp-configurada-por-tenant-por-conta-de-canal-wa-02))**: cada tenant tem sua própria configuração de WhatsApp (sem WhatsApp, um número ou múltiplos; configurações distintas) — sem WhatsApp/credencial/número global e sem quantidade fixa por tenant. Máximo de contas, onboarding, UI, modelo comercial, BSP e armazenamento de secrets ficam para esta fase.
- **Módulo legado ([D-073](../00-governance/decision-register.md#d-073--módulo-communications-implementado-fora-da-especificação-whatsapp-outbound-e-automações))**: o `crm-backend` já contém envio outbound de templates WhatsApp e automações (módulo `communications`), fora desta especificação. Está **congelado** (sem evolução funcional, sem novas funcionalidades de WhatsApp nele); a **reconciliação** (reutilizar/migrar/refatorar/substituir) ocorre na **F5.0**. O Gate (G1–G10) continua fechado.
- **Critérios de aceite**: UC-08 executável ponta a ponta; teste de reentrega de webhook não duplica mensagem (BR-20); falha de envio visível ao usuário após esgotar retries (BR-21); fallback de polling testado com WebSocket desligado.
- **Riscos**: bloqueio de número por uso de provedor não oficial — mitigado pela decisão de usar API oficial/BSP como canal primário do produto; dependência de provedor externo — mitigada pela camada de abstração `ChannelAdapter` (ver [../03-architecture/architecture.md](../03-architecture/architecture.md)).

## FASE 6 — Omnichannel
- **Significado funcional (D-070)**: WhatsApp + futuros canais em uma caixa de entrada unificada.
- **Objetivo**: múltiplos canais de conversa no mesmo histórico único do cliente.
- **Funcionalidades**: abstração de canal (RF-22) aplicada a novos canais além do WhatsApp (por exemplo e-mail/SMS, quando decididos — D-040), caixa de entrada unificada.
- **Dependências**: Fase 5.
- **Critérios de aceite**: a definir quando os canais adicionais forem escolhidos; um novo canal se integra pela abstração de canal sem acoplar o CRM a um provedor específico (RF-22).
- **Riscos**: acoplamento a provedor específico — mitigado pela abstração de canal.

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
- **Funcionalidades candidatas**: sugestão de próxima ação em oportunidade, resumo automático de atendimento, transcrição de áudio/conversa (chamada apenas se telefonia voltar ao escopo — D-070). Escopo exato: [D-048](../00-governance/decision-register.md#d-048--escopo-de-ia-como-funcionalidade-do-produto) (`ADIADO`), a detalhar em documento próprio quando esta fase se aproximar.
- **Dependências**: volume de dado histórico suficiente (interações, chamadas) das fases anteriores.
- **Critérios de aceite**: a definir na especificação da fase.
- **Riscos**: custo de inferência, qualidade/alucinação, privacidade de dado de cliente usado em prompt — a tratar com o mesmo rigor de segurança do restante do sistema.
