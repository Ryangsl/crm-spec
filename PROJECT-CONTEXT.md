# Project Context

> Checkpoint operacional de continuidade do projeto. **Não substitui** o [Decision Register](docs/00-governance/decision-register.md), o [Roadmap](docs/10-roadmap/roadmap.md), o [Requirements](docs/01-product/requirements.md) ou qualquer outro documento oficial do `crm-spec` — em caso de conflito, os documentos oficiais prevalecem. Serve apenas para que uma nova sessão/agente entenda rapidamente onde o projeto parou, sem reauditar tudo do zero.

## Última atualização
- **Data**: 05/10/2026
- **Commit/referência**: branch `feat/f4-2-availability` (empilhada sobre `feat/f4-1-tenant-settings`, que ainda **não foi mergeada em `main`**) — crm-backend `97622f3` · crm-frontend `3c212e5` · crm-spec `e6618ab` (Gate) + commit de documentação do F4.2. **Commits locais, sem push.** F4.1 no origin: crm-backend `6733815` · crm-frontend `ad99228` · crm-spec `5eb6f65` + `cc1750c`. `main` segue em crm-backend `ec63390`, crm-frontend `dacf723`, crm-spec `90341cc`.
- **Repositório**: crm-spec
- **Ação realizada**: **F4.2 — Disponibilidade implementado** (backend + frontend + documentação), seguindo o Gate fechado e as derivações aprovadas. Commits locais; **sem push, sem merge**. F4.3 não iniciado.

## Estado atual

**Fase 3 — CRM Comercial: CONCLUÍDA.** Os incrementos 3.1 a 3.6 estão concluídos e com commits fechados nos três repositórios (`crm-backend`, `crm-frontend`, `crm-spec`): Fundação Frontend Auth/RBAC, Customers/Contacts, Leads com round-robin, Pipelines, Opportunities e agora Follow-up (Notes/Tasks/Appointments). Em 2026-09-21 houve um ajuste de escopo de produto (D-070/D-071) que redefiniu o significado funcional das Fases 3–6 (CRM Comercial + Atendimento/Conversas + WhatsApp + futuro Omnichannel, sem Call Center telefônico) — ajuste documental, sem alterar código nem decisões já fechadas (D-031 a D-069). A Fase 3 está concluída; a Fase 4 (Atendimento/Conversas) ainda não foi iniciada. Em 2026-09-29 as regras de negócio de disponibilidade (D-071) foram consolidadas — D-071 deixa de bloquear o conceito básico de disponibilidade; sua implementação técnica será planejada na Fase 4. Em 2026-09-30 foi feito o discovery do WhatsApp ([D-072](docs/00-governance/decision-register.md#d-072--whatsapp-é-uma-frente-própria-fase-5-núcleo-de-conversas-agnóstico-ao-canal-fase-4)): frente própria da Fase 5, Fase 4 agnóstica ao canal, **implementação do WhatsApp bloqueada por Gate**. O discovery encontrou um módulo `communications` já implementado no backend fora da especificação ([D-073](docs/00-governance/decision-register.md#d-073--módulo-communications-implementado-fora-da-especificação-whatsapp-outbound-e-automações)), hoje **congelado**; a integração de WhatsApp é por tenant/conta de canal ([D-074](docs/00-governance/decision-register.md#d-074--integração-de-whatsapp-configurada-por-tenant-por-conta-de-canal-wa-02)). Em 2026-09-30 foi feito também o **discovery técnico da Fase 4** (`phase-4-plan.md`): a fase segue **não iniciada**. Em **2026-10-05** o **F4.0** (fechamento de decisões) foi **executado**: novo consultor inicia `INDISPONÍVEL`; tenant sem disponibilidade mantém o comportamento da Fase 3; indisponibilidade não retira a carteira; **Lead sem proprietário é estado legítimo** ([D-075](docs/00-governance/decision-register.md#d-075--lead-sem-proprietário-é-um-estado-legítimo-do-negócio)); diretrizes A1–A3 aprovadas ([D-076](docs/00-governance/decision-register.md#d-076--fronteira-f4f5-diretrizes-de-planejamento-da-fase-4-aprovadas-a1a3)). O F4.0 foi concluído e aprovado. Em **2026-10-05** o **F4.1** (configurações do tenant) foi implementado e **enviado ao origin** (`feat/f4-1-tenant-settings`, três repositórios), aguardando aprovação/merge. Também em 2026-10-05 o **Gate de entrada do F4.2** foi fechado ([D-071](docs/00-governance/decision-register.md#d-071--disponibilidade-de-consultoratendente-para-distribuição-automática), [D-077](docs/00-governance/decision-register.md#d-077--disponibilidade-modelo-de-dados-e-permissões-td-01-td-08)): em seguida o **F4.2 (disponibilidade) foi implementado** na branch `feat/f4-2-availability` (três repositórios, commits locais, **sem push**), aguardando revisão; nenhum incremento F4.3+ iniciado.

## Última ação realizada

- **O que foi feito**: **F4.2 — Disponibilidade** (escopo exato de [phase-4-plan.md](docs/10-roadmap/phase-4-plan.md) §15/§0.6 e [D-077](docs/00-governance/decision-register.md#d-077--disponibilidade-modelo-de-dados-e-permissões-td-01-td-08)), sem antecipar F4.3+. A branch `feat/f4-2-availability` foi criada **a partir da branch aprovada do F4.1** (a `main` ainda não tem o F4.1, de que o F4.2 depende).
  - **Backend** (`crm-backend`, `97622f3`): migration aditiva `20261005120000_f4_2_availability` (enums + `user_availability` + `availability_log`); módulo `availability` com regras puras (`availability-rules.ts`), repository, service e controllers; `GET/PUT /v1/availability/me` (também devolve `enabled`), `GET /v1/availability`, `PUT /v1/users/{id}/availability`, `GET /v1/users/{id}/availability/history` (cursor). Estado atual + histórico + auditoria `availability.changed` em **uma transação**, **serializada por usuário** (`SELECT … FOR NO KEY UPDATE` em `users`). Sem registro = `INDISPONÍVEL`; estado igual não grava. Próprio estado: livre entre Disponível/Indisponível/Pausa/Almoço, **nunca** entra/sai de Treinamento (403 `AVAILABILITY_TRAINING_LOCKED`), autorizado por `availability:update` **ou** `availability:manage`. Terceiros (`manage`, Admin/Gerente): **só** colocam em Treinamento ou retiram (sempre → `INDISPONÍVEL`); o próprio usuário não é alvo (422). Flag desabilitada: escritas 409 `AVAILABILITY_DISABLED`, leituras seguem, estados preservados. Seed: `manage` → admin/gerente; `read` → admin/gerente/supervisor/diretor; `update` → vendedor/backoffice (admin recebe todas; `operador` e `leitura` nenhuma — verificado no banco de teste).
  - **Frontend** (`crm-frontend`, `3c212e5`): seletor no `AppShell` (4 estados; Treinamento travado e somente leitura; polling 30 s; oculto sem permissão ou com a flag desabilitada), item "Equipe" (só `availability:read`, só com a flag habilitada) e `/team/availability` (lista, filtro por estado, paginação, colocar/retirar de Treinamento só com `manage`, nunca o próprio usuário).
  - **Spec** (crm-spec): derivações do D-077 registradas como **aprovadas**; `phase-4-plan.md` (F4.2 com fatos e testes), `decision-register.md`, `roadmap.md`, `openapi.yaml` (rotas marcadas como implementadas), `workflows.md` e este arquivo.
- **Confirmações do responsável pelo produto incorporadas**: `manage` concede Admin/Gerente alterarem o próprio estado e gerirem terceiros (sem `availability:update` ao Gerente); retirada de Treinamento → `INDISPONÍVEL`; `GET /availability/me` devolve `enabled`; `personas.md` e o Supervisor **não** foram alterados; códigos de erro conforme as sugestões; terceiros só Treinamento e nunca o próprio usuário; `source` ∈ {`user`,`manager`}, sem `system`.
- **Testes automatizados adicionados**: backend — 56 unit + 22 e2e; frontend — 23. **Nenhum teste existente foi alterado.** Nenhum teste manual executado.
- **Resultado (executado de verdade)**: backend — lint ✅, `tsc` ✅, build ✅, unit **112/112** (eram 56), integração **2/2**, e2e **175/175** (eram 153; auth, tenant isolation, Customers/Leads/Opportunities, Follow-up, round-robin e F4.1 inalterados e passando). Frontend — lint ✅, type-check/build ✅, **165/165** testes (eram 142).
- **Bug de teste/commit corrigidos no caminho**: mensagem do commit do backend citava 77 unit (o correto é 56) — corrigida antes de qualquer push (commit local).
- **Não implementado de propósito**: aplicação da disponibilidade ao Round Robin (F4.3), `VN-16`, `VN-07`/`VN-08`, P1, ator Sistema, `availability:training`/`availability:configure`, `operador` em `availability:update`, duração/`ends_at`/worker de Treinamento, escopo por equipe/filial, redistribuição de Leads, conversas, notificações, WhatsApp, UI para habilitar a flag (continua só pela API `PUT /v1/tenant-settings/availability`).
- **Pendente operacional (não executado)**: tenants **já existentes** precisam rodar o seed idempotente (ou passo manual — D-059) para receber `availability:*` nos papéis de fábrica; aplicar a migration (`prisma migrate deploy`) em cada ambiente.
- **Push**: **não**. **Merge**: não.

## Próxima etapa

- **Fase**: 4 — Atendimento/Conversas
- **Objetivo**: histórico unificado de interações (Lead/Cliente/Oportunidade) e disponibilidade de consultor/atendente. As regras de negócio de disponibilidade já estão fechadas (D-071); falta o **planejamento técnico** dentro da Fase 4. A regra detalhada de ociosidade de atendimento de Cliente será definida no incremento correspondente da Fase 4.
- **Repositório(s) envolvidos**: crm-backend, crm-frontend, crm-spec.
- **Planejamento**: ver [phase-4-plan.md](docs/10-roadmap/phase-4-plan.md) (incrementos F4.0–F4.8). **F4.0 e F4.1 concluídos**, **F4.2 implementado em branch local (sem push), aguardando revisão**. O próximo passo — **somente com autorização explícita** — é o **F4.3** (distribuição v2: ativo + Disponível + permissão, só com a flag habilitada; carteira intocada). `VN-16` (política posterior de Leads sem proprietário) e `VN-07` (efeito de `business_hours` na distribuição) precisam ser tratados conforme o escopo do F4.3.
- **WhatsApp**: **não** faz parte da Fase 4 — é a Fase 5, bloqueada por Gate (ver [whatsapp-architecture.md](docs/03-architecture/whatsapp-architecture.md) §10). A Fase 4 deve produzir o núcleo agnóstico que a Fase 5 consome (§4 do mesmo documento), conforme as diretrizes A1–A3 ([D-076](docs/00-governance/decision-register.md#d-076--fronteira-f4f5-diretrizes-de-planejamento-da-fase-4-aprovadas-a1a3)); o critério G7 do Gate da Fase 5 segue parcial.

## Próximas ações

00. **Revisar o F4.2** (branch `feat/f4-2-availability`, três repositórios, commits locais) e decidir a integração: autorizar o **push** e como mergear (F4.1 e F4.2 estão empilhados; `main` ainda não tem o F4.1). Aplicar a migration e rodar o seed nos ambientes reais (tenants existentes). Só depois autorizar o F4.3.
0. **WhatsApp (independente do F4.0)**: revisar e aprovar/ajustar [whatsapp-architecture.md](docs/03-architecture/whatsapp-architecture.md) — o G7 está parcial (A1–A3 aprovadas para a F4) e os demais itens do Gate seguem abertos. WA-02 (princípio) e o congelamento do módulo `communications` ([D-073](docs/00-governance/decision-register.md#d-073--módulo-communications-implementado-fora-da-especificação-whatsapp-outbound-e-automações)) já estão decididos.
1. Executar o F4.3 somente com autorização explícita: aplicar a disponibilidade ao Round Robin (D-068) apenas com a flag habilitada, ler a elegibilidade dentro da transação após o lock (K5), cursor "primeiro id maior" (TD-11), carteira existente intocada; `VN-16` e o efeito de `business_hours` (VN-07) pendentes.
2. Aplicar a disponibilidade ao Round Robin só no F4.3 (evolução da F3.4, D-068): ativo + **Disponível** + permissão, apenas com a flag habilitada; carteira existente intocada.
3. Aplicar a disponibilidade ao Round Robin (evolução da F3.4, D-068): ativo + **Disponível** + permissão.
4. Definir o desenho do módulo de Interações (histórico unificado) sem antecipar WhatsApp (Fase 5).
5. No incremento de atendimento/conversas de Cliente: fechar os detalhes da ociosidade (BR-28) e as pendências de D-070 (BR-15/16/18, filas, terminologia de papéis).
6. Manter os mesmos padrões consolidados (tenant isolation, RBAC, soft delete, audit, OpenAPI, testes).
7. Ao concluir cada incremento da Fase 4, atualizar este arquivo (`PROJECT-CONTEXT.md`) com data, commits, resultado e próxima etapa.

## Decisões pendentes

| ID | Decisão necessária | Impacto | Fase limite | Status |
|----|---------------------|---------|--------------|--------|
| D-071 / D-077 (disponibilidade) | **Implementado no F4.2** (derivações aprovadas). Continuam dependendo de outras decisões: `VN-07` (formato/efeito de `business_hours`, feriados, acesso fora do horário) e `VN-08` (liberação excepcional) — não bloquearam o F4.2 | Distribuição por disponibilidade (F4.3); acesso fora do horário | F4.3 / F4.7 | Regras `DECIDIDO`; `VN-07`/`VN-08` `VALIDAÇÃO DE NEGÓCIO` |
| F4.2 (operacional) | Aplicar a migration `20261005120000_f4_2_availability` e rodar o seed idempotente (ou passo manual de dados, D-059) nos tenants **já existentes** para os papéis de fábrica receberem `availability:*` | Sem isso, usuários de tenants existentes não veem seletor/painel | Antes de habilitar a disponibilidade num tenant real | Pendente (não executado) |
| D-075 (política posterior) | `VN-16`: se a criação/importação distribui automaticamente ou mantém Leads sem proprietário; como/quando são atribuídos depois (lote, reivindicação, Gestor); filtro/indicador "sem proprietário". Lacunas técnicas K8–K10 (round-robin sempre aplicado na criação/importação; sem filtro; sem lote) | Escoamento da carteira "sem proprietário" | Antes de qualquer incremento que o implemente | Princípio `DECIDIDO`; política `VALIDAÇÃO DE NEGÓCIO` |
| D-071 (ociosidade) | Detalhes da ociosidade de atendimento de Cliente: regra de 5 minutos, eventos que reiniciam o contador, seleção do próximo consultor, prioridade, mensagens automáticas, transferência | Atendimento/conversas de Cliente (BR-28) | Incremento de atendimento de Cliente (Fase 4) | `VALIDAÇÃO DE NEGÓCIO` (princípio já `DECIDIDO`) |
| Fase 4 (plano) | Pendências `VN-06`, `VN-09`–`VN-15` e decisões técnicas ainda abertas (`TD-02`, `TD-05`–`TD-07`, `TD-09`, `TD-11`, `TD-12` e a parte `messages:*` do `TD-08`) de [phase-4-plan.md §17–§18](docs/10-roadmap/phase-4-plan.md); F4.6/F4.7/F4.8 são **condicionais** a VN-12, VN-07/08 e VN-13 | Conteúdo dos incrementos F4.4–F4.8 | Antes de cada incremento | `VALIDAÇÃO DE NEGÓCIO` / `PROPOSTO` |
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
- **Fase 4: F4.0 e F4.1 concluídos (F4.1 no origin); F4.2 implementado em branch local (sem push); nenhum código de F4.3+ antes da autorização explícita**
- **Disponibilidade (Gate do F4.2, [D-077](docs/00-governance/decision-register.md#d-077--disponibilidade-modelo-de-dados-e-permissões-td-01-td-08))**: sem registro = `INDISPONÍVEL`; sem transição automática (login/logout/Sistema) e sem transição automática para `DISPONÍVEL`; Admin/Gerente só colocam/retiram terceiros de `TREINAMENTO` (nunca alteram arbitrariamente os demais estados de terceiros); `TREINAMENTO` sem duração, worker, timer ou `ends_at`; sem escopo por equipe/filial; **não** criar `availability:training` nem `availability:configure`; **não** incluir `operador` em `availability:update`; flag desabilitada = seletor oculto, escritas bloqueadas, distribuição ignora, estados preservados e retomados (sem reset); P1 não é necessário.
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
| 2026-10-05 | crm-spec | **F4.0** — decisões VN-01–VN-05 e A1–A3 (D-071, D-075, D-076); BR-14/BR-29; RF-12/RF-15; entities/relationships/workflows/use-cases/roadmap | `5eb6f65` (branch `feat/f4-1-tenant-settings`, no origin) | Documentação apenas; F4.0 aprovado |
| 2026-10-05 | crm-backend | **F4.1** — API de configurações do tenant (`business_hours`, flag de disponibilidade) | `6733815` (branch `feat/f4-1-tenant-settings`, no origin) | lint/tsc/build ✅; unit 56, integração 2, e2e 153 passando |
| 2026-10-05 | crm-frontend | **F4.1** — tela `/settings/business-hours` + item de menu por permissão | `ad99228` (branch `feat/f4-1-tenant-settings`, no origin) | lint/type-check/build ✅; 142 testes passando |
| 2026-10-05 | crm-spec | **F4.1** — OpenAPI, plano, roadmap, entities, CLAUDE.md, PROJECT-CONTEXT | `cc1750c` (branch `feat/f4-1-tenant-settings`, no origin) | Documentação apenas |
| 2026-10-05 | crm-spec | **Gate de entrada do F4.2** — TD-01/TD-08 (D-077) e VN-17.1–17.5 + flag desabilitada (D-071); plano, BR-14, RF-15, entities/relationships, workflows, UC-11, OpenAPI (rascunho) | `e6618ab` (branch `feat/f4-2-availability`, local) | Documentação apenas; nenhum código alterado |
| 2026-10-05 | crm-backend | **F4.2** — disponibilidade: migration, módulo `availability`, seed de permissões | `97622f3` (branch `feat/f4-2-availability`, local, sem push) | lint/tsc/build ✅; unit 112, integração 2, e2e 175 passando |
| 2026-10-05 | crm-frontend | **F4.2** — seletor, item "Equipe" e `/team/availability` | `3c212e5` (branch `feat/f4-2-availability`, local, sem push) | lint/type-check/build ✅; 165 testes passando |
| 2026-10-05 | crm-spec | **F4.2** — derivações aprovadas, plano, registro, roadmap, OpenAPI, workflows, PROJECT-CONTEXT | commit de documentação do F4.2 (branch, local) | Documentação apenas |

## Roadmap atual

- **Fase atual**: Fase 3 — CRM Comercial — **concluída** (incrementos 3.1–3.6). Fase 4: F4.0 e F4.1 concluídos; **F4.2 implementado em branch local (sem push), aguardando revisão**
- **Próxima fase**: Fase 4 — Atendimento/Conversas — **em andamento** (próximo incremento: F4.3, distribuição v2 — não iniciado)
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
