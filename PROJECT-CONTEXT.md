# Project Context

> Checkpoint operacional de continuidade do projeto. **Não substitui** o [Decision Register](docs/00-governance/decision-register.md), o [Roadmap](docs/10-roadmap/roadmap.md), o [Requirements](docs/01-product/requirements.md) ou qualquer outro documento oficial do `crm-spec` — em caso de conflito, os documentos oficiais prevalecem. Serve apenas para que uma nova sessão/agente entenda rapidamente onde o projeto parou, sem reauditar tudo do zero.

## Última atualização
- **Data**: 30/09/2026
- **Commit/referência**: crm-spec — `docs(whatsapp): define tenant channel architecture` (base: `0604554`); código inalterado: `ec63390` crm-backend · `dacf723` crm-frontend
- **Repositório**: crm-spec
- **Ação realizada**: discovery e arquitetura do WhatsApp (Fase 5), com ajuste final de WA-02 (integração por tenant, [D-074](docs/00-governance/decision-register.md#d-074--integração-de-whatsapp-configurada-por-tenant-por-conta-de-canal-wa-02)) e congelamento do módulo legado (D-073) — documentação apenas; nenhum código, migration, endpoint, componente, dependência ou integração.

## Estado atual

**Fase 3 — CRM Comercial: CONCLUÍDA.** Os incrementos 3.1 a 3.6 estão concluídos e com commits fechados nos três repositórios (`crm-backend`, `crm-frontend`, `crm-spec`): Fundação Frontend Auth/RBAC, Customers/Contacts, Leads com round-robin, Pipelines, Opportunities e agora Follow-up (Notes/Tasks/Appointments). Em 2026-09-21 houve um ajuste de escopo de produto (D-070/D-071) que redefiniu o significado funcional das Fases 3–6 (CRM Comercial + Atendimento/Conversas + WhatsApp + futuro Omnichannel, sem Call Center telefônico) — ajuste documental, sem alterar código nem decisões já fechadas (D-031 a D-069). A Fase 3 está concluída; a Fase 4 (Atendimento/Conversas) ainda não foi iniciada. Em 2026-09-29 as regras de negócio de disponibilidade (D-071) foram consolidadas — D-071 deixa de bloquear o conceito básico de disponibilidade; sua implementação técnica será planejada na Fase 4. Em 2026-09-30 foi feito o discovery do WhatsApp ([D-072](docs/00-governance/decision-register.md#d-072--whatsapp-é-uma-frente-própria-fase-5-núcleo-de-conversas-agnóstico-ao-canal-fase-4)): frente própria da Fase 5, Fase 4 agnóstica ao canal, **implementação do WhatsApp bloqueada por Gate**. O discovery encontrou um módulo `communications` já implementado no backend fora da especificação ([D-073](docs/00-governance/decision-register.md#d-073--módulo-communications-implementado-fora-da-especificação-whatsapp-outbound-e-automações)).

## Última ação realizada

- **O que foi feito**: discovery e planejamento técnico/arquitetural da integração com o WhatsApp — sem implementar nada. Levantamento do `crm-spec` e do estado **real** de `crm-backend` e `crm-frontend`; definição da fronteira F4/F5/F6; catálogo de decisões; arquitetura de referência; incrementos propostos; Gate de entrada. Detalhe em [whatsapp-architecture.md](docs/03-architecture/whatsapp-architecture.md).
  - **Fronteira (proposta, aguarda aprovação)**: F4 = núcleo `Conversation`/`Message`, ciclo de vida, disponibilidade, distribuição, `business_hours` — agnóstico ao canal; F5 = WhatsApp (conta do canal, webhook, envio/recebimento, templates, mídia, tempo real); F6 = novos canais sobre o mesmo núcleo.
  - **Achado principal**: o `crm-backend` já tem o módulo `communications` (commit `3ed66f2`) com envio outbound de templates WhatsApp via Meta Cloud API + automações (`birthday`/`inactivity`/`campaign`), tabelas `whatsapp_messages`/`automation_rules`, `/v1/automations` e `/v1/whatsapp/messages` — **fora da spec** (contraria D-015/D-011 `ADIADO`/Fase 8). Credenciais globais por env (um número para todos os tenants), sem timeout no provedor, sem inbound/webhook, sem opt-in, envio sem auditoria. Registrado como [D-073](docs/00-governance/decision-register.md#d-073--módulo-communications-implementado-fora-da-especificação-whatsapp-outbound-e-automações): **congelado** (sem evolução funcional, sem apagar/refatorar agora, sem novas funcionalidades de WhatsApp nele); **reconciliação na F5.0** (reutilizar/migrar/refatorar/substituir).
  - **Pendências**: 30 itens `WA-01`–`WA-30` (nada inventado); **WA-02 resolvido no princípio** ([D-074](docs/00-governance/decision-register.md#d-074--integração-de-whatsapp-configurada-por-tenant-por-conta-de-canal-wa-02)): **cada tenant possui sua própria configuração de integração de WhatsApp, podendo variar conforme o negócio** — tenant sem WhatsApp, com um número ou com múltiplas contas; sem WhatsApp/credencial/número global e sem quantidade fixa por tenant; `ChannelAccount` 0..N por tenant (conceitual). Ficam para a F5: máximo de contas, onboarding, UI, modelo comercial, BSP e armazenamento de secrets.
  - **Gate**: 10 critérios (G1–G10) — **continua FECHADO**; G9 (módulo legado) está parcial (congelamento decidido; reconciliação na F5.0); os demais não atendidos.
  - Corrigidas referências "Fase 6" para WhatsApp em `integrations.md`, `workflows.md` e `use-cases.md` (a fase é a 5).
- **Repositórios/commits**:
  - crm-spec: `docs(whatsapp): define tenant channel architecture`.
  - crm-backend / crm-frontend: não alterados.
- **Arquivos/áreas afetadas**: novo `docs/03-architecture/whatsapp-architecture.md`; `docs/00-governance/decision-register.md` (D-072, D-073, tabela de fases, histórico); `docs/10-roadmap/roadmap.md` (Fase 5: gate, fronteira proposta, divergência); `docs/03-architecture/integrations.md`; `docs/02-business/workflows.md`; `docs/01-product/use-cases.md`; `docs/04-database/entities.md` (nota); `PROJECT-CONTEXT.md`.
- **Resultado**: planejamento documentado; nenhuma decisão anterior reaberta; D-071 preservada; nenhum código alterado.
- **Push**: sim, `origin/main` (crm-spec).

## Próxima etapa

- **Fase**: 4 — Atendimento/Conversas
- **Objetivo**: histórico unificado de interações (Lead/Cliente/Oportunidade) e disponibilidade de consultor/atendente. As regras de negócio de disponibilidade já estão fechadas (D-071); falta o **planejamento técnico** dentro da Fase 4. A regra detalhada de ociosidade de atendimento de Cliente será definida no incremento correspondente da Fase 4.
- **Repositório(s) envolvidos**: crm-backend, crm-frontend, crm-spec.
- **WhatsApp**: **não** faz parte da Fase 4 — é a Fase 5, bloqueada por Gate (ver [whatsapp-architecture.md](docs/03-architecture/whatsapp-architecture.md) §10). A Fase 4 deve produzir o núcleo agnóstico que a Fase 5 consome (§4 do mesmo documento), sujeito à aprovação da fronteira.

## Próximas ações

0. **Antes de tudo (WhatsApp)**: revisar e aprovar/ajustar [whatsapp-architecture.md](docs/03-architecture/whatsapp-architecture.md) — em especial a fronteira F4/F5 (G7) e os demais itens do Gate. WA-02 (princípio) e o congelamento do módulo `communications` ([D-073](docs/00-governance/decision-register.md#d-073--módulo-communications-implementado-fora-da-especificação-whatsapp-outbound-e-automações)) já estão decididos.
1. Iniciar a Fase 4 somente com autorização explícita; o primeiro passo é o planejamento técnico (não iniciado), agora considerando o que a F5 vai consumir (núcleo `Conversation`/`Message` agnóstico, distribuição, `business_hours`, Interações/linha do tempo, Notificações).
2. No planejamento técnico da disponibilidade: representação do estado atual vs. histórico (reaproveitando o conceito `agent_status_log`/RF-15, cujo enum em `entities.md` precisa ser revisto para os cinco estados), nomenclatura neutra, relação com login/logout, fallback para tenants sem disponibilidade e tratamento de leads já atribuídos (lacunas remanescentes de D-071).
3. Aplicar a disponibilidade ao Round Robin (evolução da F3.4, D-068): ativo + **Disponível** + permissão.
4. Definir o desenho do módulo de Interações (histórico unificado) sem antecipar WhatsApp (Fase 5).
5. No incremento de atendimento/conversas de Cliente: fechar os detalhes da ociosidade (BR-28) e as pendências de D-070 (BR-15/16/18, filas, terminologia de papéis).
6. Manter os mesmos padrões consolidados (tenant isolation, RBAC, soft delete, audit, OpenAPI, testes).
7. Ao concluir cada incremento da Fase 4, atualizar este arquivo (`PROJECT-CONTEXT.md`) com data, commits, resultado e próxima etapa.

## Decisões pendentes

| ID | Decisão necessária | Impacto | Fase limite | Status |
|----|---------------------|---------|--------------|--------|
| D-071 (implementação) | Planejamento técnico da disponibilidade: estado atual vs. histórico, nomenclatura neutra, relação com login/logout, fallback para tenant sem disponibilidade, leads já atribuídos a quem fica indisponível, formato de `business_hours` e da liberação excepcional pelo Admin | Distribuição automática por disponibilidade; acesso fora do horário | Planejamento da Fase 4 | Regras de negócio `DECIDIDO` (2026-09-29); implementação a planejar |
| D-071 (ociosidade) | Detalhes da ociosidade de atendimento de Cliente: regra de 5 minutos, eventos que reiniciam o contador, seleção do próximo consultor, prioridade, mensagens automáticas, transferência | Atendimento/conversas de Cliente (BR-28) | Incremento de atendimento de Cliente (Fase 4) | `VALIDAÇÃO DE NEGÓCIO` (princípio já `DECIDIDO`) |
| D-072 (Gate WhatsApp) | Aprovar a fronteira F4/F5 e cumprir os 10 critérios do Gate — **FECHADO** ([whatsapp-architecture.md §10](docs/03-architecture/whatsapp-architecture.md#10-gate-de-entrada-para-implementação)); responder as pendências restantes `WA-01`–`WA-30` (críticas: WA-03, WA-06, WA-10, WA-14, WA-22, WA-24, WA-27) | **Bloqueia a implementação da Fase 5** (não bloqueia o início da Fase 4) | Antes da Fase 5 | Escopo `DECIDIDO`; fronteira `PROPOSTO`; pendências `PENDENTE` |
| D-073 (`communications`) | Reconciliação do módulo legado de WhatsApp outbound/automações com a nova arquitetura: reutilizar, migrar, refatorar ou substituir | Módulo **congelado**; risco de segurança/compliance enquanto existir sem timeout, opt-in, cota e com credenciais globais | F5.0 | Congelamento `DECIDIDO`; reconciliação `PENDENTE` |
| D-074 (detalhes) | Máximo de contas por tenant, onboarding, UI de configuração, modelo comercial, provedor/BSP, armazenamento de secrets, qual conta inicia conversa ativa | Modelo `ChannelAccount` e configuração por tenant (F5) | Fase 5 | Princípio `DECIDIDO`; detalhes `PENDENTE` |
| D-070 (pendências) | O que caracteriza uma Conversa/atendimento "finalizado"; limite de pausa e destinatário do alerta (e se Almoço/Treinamento contam); pontos de medição do SLA; se "filas" de atendimento existem já na Fase 4 ou só na Fase 5; terminologia dos papéis "Supervisor/Operador de Call Center" | BR-15, BR-16, BR-18 e nomenclatura de papéis (Fase 4/5) | Antes da fase que as implementa (Fase 4/5) | `VALIDAÇÃO DE NEGÓCIO` |

**D-071 deixou de ser decisão de negócio bloqueante** para o conceito básico de disponibilidade. As pendências acima são decididas no incremento da Fase 4 que as implementar — não impedem o início da Fase 4.

## Restrições importantes

- Não implementar telefonia, PSTN, URA, discador ou gravação de chamadas — fora de escopo do produto (D-070).
- Disponibilidade de consultor/atendente pertence à Fase 4: implementar somente após o planejamento técnico da fase, seguindo as regras de D-071. Não implementar a regra de ociosidade antes de seus detalhes serem definidos no incremento de atendimento de Cliente.
- Lead não é Cliente (BR-28): regras de atendimento de Cliente (ex.: ociosidade) não se aplicam a Lead.
- Usar a terminologia "CRM Universal"; não definir o produto como "Call Center".
- Reutilizar módulos/modelos já existentes antes de criar qualquer estrutura nova (ex.: F3.6 reaproveitou o padrão do módulo `tasks` para `notes`/`appointments`); manter o modelo polimórfico `entity_type` + `entity_id` (D-031), sem colunas de FK dedicadas por tipo de entidade.
- Manter tenant isolation, RBAC, soft delete e auditoria consistentes com os padrões já implementados em Customers/Leads/Opportunities/Notes/Tasks/Appointments.
- Não avançar automaticamente para a próxima fase (Fase 4) sem fechamento formal do incremento/fase atual.
- **Não implementar WhatsApp** (código, migration, endpoint, componente, dependência ou integração) antes do Gate de [D-072](docs/00-governance/decision-register.md#d-072--whatsapp-é-uma-frente-própria-fase-5-núcleo-de-conversas-agnóstico-ao-canal-fase-4). A Fase 4 permanece agnóstica ao canal. O módulo `communications` legado está **congelado** ([D-073](docs/00-governance/decision-register.md#d-073--módulo-communications-implementado-fora-da-especificação-whatsapp-outbound-e-automações)): sem novas funcionalidades de WhatsApp nele. A integração é por tenant/conta de canal ([D-074](docs/00-governance/decision-register.md#d-074--integração-de-whatsapp-configurada-por-tenant-por-conta-de-canal-wa-02)): nunca assumir WhatsApp, credencial ou número global.
- Não reabrir decisões já fechadas (D-031 a D-069), o ajuste de escopo D-070 nem as regras de negócio de D-071.
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
| 2026-09-27 | crm-spec | Atualização do PROJECT-CONTEXT após F3.6 | `a642465` | Checkpoint atualizado; push feito |
| 2026-09-29 | crm-spec | Consolidação das regras de disponibilidade (D-071), Lead x Cliente, ociosidade (princípio), "CRM Universal" | `0604554` | Documentação apenas; nenhum código alterado; push feito |
| 2026-09-30 | crm-spec | Discovery e arquitetura do WhatsApp (D-072, D-073, D-074, `whatsapp-architecture.md`); WA-02 por tenant; módulo legado congelado | `docs(whatsapp): define tenant channel architecture` | Documentação apenas; nenhum código alterado; Gate F5 (G1–G10) continua fechado; push feito |

## Roadmap atual

- **Fase atual**: Fase 3 — CRM Comercial — **concluída** (incrementos 3.1–3.6, incluindo Follow-up)
- **Próxima fase**: Fase 4 — Atendimento/Conversas (histórico unificado de interações, disponibilidade de consultor/atendente — regras de negócio fechadas em D-071, implementação técnica a planejar) — **não iniciada**
- **Fases posteriores (resumo)**:
  - Fase 5 — WhatsApp/Conversas (integração com provedor oficial/BSP, conversas distribuídas por disponibilidade) — **bloqueada por Gate** (D-072); incrementos propostos F5.0–F5.7 em [whatsapp-architecture.md](docs/03-architecture/whatsapp-architecture.md)
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
