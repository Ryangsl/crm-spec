# Project Context

> Checkpoint operacional de continuidade do projeto. **Não substitui** o [Decision Register](docs/00-governance/decision-register.md), o [Roadmap](docs/10-roadmap/roadmap.md), o [Requirements](docs/01-product/requirements.md) ou qualquer outro documento oficial do `crm-spec` — em caso de conflito, os documentos oficiais prevalecem. Serve apenas para que uma nova sessão/agente entenda rapidamente onde o projeto parou, sem reauditar tudo do zero.

## Última atualização
- **Data**: 05/10/2026
- **Commit/referência**: crm-spec — alterações **locais não commitadas** (base: `90341cc` `docs(whatsapp): define tenant channel architecture`); código inalterado: `ec63390` crm-backend · `dacf723` crm-frontend
- **Repositório**: crm-spec
- **Ação realizada**: **F4.0 da Fase 4** — fechamento das decisões de produto `VN-01`–`VN-05` e das diretrizes `A1`–`A3` e atualização da documentação oficial; documentação apenas, sem código, migration, schema, endpoint, componente ou dependência. **Executado; aguarda aprovação do responsável pelo produto.**

## Estado atual

**Fase 3 — CRM Comercial: CONCLUÍDA.** Os incrementos 3.1 a 3.6 estão concluídos e com commits fechados nos três repositórios (`crm-backend`, `crm-frontend`, `crm-spec`): Fundação Frontend Auth/RBAC, Customers/Contacts, Leads com round-robin, Pipelines, Opportunities e agora Follow-up (Notes/Tasks/Appointments). Em 2026-09-21 houve um ajuste de escopo de produto (D-070/D-071) que redefiniu o significado funcional das Fases 3–6 (CRM Comercial + Atendimento/Conversas + WhatsApp + futuro Omnichannel, sem Call Center telefônico) — ajuste documental, sem alterar código nem decisões já fechadas (D-031 a D-069). A Fase 3 está concluída; a Fase 4 (Atendimento/Conversas) ainda não foi iniciada. Em 2026-09-29 as regras de negócio de disponibilidade (D-071) foram consolidadas — D-071 deixa de bloquear o conceito básico de disponibilidade; sua implementação técnica será planejada na Fase 4. Em 2026-09-30 foi feito o discovery do WhatsApp ([D-072](docs/00-governance/decision-register.md#d-072--whatsapp-é-uma-frente-própria-fase-5-núcleo-de-conversas-agnóstico-ao-canal-fase-4)): frente própria da Fase 5, Fase 4 agnóstica ao canal, **implementação do WhatsApp bloqueada por Gate**. O discovery encontrou um módulo `communications` já implementado no backend fora da especificação ([D-073](docs/00-governance/decision-register.md#d-073--módulo-communications-implementado-fora-da-especificação-whatsapp-outbound-e-automações)), hoje **congelado**; a integração de WhatsApp é por tenant/conta de canal ([D-074](docs/00-governance/decision-register.md#d-074--integração-de-whatsapp-configurada-por-tenant-por-conta-de-canal-wa-02)). Em 2026-09-30 foi feito também o **discovery técnico da Fase 4** (`phase-4-plan.md`): a fase segue **não iniciada**. Em **2026-10-05** o **F4.0** (fechamento de decisões) foi **executado**: novo consultor inicia `INDISPONÍVEL`; tenant sem disponibilidade mantém o comportamento da Fase 3; indisponibilidade não retira a carteira; **Lead sem proprietário é estado legítimo** ([D-075](docs/00-governance/decision-register.md#d-075--lead-sem-proprietário-é-um-estado-legítimo-do-negócio)); diretrizes A1–A3 aprovadas ([D-076](docs/00-governance/decision-register.md#d-076--fronteira-f4f5-diretrizes-de-planejamento-da-fase-4-aprovadas-a1a3)). O F4.0 aguarda aprovação; **nenhum incremento F4.1+ foi iniciado**.

## Última ação realizada

- **O que foi feito**: **F4.0** — incorporação das decisões de produto abaixo ao planejamento ([phase-4-plan.md](docs/10-roadmap/phase-4-plan.md)) e à documentação oficial. Sem novo discovery; nada implementado.
  - **`VN-01`** (`DECIDIDO`): novo consultor inicia `INDISPONÍVEL`; precisa se colocar `DISPONÍVEL` manualmente; **sem transição automática por login/logout** na primeira implementação.
  - **`VN-02`** (`DECIDIDO`): tenant sem disponibilidade mantém o comportamento atual da Fase 3; o estado não é obrigatório.
  - **`VN-03`** (`DECIDIDO`): ficar `INDISPONÍVEL` **não remove** a carteira nem a redistribui; a disponibilidade controla a elegibilidade para **novos** Leads.
  - **`VN-04`** (`DECIDIDO`, [D-075](docs/00-governance/decision-register.md#d-075--lead-sem-proprietário-é-um-estado-legítimo-do-negócio)): **Lead sem proprietário é estado legítimo do negócio** — não é erro nem exceção; `owner_id` continua anulável; distribuição não é obrigatória na criação; fontes além de WhatsApp (cadastro manual, importação, listas do tenant); sem limite de 300 nem regra especial. Política de atribuição posterior: **pendente** (`VN-16`).
  - **`VN-05`** (`DECIDIDO`): consultor altera o próprio estado exceto `TREINAMENTO`; Gestor/Admin colocam e retiram de `TREINAMENTO`; Sistema só futuramente, sem regras automáticas.
  - **`A1`–`A3`** (aprovadas como **diretriz de planejamento**, [D-076](docs/00-governance/decision-register.md#d-076--fronteira-f4f5-diretrizes-de-planejamento-da-fase-4-aprovadas-a1a3)): `Conversation` pode ficar no F4.6 (agnóstico a canal) e, se as regras não estiverem fechadas, ser deslocado para o F5.0; nada específico de canal na F4 (`channel_account_id`, `file_assets`, `ChannelAdapter`, credenciais, infraestrutura de WhatsApp); `Conversation` com `customer_id`/`lead_id`/`opportunity_id` dedicados.
  - **Lacunas técnicas documentadas (não alteradas)**: criar/importar Leads sem `owner_id` **sempre** aciona o round-robin (não há modo explícito "sem proprietário" — relevante ao cenário da lista de ~300 pessoas); sem filtro "sem proprietário" na listagem; sem atribuição em lote (K8–K10 do plano). Dependem de `VN-16`.
  - **Revisão do plano**: trechos que tratavam Lead sem dono como exceção/consequência de indisponibilidade foram reescritos; UC-01 e `workflows.md §1` (que pressupunham distribuição sempre) corrigidos.
- **Repositórios/commits**:
  - crm-spec: alterações locais **não commitadas** (por instrução expressa — sem commit nem push).
  - crm-backend / crm-frontend: não alterados.
- **Arquivos/áreas afetadas**: `docs/10-roadmap/phase-4-plan.md` (§0 nova, §3–§4, §9–§10, §13, §15, §17–§21), `docs/00-governance/decision-register.md` (D-071, D-075, D-076, notas em D-069/D-072, tabela de fases, histórico), `docs/02-business/business-rules.md` (BR-14, BR-29), `docs/01-product/requirements.md` (RF-12, RF-15), `docs/04-database/entities.md` e `relationships.md`, `docs/02-business/workflows.md`, `docs/01-product/use-cases.md`, `docs/10-roadmap/roadmap.md`, `docs/03-architecture/whatsapp-architecture.md` (notas de status em §3/G7), `PROJECT-CONTEXT.md`.
- **Resultado**: decisões registradas sem reabrir D-031 a D-074; Gate da Fase 5 inalterado (**fechado**); nenhum código alterado; F4.1 **não iniciado**.
- **Push**: não.

## Próxima etapa

- **Fase**: 4 — Atendimento/Conversas
- **Objetivo**: histórico unificado de interações (Lead/Cliente/Oportunidade) e disponibilidade de consultor/atendente. As regras de negócio de disponibilidade já estão fechadas (D-071); falta o **planejamento técnico** dentro da Fase 4. A regra detalhada de ociosidade de atendimento de Cliente será definida no incremento correspondente da Fase 4.
- **Repositório(s) envolvidos**: crm-backend, crm-frontend, crm-spec.
- **Planejamento**: ver [phase-4-plan.md](docs/10-roadmap/phase-4-plan.md) (incrementos F4.0–F4.8). O **F4.0 foi executado em 2026-10-05 e aguarda aprovação**; o próximo passo — **somente após essa aprovação e autorização explícita** — é o **F4.1** (configurações do tenant). Antes do F4.2 ainda devem ser resolvidos `TD-01`/`TD-08` e os resíduos `VN-17`.
- **WhatsApp**: **não** faz parte da Fase 4 — é a Fase 5, bloqueada por Gate (ver [whatsapp-architecture.md](docs/03-architecture/whatsapp-architecture.md) §10). A Fase 4 deve produzir o núcleo agnóstico que a Fase 5 consome (§4 do mesmo documento), conforme as diretrizes A1–A3 ([D-076](docs/00-governance/decision-register.md#d-076--fronteira-f4f5-diretrizes-de-planejamento-da-fase-4-aprovadas-a1a3)); o critério G7 do Gate da Fase 5 segue parcial.

## Próximas ações

00. **Aprovar o F4.0** (responsável pelo produto): revisar as decisões registradas e a coerência da documentação ([phase-4-plan.md](docs/10-roadmap/phase-4-plan.md) §0). Só depois autorizar o F4.1. Antes do F4.2: `TD-01`/`TD-08` e `VN-17`; antes de qualquer incremento que escoe/atribua Leads sem proprietário: `VN-16`.
0. **WhatsApp (independente do F4.0)**: revisar e aprovar/ajustar [whatsapp-architecture.md](docs/03-architecture/whatsapp-architecture.md) — o G7 está parcial (A1–A3 aprovadas para a F4) e os demais itens do Gate seguem abertos. WA-02 (princípio) e o congelamento do módulo `communications` ([D-073](docs/00-governance/decision-register.md#d-073--módulo-communications-implementado-fora-da-especificação-whatsapp-outbound-e-automações)) já estão decididos.
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
| D-071 (implementação) | Planejamento técnico **feito** ([phase-4-plan.md §9–§10, §13](docs/10-roadmap/phase-4-plan.md)) — `PROPOSTO`. Regras de negócio **`DECIDIDO`**, inclusive VN-01/02/03/05 (2026-10-05). Resíduos `VN-17`: usuários já existentes ao habilitar, demais estados de terceiros, duração de Treinamento, mapeamento de papéis de fábrica, quem habilita o mecanismo. Ainda dependem: `VN-07` (formato/efeito de `business_hours`, feriados, acesso fora do horário) e `VN-08` (liberação excepcional) | Distribuição por disponibilidade; acesso fora do horário | Antes do F4.2/F4.3 (parte afetada) | Regras `DECIDIDO`; plano `PROPOSTO`; `VN-17`/`VN-07`/`VN-08` `VALIDAÇÃO DE NEGÓCIO` |
| D-075 (política posterior) | `VN-16`: se a criação/importação distribui automaticamente ou mantém Leads sem proprietário; como/quando são atribuídos depois (lote, reivindicação, Gestor); filtro/indicador "sem proprietário". Lacunas técnicas K8–K10 (round-robin sempre aplicado na criação/importação; sem filtro; sem lote) | Escoamento da carteira "sem proprietário" | Antes de qualquer incremento que o implemente | Princípio `DECIDIDO`; política `VALIDAÇÃO DE NEGÓCIO` |
| D-071 (ociosidade) | Detalhes da ociosidade de atendimento de Cliente: regra de 5 minutos, eventos que reiniciam o contador, seleção do próximo consultor, prioridade, mensagens automáticas, transferência | Atendimento/conversas de Cliente (BR-28) | Incremento de atendimento de Cliente (Fase 4) | `VALIDAÇÃO DE NEGÓCIO` (princípio já `DECIDIDO`) |
| Fase 4 (plano) | Pendências `VN-06`, `VN-09`–`VN-15` e decisões técnicas `TD-01`–`TD-13` de [phase-4-plan.md §17–§18](docs/10-roadmap/phase-4-plan.md); F4.6/F4.7/F4.8 são **condicionais** a VN-12, VN-07/08 e VN-13 | Conteúdo dos incrementos F4.4–F4.8 | Antes de cada incremento | `VALIDAÇÃO DE NEGÓCIO` / `PROPOSTO` |
| D-072 (Gate WhatsApp) | Cumprir os 10 critérios do Gate — **FECHADO** (G7 parcial: diretrizes A1–A3 da F4 aprovadas, [D-076](docs/00-governance/decision-register.md#d-076--fronteira-f4f5-diretrizes-de-planejamento-da-fase-4-aprovadas-a1a3); falta aprovar a seção 3 por inteiro) ([whatsapp-architecture.md §10](docs/03-architecture/whatsapp-architecture.md#10-gate-de-entrada-para-implementação)); responder as pendências restantes `WA-01`–`WA-30` (críticas: WA-03, WA-06, WA-10, WA-14, WA-22, WA-24, WA-27) | **Bloqueia a implementação da Fase 5** (não bloqueia o início da Fase 4) | Antes da Fase 5 | Escopo `DECIDIDO`; fronteira da F4 `DECIDIDO` como planejamento (D-076), G7 `PROPOSTO`; pendências `PENDENTE` |
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
- **Fase 4 só começa a codificar após a aprovação do F4.0 (executado em 2026-10-05)** ([phase-4-plan.md](docs/10-roadmap/phase-4-plan.md)). Não implementar ociosidade, restrição por horário nem regras de conversa sem as decisões `VN-xx` registradas; não criar `channel_account_id`/`ChannelAdapter` na F4; não usar as permissões `messages:*` (pertencem ao módulo legado).
- **Lead sem proprietário é estado legítimo** ([D-075](docs/00-governance/decision-register.md#d-075--lead-sem-proprietário-é-um-estado-legítimo-do-negócio), BR-29): nunca tratá-lo como erro; não assumir proprietário obrigatório nem distribuição obrigatória na criação; não criar regra automática para eliminá-lo; não inventar a política de distribuição posterior (`VN-16`). **Indisponibilidade não retira nem redistribui a carteira** (VN-03); tenant sem disponibilidade mantém o comportamento da Fase 3 (VN-02).
- **F4 agnóstica a canal (A2/[D-076](docs/00-governance/decision-register.md#d-076--fronteira-f4f5-diretrizes-de-planejamento-da-fase-4-aprovadas-a1a3))**: não criar `channel_account_id`, `file_assets`, `ChannelAdapter`, credenciais de canal nem infraestrutura de WhatsApp na Fase 4.
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
| 2026-09-30 | crm-spec | Discovery e arquitetura do WhatsApp (D-072, D-073, D-074, `whatsapp-architecture.md`); WA-02 por tenant; módulo legado congelado | `90341cc` | Documentação apenas; nenhum código alterado; Gate F5 (G1–G10) continua fechado; push feito |
| 2026-09-30 | crm-spec | Discovery e planejamento técnico da Fase 4 (`phase-4-plan.md`) | *(não commitado)* | Documentação apenas; nenhum código alterado; Fase 4 não iniciada; decisões de negócio não fechadas |
| 2026-10-05 | crm-spec | **F4.0** — decisões VN-01–VN-05 e A1–A3 (D-071, D-075, D-076); BR-14/BR-29; RF-12/RF-15; entities/relationships/workflows/use-cases/roadmap | *(não commitado)* | Documentação apenas; nenhum código alterado; F4.0 aguarda aprovação; F4.1 não iniciado |

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
