# Fase 4 — Atendimento/Conversas: Discovery e Planejamento Técnico

> **Natureza deste documento**: discovery e planejamento. **Não autoriza implementação.** Nenhum código, migration, schema Prisma, endpoint, componente ou dependência é criado por ele. Tudo o que é proposta está marcado `PROPOSTO`; tudo o que depende de regra de negócio não documentada está `PENDENTE` / `VALIDAÇÃO DE NEGÓCIO` (`VN-xx`); decisões técnicas em aberto são `TD-xx`. Nada foi assumido sem base documental.
>
> **Levantamento**: 2026-09-30, sobre o `crm-spec` (HEAD `90341cc`), o `crm-backend` (HEAD `ec63390`) e o `crm-frontend` (HEAD `dacf723`) **reais**. Os arquivos citados foram lidos; onde a documentação e o código divergem, vale o código e a divergência está registrada na §3.
>
> **Base decidida (não reaberta)**: [D-070](../00-governance/decision-register.md#d-070--definição-de-produto-crm-comercial--atendimentoconversas--whatsapp-sem-call-center-telefônico) (produto), [D-071](../00-governance/decision-register.md#d-071--disponibilidade-de-consultoratendente-para-distribuição-automática) (disponibilidade), [D-072](../00-governance/decision-register.md#d-072--whatsapp-é-uma-frente-própria-fase-5-núcleo-de-conversas-agnóstico-ao-canal-fase-4) (F4 agnóstica / WhatsApp = F5), [D-073](../00-governance/decision-register.md#d-073--módulo-communications-implementado-fora-da-especificação-whatsapp-outbound-e-automações) (módulo legado congelado), [D-074](../00-governance/decision-register.md#d-074--integração-de-whatsapp-configurada-por-tenant-por-conta-de-canal-wa-02) (WhatsApp por tenant), BR-14, BR-27, BR-28. Relação com o discovery do WhatsApp: [../03-architecture/whatsapp-architecture.md](../03-architecture/whatsapp-architecture.md).
>
> **Atualização F4.0 (2026-10-05)**: as decisões de produto `VN-01` a `VN-05` e as diretrizes `A1`–`A3` foram **incorporadas** (§0) e registradas em [D-071](../00-governance/decision-register.md#d-071--disponibilidade-de-consultoratendente-para-distribuição-automática), [D-075](../00-governance/decision-register.md#d-075--lead-sem-proprietário-é-um-estado-legítimo-do-negócio) e [D-076](../00-governance/decision-register.md#d-076--fronteira-f4f5-diretrizes-de-planejamento-da-fase-4-aprovadas-a1a3). Não houve novo discovery. O plano abaixo foi **revisto** para refletir as decisões; o que continua sem decisão permanece `PENDENTE`/`VN`/`TD`. **O F4.0 está concluído. Em 2026-10-05 o Gate de entrada do F4.2 foi fechado (§0.6; [D-077](../00-governance/decision-register.md#d-077--disponibilidade-modelo-de-dados-e-permissões-td-01-td-08)) e o **F4.2 foi implementado em 2026-10-05** (branch `feat/f4-2-availability`, commits locais, sem push).**

## 0. Decisões incorporadas no F4.0 (2026-10-05)

### 0.1 `VN-01` a `VN-05` — `DECIDIDO`

| ID | Decisão | Registro |
|---|---|---|
| VN-01 | Novo consultor inicia **`INDISPONÍVEL`**; precisa alterar manualmente para `DISPONÍVEL` para participar da distribuição automática; **sem transição automática por login/logout** na primeira implementação | D-071 |
| VN-02 | Tenant que não utiliza/habilita disponibilidade **mantém o comportamento atual da Fase 3** (elegibilidade D-068); o estado de disponibilidade **não é obrigatório** para o CRM funcionar | D-071 |
| VN-03 | Ficar `INDISPONÍVEL` **não remove** os Leads já atribuídos; a carteira é mantida; a disponibilidade controla a elegibilidade para **NOVOS** Leads; **sem redistribuição automática** nem mecanismo de "retirar carteira" | D-071 |
| VN-04 | **Lead sem proprietário é um estado legítimo do negócio** (não é erro, exceção, abandono nem falha de distribuição); `owner_id` continua anulável; distribuição não é obrigatória na criação; fontes além de WhatsApp (cadastro manual, importação, listas do tenant, futuras); sem limite de 300 nem regra especial | D-075 |
| VN-05 | Consultor altera o próprio estado entre `DISPONÍVEL`, `INDISPONÍVEL`, `PAUSA`, `ALMOÇO`; **não** entra nem sai de `TREINAMENTO`; **Gestor/Admin *(= Admin e Gerente — Gate do F4.2)*** coloca e retira de `TREINAMENTO`; o **Sistema** só futuramente, quando houver regra de negócio — **nenhuma regra automática agora** | D-071 |

### 0.2 `A1`–`A3` — diretrizes de planejamento **aprovadas** ([D-076](../00-governance/decision-register.md#d-076--fronteira-f4f5-diretrizes-de-planejamento-da-fase-4-aprovadas-a1a3))

- **A1**: o núcleo de `Conversation` **pode** fazer parte do **F4.6**, agnóstico ao canal e sem dependência de WhatsApp; se as regras necessárias não estiverem fechadas quando o F4.6 chegar, o incremento **pode ser deslocado para o F5.0** (condição de planejamento, não decisão de negócio).
- **A2**: **não** implementar na F4 `channel_account_id`, `file_assets`, `ChannelAdapter`, credenciais de canal nem infraestrutura de WhatsApp — pertencem à F5; a F4 prepara o núcleo agnóstico que a F5 consome.
- **A3**: `Conversation` usa referências dedicadas `customer_id`, `lead_id`, `opportunity_id` (**sem** reutilizar o polimorfismo de D-031); uma Conversation **não** transforma Lead em Cliente.

### 0.3 Efeito de VN-04 no plano (revisão feita)

- **Revisão**: o plano foi varrido em busca de trechos que tratassem Lead sem proprietário como erro/exceção, como mera consequência de indisponibilidade, que presumissem proprietário obrigatório ou distribuição obrigatória na criação, ou indisponibilidade como perda automática da carteira. Os trechos de §9.3, §10, §13, F4.3, VN-04 e R1 foram **reescritos**; nenhum outro trecho era incompatível.
- **Arquitetura continua coerente**: `owner_id` de Lead segue anulável (nada a alterar no schema); a distribuição **não** é requisito de criação; a disponibilidade afeta apenas a elegibilidade para **novos** Leads; a carteira existente não é redistribuída; Leads de cadastro/importação podem existir sem proprietário; `Conversation` segue desacoplada de WhatsApp (A2); a F5 adiciona depois, de forma aditiva, os componentes de canal.
- **O plano não cria política** para escoar Leads sem proprietário — isso é `VN-16` (§18).

### 0.4 Lacunas técnicas decorrentes (apenas documentadas — nada foi alterado)

| # | Lacuna | Onde está | Tratamento |
|---|---|---|---|
| K8 | Criar e **importar** Leads sem `owner_id` **sempre** aciona o round-robin; não há modo explícito "sem proprietário" quando existem elegíveis. No cenário "lista de ~300 pessoas" (D-075), a importação sem `owner_id` distribuiria tudo se houver consultores elegíveis | §3.2 | Depende de `VN-16` |
| K9 | `GET /leads` filtra `owner_id` por igualdade; **não há filtro "sem proprietário"** (o frontend só rotula "Sem responsável") | §3.2 | Depende de `VN-16` |
| K10 | **Não há atribuição em lote** de Leads (o `PATCH /leads/{id}` atribui um a um) | §3.2 | Depende de `VN-16` |
| TD-13 | Momento de entrega do P1 (contexto de tenant fora de HTTP + ator Sistema): com VN-05, o Sistema **não** altera estados agora; P1 só é exigido antes do F4.8 e da F5 | §17 | **Resolvida no F4.1**: não entregue (ver F4.1) |

### 0.5 O que continua pendente (não decidido)

~~Resíduos de disponibilidade (`VN-17`)~~ (fechados no Gate do F4.2, §0.6); política de distribuição posterior de Leads sem proprietário (`VN-16`, F4.3); BR-16 (`VN-06`); `business_hours` — formato, feriados, regra de acesso fora do horário e liberação excepcional (`VN-07`/`VN-08`); interações (`VN-09`); visibilidade (`VN-10`); notificações (`VN-11`); conversa — contato desconhecido, encerramento, disposições, filas, SLA (`VN-12`); **ociosidade** — regra de 5 minutos, reinício do contador, próximo consultor, prioridade, mensagens automáticas (`VN-13`); Lead convertido (`VN-14`); papéis (`VN-15`); e todas as decisões técnicas `TD-xx`.

### 0.6 Gate de entrada do F4.2 — fechado em 2026-10-05

Decisões de produto e técnicas aprovadas pelo responsável pelo produto (registro: [D-071](../00-governance/decision-register.md#d-071--disponibilidade-de-consultoratendente-para-distribuição-automática) e [D-077](../00-governance/decision-register.md#d-077--disponibilidade-modelo-de-dados-e-permissões-td-01-td-08)):

| Item | Decisão |
|---|---|
| TD-01 | `user_availability` (estado atual, 1:1 por usuário/tenant) + `availability_log` (histórico append-only); linha criada sob demanda; ausência de linha = `INDISPONÍVEL`; transição + histórico + auditoria na mesma transação |
| TD-08 | `availability:read`, `availability:update`, `availability:manage`; **sem** `availability:training` |
| VN-17.1 | Sem registro = `INDISPONÍVEL`; ao habilitar, existentes sem registro continuam `INDISPONÍVEIS`; sem transição automática para `DISPONÍVEL` |
| VN-17.2 | Admin e Gerente colocam/retiram terceiros de `TREINAMENTO`; **não** alteram arbitrariamente os demais estados de terceiros; usuário altera o próprio estado pelas regras já decididas; sem escopo por equipe/filial |
| VN-17.3 | `TREINAMENTO` sem duração automática; termina só por remoção manual de Admin/Gerente; registrar desde quando; sem worker/timer/`ends_at` |
| VN-17.4 | `manage`: admin, gerente · `read`: admin, gerente, supervisor, diretor · `update`: vendedor, backoffice · Admin/Gerente alteram o próprio estado · **`operador` fora** (papéis legados de Call Center pendentes) |
| VN-17.5 | Habilitar = `tenant_settings:update` (só Admin); sem `availability:configure` |
| Flag desabilitada | Seletor oculto; escritas bloqueadas pela API; distribuição ignora a disponibilidade; estados preservados e retomados ao reativar; novos usuários sem registro = `INDISPONÍVEL`; sem reset |

**Derivações técnicas (aprovadas pelo responsável pelo produto em 2026-10-05)**: (1) o próprio estado exige `availability:update` **ou** `availability:manage` (`manage` inclui o próprio estado; **não** se adiciona `update` ao Gerente); (2) a retirada de `TREINAMENTO` leva a `INDISPONÍVEL`; (3) a via de terceiros não aceita o próprio usuário como alvo e ninguém entra em `TREINAMENTO` pela via do próprio estado; (4) a via de terceiros só aceita `TREINAMENTO` (entrar) e `INDISPONÍVEL` (retirar, somente a partir de `TREINAMENTO`), para usuário ativo do mesmo tenant; (5) `GET /availability/me` devolve `enabled`; (6) com a flag desabilitada, escritas respondem 409 `AVAILABILITY_DISABLED` e leituras seguem; entrar/sair de Treinamento pelo próprio estado responde 403 `AVAILABILITY_TRAINING_LOCKED`; (7) `source` ∈ {`user`, `manager`}, sem `system`. Ver [D-077](../00-governance/decision-register.md#d-077--disponibilidade-modelo-de-dados-e-permissões-td-01-td-08).

**Continua fora do F4.2 (não bloqueia)**: `VN-16` (distribuição posterior de Leads sem proprietário — F4.3); `VN-07`/`VN-08` (`business_hours` segue separado da disponibilidade); P1 (**P1 não bloqueia o F4.2**: todo ator é um usuário autenticado; sem worker); BR-16/`VN-06`; ociosidade; conversas; notificações; WhatsApp.

## 1. Estado atual (real)

### 1.1 Backend (`crm-backend`, código lido)

| Área | Fato verificado |
|---|---|
| Módulos | `auth`, `users`, `roles`, `tenants`, `customers`, `leads`, `pipelines`, `opportunities`, `tasks`, `notes`, `appointments`, `audit`, `communications` (legado), `health`. **Não existem**: availability, interactions, notifications, conversations, messages, dispositions, queues |
| Schema | Sem nenhuma tabela de disponibilidade, interação, notificação, conversa, mensagem, disposição ou fila. `CrmEntityType` = `lead \| customer \| opportunity` |
| Round Robin | `RoundRobinService.assignOwner(tenantId, tx)`: elegíveis = `UsersService.listActiveIdsWithPermission('leads:update')` (**lido fora da `tx`**, via outra conexão) → `lockCursor` (`INSERT … ON CONFLICT DO NOTHING` + `SELECT … FOR UPDATE` em `tenant_settings`, chave `crm.lead_round_robin.cursor`) → ordena ids → próximo = índice do último + 1. Se o último escolhido saiu do conjunto, **reinicia do primeiro id** (`indexOf = -1`) |
| `business_hours` | `RoundRobinRepository.findBusinessHours` lê `crm.business_hours` e só emite `logger.warn`: **formato indefinido, não filtra**. Nenhum endpoint escreve essa chave |
| `TenantSettings` | Tabela existe (`tenantId+key` único, `value` JSON). **Sem service/controller**; só o round-robin a usa. As permissões `tenant_settings:read/update` existem no seed **sem uso** |
| Usuário | `User.status` = `active \| inactive`. **Nenhum conceito de disponibilidade ou presença**. `Team.managerId` e `Branch` existem no schema mas o RBAC é tenant-only ([D-058](../00-governance/decision-register.md#d-058--escopo-de-rbac-na-fase-2-e-na-fase-3-apenas-tenant)) |
| Sessão | Access token JWT 15 min (`{sub, tenantId}`), um refresh token **por dispositivo**; `logout` revoga um refresh token, `logoutAll` todos. `JwtAuthGuard` só valida o JWT; `PermissionsGuard` lê as permissões **do banco a cada requisição** (mudança de papel vale imediatamente) |
| Contexto | `TenantContextStorage` (AsyncLocalStorage) é preenchido **só** pelo `JwtAuthGuard`. Não há helper para executar código em um tenant fora de HTTP (worker/cron/webhook). `AuditService.record` lê `tenantId`/`userId` do contexto — **ator "Sistema" não é representável** (userId vazio violaria a FK de `audit_log.user_id` — confirmar em teste) |
| Follow-up (F3.6) | `notes`/`tasks`/`appointments`: `entity_type + entity_id` (D-031), `entityExists` validado no Service, auditoria na mesma `tx`, soft delete, paginação por offset, `RequirePermissions`. É o padrão a seguir |
| Auditoria | `audit_log(tenant, user?, action, entity_type, entity_id?, payload)`; ações hoje: `*.created/updated/deleted`, `lead.assigned/unassigned`, `opportunity.moved`, `user.deactivated`… Sem endpoint de leitura |
| Filas | BullMQ/Redis configurados (`QueueModule`); só existe a fila de exemplo e a fila legada `whatsapp` (job repetível de varredura horária) |
| `Customer.lastInteractionAt` | Só é gravado se o **cliente da API enviar** `last_interaction_at`; nenhum código o atualiza por interação |
| Permissões (seed) | `messages:create/read` **já existem** e gateiam o controller **legado** `/v1/whatsapp/messages` — colisão de nome se a F4 criar `messages` |
| Paginação | `offset.util` (recursos administrativos) e `cursor.util` (`createdAt+id`, base64url) — ambos prontos |
| Testes | unit (`jest-unit`), e2e contra Postgres real (`test/e2e/*`, inclui `tenant-isolation.e2e-spec.ts`), integração de fila. `resetDatabase` lista as tabelas manualmente (`TRUNCATE`) — **toda tabela nova precisa entrar nela** |

### 1.2 Frontend (`crm-frontend`, código lido)

| Área | Fato verificado |
|---|---|
| Stack | React 19, React Router 7, TanStack Query 5, Tailwind 4; **sem** WebSocket, **sem** `useInfiniteQuery` em uso; polling só em `useHealth` (`refetchInterval: 30s`) |
| Estrutura | `features/{auth,customers,leads,opportunities,follow-up,status}` com `types/ services/ hooks/ components/ pages/`; rotas planas em `routes/router.tsx`; `AppShell` com 6 itens de navegação |
| Padrão de embutir | `NotesSection`/`TasksSection`/`AppointmentsSection` recebem `entityType + entityId` e são montadas em `Customer/Lead/OpportunityDetailPage` — modelo direto para uma linha do tempo |
| Auth/RBAC | `useAuth().hasPermission(key)` (só UX); `AuthUser.permissions` vem de `GET /v1/users/me` (o comentário no tipo dizendo que "ainda não devolve permissions" está **desatualizado** — o backend já devolve) |
| Gaps | Sem service/telas de **usuários** (necessário para painel de gestão), sem tela de **configurações do tenant**, sem controle de status do usuário; `AppShell` ainda exibe **"CRM + Call Center"** (contradiz D-070/"CRM Universal") |

### 1.3 Spec (documentos lidos)

Conceitos documentados que **não existem no código**: `conversations`, `messages`, `message_templates`, `queues`, `queue_members`, `dispositions`, `agent_status_log`, `notifications`, `file_assets`; `GET /customers/{id}/interactions` (OpenAPI) sem implementação.

## 2. O que já existe e pode ser reaproveitado

| Reaproveitável | Uso na F4 |
|---|---|
| Padrão Controller→Service→Repository + `RequirePermissions` + `TenantContextStorage` + `AuditService(tx)` + soft delete | Todos os módulos novos |
| `TenantSettings` (tabela) | `business_hours`, flag de disponibilidade, futura regra de ociosidade — falta o **service/API** |
| `RoundRobinService` + lock de cursor | Base do motor de distribuição (§10); o lock por linha `(tenant,key)` já resolve concorrência |
| `UsersService.listActiveIdsWithPermission` | Elegibilidade (ativo + permissão) — vira a base de "ativo + Disponível + permissão" |
| Modelo polimórfico `entity_type + entity_id` (D-031) | Interações manuais; **não** para `Conversation` (§11.4) |
| `cursor.util` / `offset.util` | Timeline e mensagens (cursor); listas administrativas (offset), conforme D-007 |
| BullMQ | Somente se/quando a ociosidade exigir temporizador (§12); **não** é necessário nos incrementos iniciais |
| Seções embutidas do follow-up + `Card/Button/Alert/EmptyState/Spinner/Select/Input/Textarea` | Timeline, formulário de interação, painéis de conversa |
| `useAuth.hasPermission`, `ProtectedRoute`, `api.ts` (refresh automático) | Gate de UI e chamadas |
| Suite e2e com `tenant-isolation.e2e-spec.ts` | Modelo dos testes de isolamento dos recursos novos |

**Não reaproveitar** (existe só na documentação ou é legado): `agent_status_log` como está (enum de 4 estados, vocabulário de Call Center), `queues.channel_type=voice`, `calls`, permissões `messages:*` (legado WhatsApp), o módulo `communications`.

## 3. Gaps e contradições encontrados

### 3.1 Entre documentos

| # | Contradição / lacuna | Onde |
|---|---|---|
| C1 | Roadmap F5 lista "Conversas, Mensagens" na Fase 5; o discovery do WhatsApp propõe o núcleo na F4 (**fronteira `PROPOSTO`** — analisada na §4) | roadmap × whatsapp-architecture |
| C2 | `Interaction.type` no OpenAPI = `[call, message, note]`; `call` é telefonia (D-070). `Interaction` não tem definição de origem nem de vínculo a Lead/Oportunidade | openapi.yaml |
| C3 | `agent_status_log.status` = `available/busy/paused/offline` × D-071 = 5 estados (`Disponível, Indisponível, Pausa, Almoço, Treinamento`) | entities.md |
| C4 | `conversations.channel_type` = `whatsapp/email/sms` (sem valor neutro); só `customer_id` (sem `lead_id`, embora BR-19/BR-28 falem de Cliente **ou** Lead) | entities.md |
| C5 | BR-05 diz que a distribuição só considera consultores "dentro do horário de atendimento do tenant"; D-071/BR-27 dizem que `business_hours` "não altera o status" e "poderá restringir acesso". Falta dizer explicitamente **o que acontece com a distribuição fora do horário** | business-rules |
| C6 | `workflows.md §2–4` (atendimento/telefonia) e UC-05 a UC-07 seguem escritos para telefonia; a própria nota diz que "devem ser reescritos antes da implementação" | workflows, use-cases |
| C7 | Matriz de permissões tem linha "Atendimentos/Call Center", "Filas/Telefonia"; papéis "Supervisor/Operador de Call Center" (nomes legados, D-070 pendência 5) | personas |
| C8 | Personas dizem que vendedor/operador **não** veem registros de outros; RBAC real é **tenant-only** (D-058). Para conversas/mensagens (dados pessoais) isso vira decisão obrigatória (VN-10) | personas × D-058 |
| C9 | `crm-spec/CLAUDE.md` "Estado atual" ainda diz "FASE 3 aguarda autorização" | CLAUDE.md |
| C10 | `dispositions.queue_id` opcional e `queues` na spec, mas "existência de filas na F4" segue pendente (D-070 pendência 4) | entities × D-070 |
| C11 | UC-01 tratava lead sem dono como **exceção** com "alerta ao gerente" (anterior a D-069/D-075); `workflows.md §1` supunha distribuição sempre | use-cases, workflows — **corrigido no F4.0** (D-075/BR-29) |

### 3.2 Entre spec e código

| # | Divergência | Efeito |
|---|---|---|
| K1 | `messages:*` no seed pertence ao módulo legado WhatsApp | F4 deve usar outras chaves (§7.4) |
| K2 | `Customer.lastInteractionAt` é escrito só pelo cliente da API | Regra de "última interação" não existe de fato |
| K3 | `TenantSettings` sem service/API; `tenant_settings:*` sem uso | Necessário para `business_hours` — **resolvido no F4.1** |
| K4 | Ator "Sistema" e execução por tenant fora de HTTP **não existem** (contexto, auditoria) | Pré-requisito para transições do Sistema (Treinamento), ociosidade e F5 (webhook) |
| K5 | Round Robin lê elegibilidade **fora da `tx`** e reinicia do primeiro id quando o último atribuído não é mais elegível (favorece o menor id) | Comportamento a corrigir ao introduzir disponibilidade (§10) |
| K6 | Frontend `AppShell`: "CRM + Call Center"; comentário desatualizado em `AuthUser.permissions` | Ajuste de terminologia/documentação de código |
| K7 | `resetDatabase` (e2e) lista tabelas à mão | Toda tabela nova precisa entrar |
| K8 | `LeadsService.create` e `importRows` (que chama `create`) **sempre** acionam o round-robin sem `owner_id` | Sem modo explícito de criar/importar sem proprietário quando há elegíveis (cenário D-075) — `VN-16` |
| K9 | `ListLeadsQueryDto`/`LeadsRepository.listByTenant`: `owner_id` por igualdade, sem filtro "sem proprietário" | Lista de Leads sem dono não é consultável (frontend só rotula "Sem responsável") — `VN-16` |
| K10 | Sem atribuição em lote; `PATCH /leads/{id}` aceita `owner_id` (inclusive `null`) individualmente | Escoar centenas de Leads exigiria N chamadas — `VN-16` |

### 3.3 Classificação do que já está definido

| Estado | Itens |
|---|---|
| `DECIDIDO` | 5 estados de disponibilidade; só *Disponível* recebe distribuição; disponibilidade global por usuário; consultor controla o próprio status, **exceto Treinamento** (só Gestor/Admin *(= Admin e Gerente — Gate do F4.2)* põem e retiram; consultor não entra nem sai; Sistema só futuramente); `business_hours` configurável por tenant, **não** altera status, **pode** restringir acesso a Leads/Conversas com liberação excepcional do Admin; Lead ≠ Cliente; ociosidade é de atendimento de **Cliente**, não de Lead; "Só mais um momento" deve ser considerado para evitar transferência indevida; "regra de 5 minutos" será detalhada depois; F4 agnóstica a canal; WhatsApp por tenant; módulo legado congelado; **(F4.0, 2026-10-05)** novo consultor inicia `INDISPONÍVEL`, sem transição automática por login/logout; tenant sem disponibilidade = comportamento da Fase 3; indisponibilidade não remove nem redistribui a carteira; consultor altera o próprio estado exceto Treinamento (Gestor/Admin); **Lead sem proprietário é estado legítimo**; diretrizes A1–A3 |
| `PROPOSTO` (neste documento ou no discovery do WhatsApp) | Todos os módulos, tabelas, endpoints, telas e incrementos abaixo. (A fronteira F4/F5 — A1–A3 — foi **aprovada como diretriz de planejamento**, §4/D-076; o critério G7 do Gate da Fase 5 segue pendente) |
| `PENDENTE` técnica (`TD-xx`, §17) | Representação do estado atual, formato da timeline, biblioteca de fuso horário, armazenamento das exceções, temporizador de ociosidade etc. |
| `VALIDAÇÃO DE NEGÓCIO` (`VN-xx`, §18) | **`VN-01` a `VN-05` fechados no F4.0; `VN-17.1`–`VN-17.5` fechados no Gate do F4.2.** Restam: política posterior de leads sem proprietário (`VN-16`), formato/regra de `business_hours`, liberação excepcional, tipos de interação, visibilidade, notificações, ciclo de vida da conversa, todos os detalhes da ociosidade |

## 4. Análise da fronteira F4 × F5 (diretrizes A1–A3 **aprovadas em 2026-10-05** — D-076)

**Pergunta**: a divisão do discovery do WhatsApp (núcleo `Conversation`/`Message` na F4; canal na F5) é tecnicamente coerente? **Resposta: coerente, com três ajustes** — apresentados como proposta no discovery e **aprovados em 2026-10-05 como diretriz de planejamento** ([D-076](../00-governance/decision-register.md#d-076--fronteira-f4f5-diretrizes-de-planejamento-da-fase-4-aprovadas-a1a3)).

### 4.1 O que a análise confirma
- O contrato `ChannelAdapter` já documentado ([architecture.md §4](../03-architecture/architecture.md)) é **normalizado** (`Message` com `direction`, `status`, `external_message_id`): o núcleo pode existir sem conhecer o canal.
- Disponibilidade, distribuição e `business_hours` **não dependem de canal** (D-071 diz que são globais e reutilizáveis) — precisam nascer na F4, antes de qualquer conversa real.
- A F5 só fica desacoplada do CRM Core se consumir uma **API interna estável** (`ConversationsService`, distribuição, disponibilidade, timeline). Isso é viável.

### 4.2 Riscos da divisão original
1. **Especulação**: sem canal real, `Message` na F4 só pode ser exercitada por um canal "manual". Modelar a mensagem antes de conhecer um payload real pode gerar retrabalho.
2. **Bloqueio por regra de negócio**: o ciclo de vida da conversa depende de pelo menos 6 regras ainda pendentes (VN-12: contato desconhecido, associação, encerramento/disposição, transferência, filas, SLA). Construí-lo cedo tende a fixar regra por acidente.
3. **Critério de aceite do roadmap para a F4** ("histórico de interações reflete leads, oportunidades e atendimentos manuais em uma linha do tempo única") **não exige** `Conversation`/`Message`.

### 4.3 Diretrizes aprovadas (`DECIDIDO` como planejamento — D-076)

| # | Ajuste | Justificativa |
|---|---|---|
| A1 | **Sequenciar**: entregar primeiro configurações, disponibilidade, distribuição, interações/timeline e notificações (F4.1–F4.5); o **núcleo Conversation/Message** vira o incremento **F4.6**, **condicional** à validação de VN-12. Se as regras não estiverem validadas, F4.6 migra para a **F5.0**, sem impedir a aceitação da F4 | Reduz retrabalho e mantém a F4 aceitável pelo critério do roadmap |
| A2 | **Não** criar `channel_account_id`, `file_assets` nem o registro de `ChannelAdapter` na F4. A F4 apenas **documenta** o contrato e mantém `channel_type` extensível; a coluna e a conta entram como **aditivas** na F5.0/F5.5 | Coluna anulável adicionada depois é migração não destrutiva; evita FK para tabela que ainda não existe (D-074) |
| A3 | `Conversation` usa **FKs dedicadas** (`customer_id`, `lead_id`, `opportunity_id`), **não** o modelo polimórfico de D-031 | D-031 decidiu o polimorfismo para notas/tarefas/compromissos; para conversas a integridade e o índice por sujeito importam mais, e a distinção Lead ≠ Cliente fica explícita no schema |

O roadmap recebeu notas no F4.0 (Fases 4 e 5) refletindo a diretriz: F4 cita "núcleo de Conversas/Mensagens agnóstico (F4.6, condicional)"; a F5 mantém integração, ChannelAccount, webhook, envio/recebimento, templates, mídia, tempo real e reconciliação de `communications`. A lista completa de funcionalidades da F5 não foi reescrita.

## 5. Arquitetura proposta da F4 — módulos (`PROPOSTO`)

| Módulo | Responsabilidade | Entidades | Serviços | Repositories / Controllers | Depende de | Eventos/filas | Impacto no frontend |
|---|---|---|---|---|---|---|---|
| `tenant-settings` | Ler/gravar configurações tipadas do tenant (`business_hours`, flag de disponibilidade) | `tenant_settings` (existe) | `TenantSettingsService` (registro de chaves + validação de schema), `BusinessHoursService` (avaliador puro: "agora está em horário?") | `TenantSettingsRepository`; `TenantSettingsController` | `audit` | — | Tela de configurações |
| `availability` | Estado atual + histórico + regras de transição (D-071) | `user_availability`, `availability_log` | `AvailabilityService` (transições, treinamento, auditoria), consulta de elegíveis | `AvailabilityRepository`; `AvailabilityController` | `users`, `audit`, `tenant-settings` | Evento in-process `availability.changed` | Controle de status; painel de gestão |
| `distribution` | Elegibilidade e escolha do responsável, genérico por "pool" | usa `tenant_settings` (cursor) | `EligibilityService` (ativo + Disponível + permissão + horário), `RoundRobinService` (movido de `leads`) | `RoundRobinRepository` | `users`, `availability`, `tenant-settings` | — | Nenhum direto |
| `interactions` | Registro manual de atendimento + **timeline** (read model) | `interactions` | `InteractionsService`, `TimelineService` (une fontes; cursor) | `InteractionsRepository`, `TimelineRepository`; controllers | `customers`, `leads`, `opportunities`, `notes`… | Escreve `lastInteractionAt` | Seção de timeline + formulário |
| `notifications` | Notificações in-app (primeira versão) | `notifications` | `NotificationsService` (criar/listar/ler) | Repository/Controller | eventos de domínio | Consumidor de eventos in-process | Sino/lista |
| `conversations` (F4.6, condicional) | Conversa: ciclo de vida, atribuição, transferência, encerramento, reabertura, disposição; **mensagens como sub-recurso** (padrão Contacts de D-065) | `conversations`, `messages`, `conversation_assignments`, `dispositions` | `ConversationsService`, `MessagesService`, `DispositionsService`, `ContactResolutionService` | Repositories/Controllers | `distribution`, `availability`, `customers`, `leads`, `notifications` | Eventos `conversation.*`, `message.*` | Telas de conversa |
| `access-control` (F4.7) | Restrição por `business_hours` + exceções do Admin | `access_exceptions` | `BusinessHoursGuard`, `AccessExceptionsService` | Repository/Controller | `tenant-settings`, `users` | — | Aviso "fora do horário" + tela do Admin |

Sobre os nomes: **`availability` / `distribution` / `interactions` / `notifications` / `conversations` são propostas de nome**, não obrigatórias. `messages` **não** é módulo próprio (evita colisão com as permissões `messages:*` legadas — TD-08). Não há módulo `channels` na F4 (ajuste A2).

Pré-requisitos transversais (entram no F4.0/F4.2): **(P1)** helper para executar código com contexto de tenant fora de HTTP e **ator "Sistema"** na auditoria (K4); **(P2)** serviço genérico de `tenant-settings` (K3).

## 6. Modelo de dados proposto (`PROPOSTO` — sem migration)

Convenções (todas seguem o schema atual): `id` UUID v7; `tenant_id` obrigatório e indexado; `created_at/updated_at`; `deleted_at` onde a BR-22 se aplica; toda mutação grava `audit_log` na mesma transação.

### 6.1 `user_availability` — estado **atual** (1:1 com `users`)
- **Finalidade**: consulta O(1) para elegibilidade. **Campos**: `user_id` (PK, FK users), `tenant_id`, `status` enum `available|unavailable|break|lunch|training`, `since` timestamptz, `set_by_user_id` (**não nulo** — o Sistema não altera estados), `reason` (opcional). **Índices**: `(tenant_id, status)`. **Soft delete**: não (acompanha o usuário). **Constraints**: PK em `user_id`. **Criação**: **sob demanda**, na primeira transição; **ausência de linha = `INDISPONÍVEL`** (aprovado, TD-01/VN-17.1) — sem criação no cadastro de usuário e sem backfill. **Auditoria**: `availability.changed` (payload: de → para, origem). **Riscos**: dupla escrita atual+log (mitigada por transação); primeira escrita concorrente (mitigada **serializando por usuário** com `SELECT … FOR NO KEY UPDATE` na linha do usuário em `users`, na mesma ideia do `RoundRobinRepository.lockCursor`; funciona também quando ainda não há linha de estado). **Estado:** `DECIDIDO` (Gate do F4.2).
- *Nomenclatura*: identificadores em inglês como o resto do schema; rótulos em português na UI. Substitui conceitualmente `agent_status_log` (vocabulário neutro).

### 6.2 `availability_log` — histórico (append-only)
- **Campos**: `id`, `tenant_id`, `user_id`, `status`, `started_at`, `ended_at` (nulo = corrente), `source` enum `user|manager` (**sem `system`**), `changed_by_user_id` (**não nulo**), `reason?`. **Índices**: `(tenant_id, user_id, started_at desc)`. **Soft delete**: não (BR-24 análogo: histórico não se apaga). **Risco**: crescimento — baixo (poucas linhas/dia/usuário).
- ~~Alternativa (TD-01): só o log com índice único parcial~~ **descartada** (Gate do F4.2): exige SQL manual (o Prisma não modela índice parcial). TD-01 resolvida com a tabela de estado atual + log.

### 6.3 `tenant_settings` (existente) — novas chaves
- `crm.availability.enabled` (boolean; **ausência = comportamento atual**, ver §9.6), `crm.business_hours` (schema v1 proposto na §13), `crm.business_hours.access_restriction` (VN-07). Sem migration (tabela existe).

### 6.4 `interactions` — registro manual de atendimento
- **Finalidade**: fato "houve contato com este Cliente/Lead" registrado por uma pessoa (MVP: "por qual canal, com qual resultado"). **Campos**: `entity_type` (`lead|customer|opportunity`, mesmo enum de D-031), `entity_id`, `author_id`, `channel` (texto curto — catálogo `PENDENTE` VN-09), `direction?` (`inbound|outbound` — VN-09), `summary`, `outcome?`, `occurred_at`, `deleted_at`. **Índices**: `(tenant_id, entity_type, entity_id, occurred_at desc)`, `(tenant_id, author_id)`. **Constraints**: validação de `entity_id` no Service (padrão D-031). **Auditoria**: `interaction.created/deleted`. **Riscos**: sobreposição com Nota — regra de fronteira: *Nota = anotação livre; Interação = evento de contato com data, canal e resultado*.

### 6.5 `notifications` (já documentada)
- `user_id`, `type`, `payload jsonb`, `read_at`, `created_at`. **Índice**: `(tenant_id, user_id, read_at, created_at desc)`. Sem soft delete. **Riscos**: retenção indefinida; eventos que geram notificação `PENDENTE` (VN-11).

### 6.6 `dispositions` (BR-15) — F4.6
- `name`, `active`, `deleted_at`; **sem** `queue_id` na F4 (VN-12: filas). Único `(tenant_id, name)` entre não excluídas.

### 6.7 `conversations` — F4.6
- **Campos**: `customer_id?`, `lead_id?`, `opportunity_id?` (FKs reais), `channel_type` (texto extensível; valor `manual` na F4), `external_contact_id?` (identificador normalizado do contato no canal — para contatos ainda sem cadastro), `status` `open|closed`, `assigned_to?`, `assigned_at?`, `disposition_id?`, `closed_at?`, `closed_by?`, `last_message_at?`, `last_customer_message_at?`, `last_agent_message_at?`, `deleted_at`. **Índices**: `(tenant_id, status, assigned_to)`, `(tenant_id, customer_id)`, `(tenant_id, lead_id)`, `(tenant_id, last_message_at desc)`. **Constraints**: **nenhuma** unicidade de conversa aberta por contato (VN-12); **nenhuma** regra que converta Lead em Cliente por existir conversa (BR-28). "Não atribuída" = `open` com `assigned_to` nulo (mesmo espírito de D-068/D-069). **Riscos**: invariantes de vínculo (Lead convertido) `PENDENTE` VN-14.

### 6.8 `messages` — F4.6
- **Campos**: `conversation_id`, `direction` `inbound|outbound`, `sender_type` `customer|agent|system`, `sender_user_id?`, `content`, `external_message_id?`, `status` `pending|sent|delivered|read|failed`, `error_code?`, `created_at`. **Sem** `attachment_id` (A2). **Índices**: `(conversation_id, created_at, id)`; **único** `(tenant_id, external_message_id)` — em Postgres `NULL`s são distintos, então o `@@unique` do Prisma serve (BR-20). **Soft delete**: não (imutável; some só com a conversa). **Riscos**: volume (D-014, particionamento adiado); dado pessoal (WA-27); TD-09: incluir `channel_type` na unicidade. `sender_type` + timestamps são o **insumo mínimo da ociosidade** (§12) — sem antecipar a regra.

### 6.9 `conversation_assignments` — F4.6
- Histórico append-only de responsável: `conversation_id`, `user_id?`, `assigned_by?` (nulo = Sistema), `reason` (`distribution|manual|transfer|claim|reopen`), `started_at`, `ended_at?`. Necessário para transferência, SLA e ociosidade; **não** substituível pelo `audit_log` (genérico, sem consulta relacional).

### 6.10 `access_exceptions` — F4.7 (condicional a VN-07/VN-08)
- `user_id`, `granted_by`, `starts_at`, `expires_at`, `reason`, `scope` (`leads|conversations|all`), `revoked_at?`. Índice `(tenant_id, user_id, expires_at)`. Auditoria de concessão/revogação. **Não inventa** a regra funcional: só oferece o mecanismo.

## 7. APIs propostas (`PROPOSTO` — sem OpenAPI ainda)

Convenções: prefixo `/v1`; `tenant_id` **nunca** em payload (contexto do JWT); recurso de outro tenant = **404**; erro no formato padrão do projeto; permissões por chave atômica.

### 7.1 Configurações e disponibilidade
| Método | Rota | Objetivo | Autorização | Payload → Resposta | Erros relevantes |
|---|---|---|---|---|---|
| GET/PUT | `/tenant-settings/business-hours` | Ler/gravar horário do tenant | `tenant_settings:read/update` | PUT: schema v1 → `{configured, business_hours, updated_at}` (GET devolve o mesmo envelope) | 400 formato inválido; 422 `BUSINESS_HOURS_INVALID` (fuso desconhecido, `start` ≥ `end`) — **implementado no F4.1** |
| GET/PUT | `/tenant-settings/availability` | Ligar/desligar uso de disponibilidade | `tenant_settings:read/update` | `{enabled}` | 400 se não for boolean — **implementado no F4.1** (sem efeito até o F4.3) |
| GET | `/availability/me` | Estado atual do próprio usuário **e se o mecanismo está habilitado** | autenticado | → `{enabled, status, since}` (sem registro: `status=unavailable`, `since=null`) | — |
| PUT | `/availability/me` | Usuário altera o **próprio** status (Disponível/Indisponível/Pausa/Almoço) | `availability:update` **ou** `availability:manage` (derivação 1 aprovada) | `{status, reason?}` → estado | **403 `AVAILABILITY_TRAINING_LOCKED`** ao tentar entrar em `training` ou sair dele; **409 `AVAILABILITY_DISABLED`** com a flag desabilitada; 400 status inválido |
| GET | `/availability` | Lista de estados dos usuários ativos do tenant (nome, estado, desde quando; sem registro = `unavailable`) | `availability:read` | filtros `status`, `page`/`limit` (offset, D-007) | — |
| PUT | `/users/{id}/availability` | **Admin/Gerente** colocam (`training`) ou retiram (→ `unavailable`, só a partir de `training`) um **terceiro** de Treinamento. Outros estados de terceiros **não** são aceitos (VN-17.2) | `availability:manage` | `{status, reason?}` | 403 transição não permitida (`AVAILABILITY_THIRD_PARTY_RESTRICTED`); 404 outro tenant; 409 usuário inativo, retirada sem estar em Treinamento ou flag desabilitada; 422 alvo = próprio usuário (`AVAILABILITY_SELF_TARGET`; derivações 3–4 aprovadas) |
| GET | `/users/{id}/availability/history` | Histórico | `availability:read` | cursor | 404 |

### 7.2 Interações e timeline
| Método | Rota | Objetivo | Autorização | Resposta | Erros |
|---|---|---|---|---|---|
| POST | `/interactions` | Registrar atendimento manual | `interactions:create` | `{entity_type, entity_id, channel, summary, outcome?, occurred_at?}` → interação | 404 entidade inexistente/outro tenant (D-031) |
| DELETE | `/interactions/{id}` | Soft delete | `interactions:delete` | 204 | 404 |
| GET | `/customers/{id}/interactions` (**já no OpenAPI**), `/leads/{id}/interactions`, `/opportunities/{id}/interactions` | Timeline unificada | `interactions:read` | `{data:[{type, occurred_at, summary, source_id…}], next_cursor}` (cursor) | 404 |

### 7.3 Notificações e conversas (F4.5–F4.6)
| Método | Rota | Objetivo | Autorização |
|---|---|---|---|
| GET | `/notifications` (cursor), `/notifications/unread-count` | Do próprio usuário | autenticado (escopo próprio) |
| POST | `/notifications/{id}/read`, `/notifications/read-all` | Marcar lidas | autenticado (próprio) |
| CRUD | `/dispositions` | Lista configurável (BR-15) | `dispositions:*` |
| GET | `/conversations` (cursor; filtros `status`, `assigned_to`, `unassigned`, `customer_id`, `lead_id`) | Lista | `conversations:read` (**escopo de visibilidade = VN-10**) |
| POST | `/conversations` | Abrir conversa (canal `manual`) | `conversations:create` |
| GET | `/conversations/{id}` | Detalhe | `conversations:read` |
| GET/POST | `/conversations/{id}/messages` | Listar (cursor) / registrar mensagem | `conversations:read` / `conversations:update` |
| POST | `/conversations/{id}/assign`, `/transfer` | Atribuir/transferir (regra: VN-12) | `conversations:assign` |
| POST | `/conversations/{id}/close`, `/reopen` | Encerrar (com disposição) / reabrir | `conversations:update` |

Erros comuns: 404 (outro tenant), 409 (estado inválido: fechar conversa já fechada), 422 (validação). Endpoints de F4.7: `POST/GET/DELETE /access-exceptions` (`access_exceptions:manage`).

### 7.4 Permissões novas (`PROPOSTO`)
`availability:read|update|manage` (**aprovadas** — TD-08; mapeamento por papel em [D-077](../00-governance/decision-register.md#d-077--disponibilidade-modelo-de-dados-e-permissões-td-01-td-08)), `interactions:create|read|delete`, `dispositions:create|read|update|delete`, `conversations:create|read|update|assign|delete`, `access_exceptions:manage`; reaproveita `tenant_settings:read|update`. **Não** usar `messages:*` (legado — K1). Elegibilidade para receber conversas = `conversations:update` (espelha D-068: a mesma chave que autoriza agir autoriza receber). Quais papéis de fábrica recebem cada chave é `PROPOSTO`/seed, sujeito a VN-05 e VN-10.

## 8. Frontend proposto (`PROPOSTO`)

| Item | Proposta | Reaproveita |
|---|---|---|
| Controle de status | Seletor no `AppShell` (topo mobile / rodapé da sidebar) com os 4 estados que o consultor pode escolher; **Treinamento** aparece como estado **somente leitura** ("definido pelo gestor") e trava o seletor; refetch a cada ~30 s (padrão `useHealth`) para refletir mudança feita pelo gestor | `useAuth`, `api.ts`, Tailwind/UI kit |
| Painel de gestão | `/team/availability`: lista de usuários + estado + ação (permissão `availability:manage`); exige **service de usuários** (hoje inexistente no frontend) | padrão de lista de `customers` |
| Configurações | `/settings/business-hours` (admin): dias/janelas/fuso. Nenhuma tela de settings existe | padrão de formulário `CustomerForm` |
| Timeline | `TimelineSection` embutida em `CustomerDetailPage`, `LeadDetailPage`, `OpportunityDetailPage` (props `entityType/entityId`); usa `useInfiniteQuery` (**primeiro uso no repo**); `InteractionForm` para registro manual | seções de follow-up |
| Conversas (F4.6) | `/conversations` (lista + filtros), `/conversations/:id` (thread + compositor do canal `manual` + ações assign/transfer/close/reopen); item no `AppShell`; polling (sem WebSocket — D-013 é F5) | padrão list/detail |
| Notificações | Sino no `AppShell` com contador (polling) + lista | — |
| Permissões de UI | `hasPermission('availability:manage')` etc. — só UX; backend valida | `useAuth` |
| Higiene | trocar "CRM + Call Center" por "CRM Universal"; corrigir comentário de `AuthUser.permissions` | — |

Nenhuma dependência nova é necessária (a lista de fusos usa `Intl.supportedValuesOf`; TD-04 trata a biblioteca de fuso só se o `Intl` não bastar).

## 9. Disponibilidade — plano técnico (D-071)

### 9.1 Mapeamento pedido → proposta
| Tema | Proposta (`PROPOSTO`) | Decisão de negócio pendente |
|---|---|---|
| Estado atual | Tabela 1:1 `user_availability` (§6.1) | **DECIDIDO** (VN-01 + VN-17.1): sem registro = `INDISPONÍVEL`; existentes sem registro continuam `INDISPONÍVEIS` ao habilitar; sem transição automática para `DISPONÍVEL` |
| Histórico | `availability_log` append-only na mesma transação | — |
| 5 estados | Enum `available, unavailable, break, lunch, training`; rótulos PT na UI | — |
| Nomenclatura neutra | Módulo `availability`; abandona `agent_status_log`/`AgentStatus` | — |
| Login/logout | **Sem transição automática** na primeira implementação (**decidido**). Contexto técnico: a sessão é por dispositivo (`logout` revoga 1 refresh token; o usuário pode estar logado em outro) e não há noção de presença | **DECIDIDO** (VN-01) |
| Quem altera | **Decidido (VN-05)**: consultor altera o próprio estado entre Disponível/Indisponível/Pausa/Almoço; **Admin/Gerente** colocam e retiram de Treinamento. **Aprovado (TD-08)**: `availability:update` (próprio), `availability:manage` (Treinamento de terceiros) e `availability:read`, por permissão e não por nome de papel | **DECIDIDO** (VN-17.2/17.4): Admin e Gerente só colocam/retiram terceiros de Treinamento; permissões por papel em [D-077](../00-governance/decision-register.md#d-077--disponibilidade-modelo-de-dados-e-permissões-td-01-td-08) |
| Treinamento | Regra no Service: o consultor (ator do próprio estado) não entra nem sai de `training` ⇒ `AVAILABILITY_TRAINING_LOCKED`; Admin/Gerente sim (só em terceiros). **Sem duração automática**: termina por remoção manual; registra-se `since` (VN-17.3). O **Sistema não altera estados agora**; a origem `system` **não** é criada | **DECIDIDO** (VN-05, VN-17.3) |
| Persistência | Atual + log na mesma `tx` | — |
| Auditoria | `availability.changed` com de/para/origem; o ator é sempre um usuário — P1/ator Sistema **não** é necessário no F4.2 | — |
| Impacto na distribuição | §10 | — |
| `business_hours` | Não altera status (decidido); é lido à parte (§13) | VN-07 |
| Liberação excepcional | §13.4 | VN-08 |
| Tenant que não usa disponibilidade | Flag `crm.availability.enabled`, **ausente/false = comportamento atual** (todos os ativos com permissão elegíveis) | **DECIDIDO** (VN-02, VN-17.5): sem o mecanismo, vale a Fase 3. Quem habilita: `tenant_settings:update` (só Admin). **Flag desabilitada**: seletor oculto, escritas bloqueadas pela API, distribuição ignora, estados preservados e retomados ao reativar, sem reset |
| Leads já atribuídos a quem fica indisponível | **Decidido**: a carteira é mantida; nenhuma redistribuição automática nem "retirar carteira" | **DECIDIDO** (VN-03) |

### 9.2 Máquina de transição (proposta)
Qualquer estado ↔ qualquer estado, **exceto** as travas de Treinamento. Restrições do que **não** foi decidido (ex.: Almoço só em faixa horária, limite de Pausa) ficam de fora — BR-16 permanece pendente (VN-06).

### 9.3 Segurança do rollout
Com o estado inicial decidido (VN-01: `INDISPONÍVEL`), **habilitar** a disponibilidade em um tenant faz com que **ninguém** seja elegível até que cada consultor se coloque `DISPONÍVEL`. É consequência esperada da decisão — não um erro: Leads criados nesse intervalo ficam **sem proprietário**, estado legítimo ([D-075](../00-governance/decision-register.md#d-075--lead-sem-proprietário-é-um-estado-legítimo-do-negócio)). A flag permanece **desligada por padrão** (VN-02). Aviso ao Admin e visibilidade de "quantos estão disponíveis" na ativação são **proposta** para F4.2/F4.3, sem criar regra de negócio nova.

## 10. Distribuição — evolução do Round Robin (F3.4 → F4)

**Hoje** (código): ativo + permissão `leads:update`, sem disponibilidade e sem horário. **Alvo** (D-071/BR-05/BR-14): ativo + Disponível + permissão (+ horário, ver C5).

| Aspecto | Análise / proposta |
|---|---|
| Elegibilidade | `EligibilityService.list(permission, poolKey)`: `users.status='active' ∧ deleted_at null ∧ tem permissão ∧ (flag off ∨ availability='available') ∧ (sem config de horário ∨ agora ∈ horário)` — o último termo depende de VN-07 |
| Cursor | Manter `tenant_settings` (D-068), com **chave por pool** (`crm.lead_round_robin.cursor` já existe; conversas usariam outra chave **se** a rotação for separada — VN-12/WA-09) |
| Concorrência | Manter `SELECT … FOR UPDATE` na linha `(tenant,key)`. **Correção proposta (K5)**: ler a elegibilidade **dentro da `tx`, depois do lock**, em vez de antes/fora. Uma mudança de disponibilidade que ocorra entre a leitura e a atribuição continua possível (ms) e é aceitável — não há requisito de consistência estrita |
| Justiça | Trocar "índice do último + 1, reinício se ausente" por "**primeiro id maior que o último**" (circular). Hoje, se o último atribuído fica indisponível, a rotação volta ao menor id e o favorece. É melhoria técnica, sem regra de negócio nova |
| Usuários indisponíveis | Saem do conjunto; ao voltar, reentram pela ordem de id |
| Ninguém elegível | Mantém D-068/D-069: `owner_id = null`, `lead.unassigned` na auditoria (evento **informativo**). **Lead sem proprietário é estado legítimo (D-075/VN-04 decidido)** — não é erro. Com disponibilidade e horário isso passa a ocorrer com mais frequência; a política de **como/quando esses leads são atribuídos depois** (lote, reivindicação, Gestor) permanece **PENDENTE (`VN-16`)** e **não é definida** neste plano |
| Leads já atribuídos | **Decidido (VN-03)**: sem redistribuição; a disponibilidade só afeta a elegibilidade para **novos** Leads |
| Fallback | **Decidido (VN-02)**: flag desligada = comportamento de hoje |
| Criação/importação sem proprietário | **Lacuna técnica (K8–K10)**, não alterada: hoje criar/importar sem `owner_id` sempre aciona o round-robin; não há modo explícito "sem proprietário", filtro "sem proprietário" nem atribuição em lote. O tratamento depende de `VN-16` |
| Reuso | O mesmo `EligibilityService` serve a conversas na F4.6 (pool e permissão próprios) |
| Regressão | Testes e2e de lead existentes devem passar **sem alteração** com a flag desligada |

## 11. Interações e Conversas

### 11.1 `Interaction`: entidade, projeção ou união?
| Opção | Prós | Contras |
|---|---|---|
| (a) Entidade única `interactions` que copia tudo (nota, tarefa, mensagem…) | Consulta simples | **Duplica** Notas/Tarefas/Compromissos/Mensagens; risco de dessincronização |
| (b) Só projeção (união dos que já existem) | Sem duplicação | Não há onde registrar o **atendimento manual** (que não é nota, tarefa nem compromisso) |
| **(c) Híbrida (recomendada)** | Entidade `interactions` **apenas** para o contato manual + **timeline como read model** que une `interactions`, `notes`, `appointments`/`tasks` (quando o negócio quiser) e, na F4.6, `conversations` | Precisa de cursor sobre união; o tipo de cada item vem da fonte |

Regras de fronteira: Nota = anotação; Interação = evento de contato; Tarefa/Compromisso = futuro (aparecem na timeline só se VN-09 disser que sim); Mensagens **não** são copiadas — aparecem via `conversations`. O `audit_log` **não** é fonte de timeline (é técnico e sem esquema estável).

**Cursor da união (TD-02)**: `(occurred_at, source, id)`; implementação por `UNION ALL` em SQL ou por busca por fonte + merge limitado — decidir no F4.4 com medição. Índices por fonte já existem `(tenant, entity_type, entity_id)`.

**Efeito colateral proposto**: um único ponto (`InteractionsService.touch`) atualiza `Customer.lastInteractionAt` quando o negócio definir o que conta como interação (VN-09). Para **Lead** (que não tem esse campo) nada é escrito — coerente com BR-28.

### 11.2 Vínculos e Lead ≠ Cliente
`Conversation` referencia `customer_id` **ou** `lead_id` (ambos anuláveis) e, opcionalmente, `opportunity_id`. **Nenhuma regra converte Lead em Cliente por existir conversa** (BR-28). Um Lead que não converte **permanece Lead** e pode ser trabalhado novamente ([D-075](../00-governance/decision-register.md#d-075--lead-sem-proprietário-é-um-estado-legítimo-do-negócio)). O que ocorre com a conversa quando o Lead é convertido (migrar? duplicar vínculo?) é **VN-14**. A timeline do Cliente inclui ou não o histórico do Lead de origem: **VN-09**.

### 11.3 Ciclo de vida e responsável
Estados propostos `open|closed` (já na spec) + "não atribuída" derivada (`open ∧ assigned_to null`). Ações: abrir, atribuir (via distribuição ou manual), transferir, encerrar (com disposição — BR-15), reabrir. **Todas as regras** (quem transfere, motivo obrigatório, o que é "finalizada", disposição obrigatória, reabrir vs. abrir nova, "claim") são **VN-12**; o plano só entrega o mecanismo e o histórico (`conversation_assignments`).

### 11.4 Por que FKs e não polimorfismo em `Conversation`
D-031 aplica-se a notes/tasks/appointments. Conversa é entidade central, consultada por sujeito com frequência, e a distinção Lead × Cliente precisa estar no esquema; FKs reais dão integridade e índice. Notas/tarefas continuam ligadas a `lead|customer|opportunity` (sem novo tipo `conversation` — só se o negócio pedir, TD).

### 11.5 Participantes, origem e visibilidade
Sem tabela de participantes na F4 (um responsável por vez; histórico em `conversation_assignments`). Origem/canal abstrato = `channel_type` + `external_contact_id`. Visibilidade (próprio/equipe/tenant) é **VN-10**: o RBAC real é tenant-only e conversas contêm dado pessoal — **não implementar leitura de conversas sem essa decisão**.

## 12. Ociosidade (BR-28 / D-071)

| Já decidido | Ainda **pendente** (VN-13) |
|---|---|
| A regra é de **atendimento de Cliente**, **não** de Lead | O que o contador de 5 min mede e quando começa |
| Uma interação do consultor durante o atendimento (ex.: "Só mais um momento") deve ser considerada para evitar transferência indevida | Quais eventos **reiniciam** o contador (e se "Só mais um momento" reinicia ou só suspende) |
| A "regra de 5 minutos" será detalhada depois | O que ocorre ao expirar (transferir? alertar?) e para quem |
| Não implementar agora | Como escolher o **próximo consultor** e a **prioridade** |
| — | **Mensagens automáticas** e demais regras de transferência |
| — | Interação com Pausa/Almoço/Treinamento e com `business_hours`; configurabilidade por tenant |

**O que o plano prepara sem decidir**: `messages.sender_type`, `last_customer_message_at`, `last_agent_message_at` e `conversation_assignments` (insumos) — e a distinção Cliente × Lead resolvida pelo vínculo da conversa. **Mecanismo de temporização (TD-06)** — atraso por conversa (BullMQ *delayed job* rearmado a cada evento) **ou** varredura periódica (padrão já usado pelo módulo legado) — só é escolhido no F4.8, depois da regra. Requer P1 (execução por tenant fora de HTTP) e ator Sistema.

## 13. Business hours — plano técnico

| Aspecto | Proposta (`PROPOSTO`) |
|---|---|
| Persistência | Chave existente `crm.business_hours` em `tenant_settings` (D-068), valor versionado |
| Formato v1 (conteúdo `PENDENTE` VN-07) | `{ "schema_version": 1, "timezone": "America/Sao_Paulo", "weekly": [{ "days": [1,2,3,4,5], "start": "08:00", "end": "18:00" }] }` — **feriados/exceções pontuais não incluídos** (VN-07); um horário por tenant (não por filial/equipe — VN-07) |
| Fuso | IANA por tenant; avaliação em fuso do tenant; testes com relógio fixo e virada de dia/mês; TD-04 (`Intl` × biblioteca) |
| Leitura | `BusinessHoursService.isOpen(tenantId, now)` puro e testável; leitura por chave única (barata; `PermissionsGuard` já faz consulta por requisição), cache curto opcional |
| Escrita | `PUT /tenant-settings/business-hours` com validação de schema e auditoria |
| Efeito na distribuição | Filtro do tenant inteiro (BR-05); consequência (Lead sem dono fora do horário é legítimo — D-075; política posterior: `VN-16`) |
| Efeito no acesso (BR-27) | `BusinessHoursGuard` nas rotas de Leads/Conversas; **por padrão desligado** até VN-07 definir quem é restringido, se é bloqueio total ou só escrita, e se Admin/gestores estão isentos. Erro proposto: 403 `OUTSIDE_BUSINESS_HOURS` |
| Liberação excepcional (§6.10) | Mecanismo `access_exceptions` (por usuário, com expiração, motivo e auditoria) — a regra funcional (duração, escopo, quem pede) é **VN-08** |
| Segurança | Guard nunca pode trancar o Admin para fora da própria configuração; rota de settings isenta |

## 14. Estratégia de testes

| Tipo | Escopo |
|---|---|
| Unit | Matriz de transições de disponibilidade (incl. trava de Treinamento e ator Sistema); `EligibilityService` (todas as combinações ativo/estado/permissão/flag/horário); `BusinessHoursService` (fuso, virada de dia, bordas de janela) com relógio fixo; merge/cursor da timeline; máquina de estados de conversa/mensagem |
| Integração/e2e (Postgres real, como hoje) | Fluxos de cada API nova; `resetDatabase` atualizado com **todas** as tabelas novas (K7); seed com as permissões novas |
| Tenant isolation | Para **cada** recurso novo, cópia do padrão de `tenant-isolation.e2e-spec.ts`: recurso do tenant B → 404 para o tenant A; nenhuma listagem vaza |
| RBAC | Cada rota nova × papel com/sem a permissão (403); consultor tentando entrar/sair de Treinamento; usuário inativo |
| Concorrência (distribuição) | N criações de lead em paralelo (`Promise.all`) no mesmo tenant: atribuições distintas em rodízio, cursor consistente, **nenhum lead com dono inelegível**; mudança de disponibilidade durante a rajada (aceita janela de ms; testa ausência de erro e de duplicidade) |
| Regressão do Round Robin | Suíte atual de leads passa **sem alteração** com a flag desligada |
| Histórico | Log de disponibilidade fecha `ended_at` da linha anterior na mesma transação; ordem cronológica |
| Timeline | Itens de várias fontes ordenados; cursor estável com timestamps iguais; sem vazamento entre tenants; Lead e Cliente separados |
| Conversas | Ciclo abrir→atribuir→transferir→encerrar→reabrir; vínculo Lead **não** cria Cliente; idempotência por `external_message_id`; imutabilidade de mensagens |
| Ociosidade (F4.8) | Só depois da regra: relógio simulado, casos de reinício e "Só mais um momento"; teste de que **Lead nunca** dispara |
| Frontend | RTL por tela (estado de loading/erro/vazio), permissão oculta/exibida, seletor com Treinamento travado, timeline com paginação |
| Fora | Testes de carga (D-014/Fase 9) |

## 15. Incrementos propostos — F4.x (`PROPOSTO`)

> Cada incremento só inicia com o anterior aceito e com as **decisões necessárias** fechadas e registradas no Decision Register. Todos herdam: tenant isolation, RBAC por permissão, soft delete onde couber, auditoria na mesma transação, OpenAPI **antes** do código, testes.

### F4.0 — Fechamento de decisões e ajustes de spec *(documentação; sem código)* — **executado em 2026-10-05; aguarda aprovação**
- **Objetivo**: transformar `PROPOSTO` em `DECIDIDO` o que o negócio aprovou e atualizar os documentos (§21).
- **Realizado**: `VN-01`–`VN-05` e `A1`–`A3` registradas (D-071, D-075, D-076); BR-14/BR-29, RF-12/RF-15, `entities.md`/`relationships.md` (notas e FKs de `conversations`), `workflows.md §1`, UC-01 e `roadmap.md` ajustados; este plano revisto; links verificados.
- **Backend/Frontend/Banco/API**: nenhum.
- **Decisões necessárias (fechadas)**: fronteira F4/F5 (A1–A3); VN-01, VN-02, VN-03, VN-04, VN-05.
- **Não decidido / fora desta etapa**: TD-01 e TD-08 (decisões técnicas — antes do F4.2); rascunho de OpenAPI e revisão completa de `entities.md` (enum e tabelas novas) — feitos **antes do código de cada incremento** (critério 8 da §20).
- **Aceite**: decisões registradas ✔; documentos coerentes ✔; **aprovação do responsável pelo produto — pendente**.
- **Fora**: qualquer implementação; ociosidade; regras de conversa; política de `VN-16`.

### F4.1 — Fundação: `tenant-settings` + avaliador de `business_hours` — **implementado em 2026-10-05 (branch `feat/f4-1-tenant-settings`, enviada ao origin; aguardando aprovação/merge)**
- **Objetivo**: P2 e infraestrutura de configuração; **sem mudar comportamento**.
- **Backend**: `TenantSettingsService` (registro de chaves e schema), `BusinessHoursService`, controller `GET/PUT /tenant-settings/business-hours` e `/availability`; migrar a leitura do round-robin para o serviço; **P1** (contexto de tenant fora de HTTP + ator Sistema) — **não é mais exigido pelo F4.2** (o Sistema não altera estados agora; VN-05); necessário antes do F4.8 e da F5 (webhook/worker); momento de entrega em `TD-13`.
- **Frontend**: tela `/settings/business-hours`; item de menu (permissão).
- **Banco**: nenhuma tabela nova.
- **API**: §7.1 (settings).
- **Testes**: unit do avaliador (fuso/bordas); e2e de RBAC/isolamento/auditoria; regressão do round-robin.
- **Dependências**: nenhuma.
- **Decisões necessárias**: **VN-07** (conteúdo do formato), TD-04, TD-10.
- **Aceite**: horário configurável e auditado; nenhum efeito em Leads; P1 (se entregue neste incremento — `TD-13`) coberto por teste.
- **Fora**: aplicar horário à distribuição ou ao acesso.
- **Implementado (fatos)**: módulo `tenant-settings` no backend (`TenantSettingsService`, `BusinessHoursService`, módulo puro `business-hours.ts`, controller com 4 rotas); **sem migration** — reutiliza a tabela `tenant_settings`; **sem permissão nova** (`tenant_settings:read|update`, hoje só no papel `admin`); `RoundRobinService` passou a consultar a presença de `crm.business_hours` pelo serviço (mesmo comportamento; log `warn` → `debug`); frontend: `/settings/business-hours` + item "Config." no `AppShell` (visível só com `tenant_settings:read`) + `apiPut`; OpenAPI atualizado. A flag `crm.availability.enabled` só tem API (sem tela — a UI de disponibilidade é F4.2+).
- **Decisões técnicas tomadas neste incremento**: `TD-04` — `Intl` (nenhuma dependência nova); `TD-10` — chaves `crm.business_hours` e `crm.availability.enabled` (valor boolean JSON); `TD-13` — **P1 não entregue** no F4.1 (sem consumidor nos F4.2–F4.5; entra antes do F4.8/F5). Detalhes do formato v1 implementados: dias ISO 1–7, `HH:mm`, `start < end` (sem janelas que atravessam a meia-noite), dias únicos por janela, 1–21 janelas, fuso IANA validado por `Intl`. **VN-07 continua pendente** — o formato v1 é a proposta versionada do plano, não uma decisão de negócio; feriados, horário por filial/equipe, restrição de acesso e efeito na distribuição **não** foram implementados nem decididos.
- **Contrato**: `GET/PUT /v1/tenant-settings/business-hours` e `/availability` (OpenAPI). GET de horário devolve `{configured, business_hours, updated_at}` (ausente ou fora do formato v1 ⇒ `configured:false`); PUT é idempotente (valor igual não reescreve nem audita); erros: 400 estrutural, 422 `BUSINESS_HOURS_INVALID` semântico. Não há `DELETE` (não previsto no plano): uma vez gravado, o horário só pode ser substituído.
- **Testes automatizados adicionados**: backend — 21 unit (`business-hours.spec.ts`, `tenant-settings.service.spec.ts`) + 13 e2e (`tenant-settings.e2e-spec.ts`: persistência, 400/422, auditoria, idempotência, RBAC, isolamento entre tenants, linha legada fora do formato, "sem efeito operacional" na distribuição); frontend — 13 (`BusinessHoursPage.test.tsx`) + 2 (`AppShell.test.tsx`).

### F4.2 — Disponibilidade (núcleo) — **implementado em 2026-10-05 (branch `feat/f4-2-availability`, commits locais, sem push; aguardando revisão)**
- **Objetivo**: estado atual, histórico, transições e controle de Treinamento (D-071), sem efeito na distribuição.
- **Backend**: módulo `availability` (service com a transição numa única transação: garantir linha → travar → validar → fechar log aberto → inserir log → atualizar estado → auditar `availability.changed`; estado igual ao atual não grava); permissões `availability:read|update|manage` no seed (mapeamento em [D-077](../00-governance/decision-register.md#d-077--disponibilidade-modelo-de-dados-e-permissões-td-01-td-08)); bloqueio das escritas com a flag desabilitada. **Sem** evento in-process obrigatório e **sem** P1.
- **Frontend**: seletor no `AppShell` (somente com a flag habilitada e permissão; Treinamento aparece travado e somente leitura); painel `/team/availability` para `availability:read` (e ação de Treinamento para `manage`), oculto com a flag desabilitada; atualização por polling (~30 s); a lista traz o nome do usuário (sem exigir `users:read`).
- **Banco**: `user_availability`, `availability_log`, enum Postgres de 5 estados (e de `source`); migration revisada à mão.
- **API**: §7.1 (disponibilidade) e rascunho no `openapi.yaml` (já registrado no Gate).
- **Testes**: matriz de transições; trava de Treinamento (próprio e terceiros); terceiros só entram/saem de Treinamento; RBAC por papel (incluindo `operador`, `supervisor` e `diretor` sem escrita); isolamento de tenant em todas as rotas; ausência de linha = `INDISPONÍVEL`; flag desabilitada (escritas 409, leitura ok, estados preservados e retomados); idempotência; fechamento do log; **concorrência** (alterações simultâneas do mesmo usuário deixam uma única linha aberta); regressão — Round Robin e e2e existentes sem alteração e teste de que o estado **não** afeta a distribuição até o F4.3; `resetDatabase` com as tabelas novas.
- **Operacional**: tenants **já existentes** precisam das chaves novas nos papéis de fábrica (rodar o seed idempotente ou passo manual — D-059; papéis de sistema são imutáveis pela API).
- **Dependências**: F4.1 (flag `crm.availability.enabled`); P1 **não** é necessário.
- **Decisões**: tudo fechado no Gate (§0.6); derivações técnicas **aprovadas** em 2026-10-05.
- **Aceite**: o usuário altera o próprio estado entre Disponível/Indisponível/Pausa/Almoço (não entra nem sai de Treinamento); Admin/Gerente colocam e retiram terceiros de Treinamento; sem registro = Indisponível; histórico completo e auditado; com a flag desabilitada nada é alterável e nada é perdido; **nenhum efeito na distribuição**.
- **Fora**: transições automáticas por login/logout/inatividade e quaisquer alterações pelo Sistema; duração/`ends_at` de Treinamento; alteração arbitrária de estados de terceiros; escopo por equipe/filial; limites de Pausa e alertas (BR-16); distribuição (F4.3); `VN-16`; `business_hours` como regra operacional.
- **Implementado (fatos)**:
  - **Banco**: migration aditiva `20261005120000_f4_2_availability` (enums `AvailabilityStatus`/`AvailabilitySource`; tabelas `user_availability` e `availability_log`); gerada por diff contra shadow DB e revisada (nenhum `DROP`/`ALTER` em tabela existente).
  - **Backend**: módulo `availability` (regras puras em `availability-rules.ts`, repository, service, 2 controllers); rotas `GET/PUT /v1/availability/me`, `GET /v1/availability`, `PUT /v1/users/{id}/availability`, `GET /v1/users/{id}/availability/history` (cursor). Transição = estado atual + log + auditoria `availability.changed` numa transação, **serializada por usuário** (`SELECT … FOR NO KEY UPDATE` em `users`); estado igual ao atual não grava. Próprio estado autorizado por `availability:update` **ou** `availability:manage` (checado no service, pois `@RequirePermissions` exige todas as chaves). Via de terceiros: só `training` e retirada → `unavailable`. Exceções de domínio com códigos estáveis. Seed com o mapeamento aprovado.
  - **Frontend**: seletor no `AppShell` (4 estados; Treinamento travado; polling 30 s; oculto sem permissão ou com a flag desabilitada), item "Equipe" e página `/team/availability` (lista, filtro por estado, paginação, colocar/retirar de Treinamento para `manage`; nunca o próprio usuário).
  - **Sem efeito na distribuição** (confirmado por e2e), sem P1, sem Sistema, sem `system` no enum, sem worker/timer.
- **Testes automatizados adicionados**: backend — 56 unit (`availability-rules.spec.ts` matriz 4×4 + travas; `availability.service.spec.ts`) e 22 e2e (`availability.e2e-spec.ts`: transições + log encadeado + auditoria, idempotência, validação 400, RBAC por papel incluindo `operador`/`supervisor`/`diretor`, Treinamento travado, terceiros restritos, flag desabilitada com estados preservados e retomados, lista com filtro/offset, histórico com cursor, isolamento entre tenants, concorrência do mesmo usuário e usuário × gestor, round-robin e carteira inalterados); frontend — 23 (`AvailabilitySelector.test.tsx`, `TeamAvailabilityPage.test.tsx`, `AppShell.availability.test.tsx`). Nenhum teste existente foi alterado.
- **Operacional (pendente de execução em ambientes reais)**: tenants **já existentes** precisam rodar o seed idempotente (ou passo manual de dados — D-059) para os papéis de fábrica receberem `availability:*`. Não executado em nenhum ambiente além do banco de teste.

### F4.3 — Distribuição v2 (ativo + Disponível + permissão)
- **Objetivo**: aplicar D-071 ao Round Robin da F3.4.
- **Backend**: módulo `distribution` (extrai `RoundRobinService`); leitura de elegibilidade dentro da `tx` após o lock; cursor "primeiro id maior"; filtro por disponibilidade atrás da flag; filtro por horário conforme VN-07.
- **Frontend**: nenhuma tela obrigatória; visibilidade de "Leads sem proprietário" (filtro/indicador) é **candidata**, dependente de `VN-16` — Lead sem proprietário é estado legítimo, não um alerta.
- **Banco**: nenhuma.
- **API**: nenhuma nova (ajuste de comportamento de `POST /leads`).
- **Testes**: elegibilidade combinatória; **concorrência**; regressão com flag off; "nenhum elegível" (Lead permanece sem proprietário); carteira existente **não** alterada ao ficar indisponível.
- **Dependências**: F4.1, F4.2.
- **Decisões necessárias**: VN-02, VN-03 e VN-04 **fechadas** (F4.0); `VN-16` (política posterior) **não bloqueia** o F4.3 desde que ele não implemente redistribuição nem atribuição em lote; VN-07 (efeito do horário na distribuição) **pendente**.
- **Aceite**: com flag ligada só usuários Disponíveis recebem **novos** Leads; flag desligada = comportamento idêntico ao atual; rodízio justo sob concorrência; carteira existente intocada; Lead sem proprietário continua válido.
- **Fora**: redistribuição de leads já atribuídos (decidido: não há — VN-03); distribuição posterior/em lote de Leads sem proprietário e modo "criar/importar sem distribuir" (K8–K10, `VN-16`); distribuição de conversas.

### F4.4 — Interações e timeline
- **Objetivo**: histórico unificado (critério de aceite do roadmap para a F4).
- **Backend**: `interactions` (entidade + `TimelineService` como read model); `GET /customers|leads|opportunities/{id}/interactions`; escritor único de `lastInteractionAt`.
- **Frontend**: `TimelineSection` nas 3 páginas de detalhe; `InteractionForm`; `useInfiniteQuery`.
- **Banco**: `interactions`.
- **API**: §7.2 (atualiza `Interaction.type` no OpenAPI — remove `call`).
- **Testes**: união multi-fonte, cursor, isolamento, Lead ≠ Cliente.
- **Dependências**: F4.1 (P1 para auditoria consistente).
- **Decisões necessárias**: **VN-09**, VN-10 (visibilidade), TD-02.
- **Aceite**: linha do tempo única de leads, oportunidades e atendimentos manuais por entidade.
- **Fora**: mensagens/conversas; edição de interação; automações.

### F4.5 — Notificações (primeira versão)
- **Objetivo**: entregar o destino para "lead atribuído/conversa atribuída" e alertas.
- **Backend**: `notifications` + consumidor de eventos in-process; endpoints §7.3.
- **Frontend**: sino + lista; polling.
- **Banco**: `notifications`.
- **Testes**: escopo próprio (usuário A não lê notificação de B), isolamento, marcação de lida.
- **Dependências**: F4.3 (evento de atribuição).
- **Decisões necessárias**: **VN-11** (quais eventos/destinatários), VN-06 se BR-16 entrar.
- **Aceite**: eventos definidos geram notificações in-app; leitura/contagem funcionam.
- **Fora**: push/e-mail/WhatsApp; WebSocket.

### F4.6 — Núcleo de Conversas/Mensagens *(condicional a VN-12; senão → F5.0)*
- **Objetivo**: núcleo **agnóstico a canal**, exercitado pelo canal `manual`.
- **Backend**: `conversations` (+ mensagens como sub-recurso), `dispositions`, `conversation_assignments`, `ContactResolutionService` (identificador → Cliente/Lead, **sem** escolher automaticamente entre candidatos — espírito de D-067), distribuição de conversas (reusa `EligibilityService`).
- **Frontend**: `/conversations`, `/conversations/:id`, ações.
- **Banco**: `conversations`, `messages`, `conversation_assignments`, `dispositions`.
- **API**: §7.3.
- **Testes**: ciclo completo, vínculo Lead/Cliente, idempotência, isolamento, visibilidade (VN-10).
- **Dependências**: F4.2, F4.3, F4.4, F4.5.
- **Decisões necessárias**: **VN-10, VN-12, VN-14**; TD-03, TD-09.
- **Aceite**: conversa manual percorre abrir→atribuir→transferir→encerrar→reabrir com histórico; **nada específico de canal no código**; Lead não vira Cliente.
- **Fora**: WhatsApp, `ChannelAdapter` concreto, mídia, templates, tempo real, ociosidade, SLA.

### F4.7 — Restrição por `business_hours` e liberação do Admin *(condicional a VN-07/VN-08)*
- **Objetivo**: BR-27 aplicada a Leads e Conversas.
- **Backend**: `BusinessHoursGuard`, `access_exceptions`, endpoints, auditoria.
- **Frontend**: aviso "fora do horário", tela de exceções do Admin.
- **Banco**: `access_exceptions`.
- **Testes**: dentro/fora do horário, com/sem exceção, expiração, isenção de Admin, isolamento.
- **Dependências**: F4.1; F4.6 para a parte de Conversas.
- **Decisões necessárias**: **VN-07, VN-08**; TD-05.
- **Aceite**: com restrição ligada, consultor fora do horário é bloqueado conforme a regra validada; exceção concedida libera e expira.
- **Fora**: qualquer alteração automática de status pelo horário (proibido por D-071).

### F4.8 — Ociosidade de atendimento de Cliente *(condicional a VN-13; pode ficar fora da aceitação da F4)*
- **Objetivo**: implementar a regra **depois** de definida.
- **Backend**: temporização (TD-06), transferência automática conforme regra, mensagens automáticas se previstas.
- **Frontend**: indicadores conforme regra.
- **Banco**: conforme regra (possivelmente nenhum).
- **Testes**: relógio simulado; "Só mais um momento"; **Lead nunca dispara**.
- **Dependências**: F4.2, F4.3, F4.6, P1.
- **Decisões necessárias**: **todos os itens de VN-13**, TD-06.
- **Aceite**: definido na especificação da regra.
- **Fora**: tudo até que a regra esteja documentada.

## 16. Dependências com a F5 e desacoplamento

### 16.1 O que a F5 espera consumir da F4
| Item | Fornecido em | Uso na F5 |
|---|---|---|
| `ConversationsService` (abrir/obter conversa por contato, anexar mensagem, atualizar status) e `MessagesService` | F4.6 | Ingestão de webhook e envio |
| `ContactResolutionService` | F4.6 | Identificador E.164 → Cliente/Lead |
| `EligibilityService` / distribuição por pool | F4.3, F4.6 | Atribuição de conversa nova |
| Disponibilidade e `business_hours` | F4.1–F4.2 | Elegibilidade e regras de horário |
| Timeline | F4.4 | Mensagens visíveis no histórico |
| Notificações | F4.5 | "Nova mensagem/conversa" |
| P1: contexto de tenant + ator Sistema | F4.1 | Webhook/worker sem JWT |
| Permissões `conversations:*` e escopo de visibilidade | F4.6 | RBAC das telas de WhatsApp |
| Contrato `ChannelAdapter` (já documentado em [architecture.md §4](../03-architecture/architecture.md); **não implementado na F4** — A2) | — | Implementação em F5.0 |

**A F5 adiciona (aditivo, sem alterar o núcleo)**: `channel_accounts`, `channel_webhook_events`, coluna `channel_account_id` em `conversations`, `message_templates`, `file_assets`/`attachment_id`, `WhatsAppAdapter`, filas e tempo real, reconciliação do legado (D-073) — conforme [whatsapp-architecture.md §9](../03-architecture/whatsapp-architecture.md).

### 16.2 A F5 fica desacoplada do CRM Core?
**Sim, se** (i) o núcleo não importar nada de WhatsApp (verificável por regra de lint/revisão), (ii) a F5 só falar com `conversations`/`distribution`/`availability` por serviços públicos, (iii) P1 existir antes (sem ele o webhook não consegue operar por tenant nem auditar), (iv) a integração for por `ChannelAccount`/tenant (D-074), sem configuração global. **Risco residual**: se a F4.6 migrar para a F5.0 (ajuste A1), a F5.0 fica maior — mitigado por já existirem os itens F4.1–F4.5.

## 17. Decisões técnicas necessárias (`TD-xx`)

| ID | Decisão | Proposta / opções | Quando |
|---|---|---|---|
| TD-01 | ~~Estado atual da disponibilidade~~ **Resolvida (Gate do F4.2, [D-077](../00-governance/decision-register.md#d-077--disponibilidade-modelo-de-dados-e-permissões-td-01-td-08))**: `user_availability` 1:1 + `availability_log` append-only; linha sob demanda; ausência = `INDISPONÍVEL`; mesma transação | — | — |
| TD-02 | Timeline: `UNION ALL` SQL × merge por fonte; cursor `(occurred_at, source, id)` | Medir no F4.4 | F4.4 |
| TD-03 | ~~`Conversation`: FKs dedicadas × polimórfico~~ **Resolvida (A3/D-076)**: FKs dedicadas | §11.4 | — |
| TD-04 | ~~Fuso horário: `Intl` × biblioteca~~ **Resolvida no F4.1**: `Intl` (sem dependência nova; validação do nome IANA e avaliador testados com relógio fixo, incl. horário de verão) | — | — |
| TD-05 | Exceções de acesso: tabela (recomendada) × chave em settings × permissão | §6.10 | F4.7 |
| TD-06 | Ociosidade: *delayed job* por conversa × varredura periódica | Após VN-13 | F4.8 |
| TD-07 | Entrega de notificação: polling (F4) × WebSocket (F5) | Polling | F4.5 |
| TD-08 | ~~Chaves de permissão~~ **Resolvida para a disponibilidade (Gate do F4.2)**: `availability:read|update|manage`, sem `availability:training`. A colisão com `messages:*` legado só importa no F4.6 | §7.4 | F4.6 (parte `messages`) |
| TD-09 | Unicidade de `external_message_id`: `(tenant, id)` × `(tenant, channel_type, id)` | Incluir `channel_type` | F4.6 |
| TD-10 | ~~Nome/escopo das chaves em `tenant_settings`~~ **Resolvida no F4.1**: `crm.business_hours` (objeto v1) e `crm.availability.enabled` (boolean) | — | — |
| TD-11 | Correção do cursor de justiça do Round Robin | §10 | F4.3 |
| TD-12 | Enums em Postgres × texto: migração de novos valores (canal, disponibilidade) | Enum para estados fechados (disponibilidade), texto para `channel_type`/`channel` | F4.2/F4.6 |
| TD-13 | ~~Momento de entrega do P1~~ **Resolvida no F4.1**: **não entregue** no F4.1 (sem consumidor nos F4.2–F4.5, VN-05); entra antes do F4.8 e da F5 | — | — |

## 18. Pendências de negócio (`VN-xx`) — situação após o F4.0

`VN-01` a `VN-05` foram **fechadas em 2026-10-05**. Todas as demais continuam **não decididas** — nenhuma resposta foi assumida.

| ID | Pergunta | Bloqueia |
|---|---|---|
| VN-01 | ✅ **DECIDIDO (F4.0)**: novo consultor inicia `INDISPONÍVEL` e precisa se colocar `DISPONÍVEL` manualmente; sem transição automática por login/logout na primeira implementação. *(Resíduo — usuários já existentes ao habilitar; inatividade — em `VN-17`.)* | — |
| VN-02 | ✅ **DECIDIDO (F4.0)**: tenant sem disponibilidade mantém o comportamento da Fase 3; o estado não é obrigatório | — |
| VN-03 | ✅ **DECIDIDO (F4.0)**: a carteira é mantida; sem redistribuição automática nem "retirar carteira" | — |
| VN-04 | ✅ **DECIDIDO (F4.0)** — D-075: **Lead sem proprietário é estado legítimo**; `owner_id` anulável; distribuição não obrigatória na criação. *(A política de atribuição posterior é `VN-16`.)* | — |
| VN-05 | ✅ **DECIDIDO (F4.0)**: consultor altera o próprio estado exceto Treinamento; Gestor/Admin *(= Admin e Gerente — Gate do F4.2)* colocam e retiram Treinamento; Sistema só futuramente, sem regras automáticas. *(Resíduos em `VN-17`.)* | — |
| VN-06 | BR-16: limite de Pausa, destinatário do alerta, se Almoço/Treinamento contam | F4.5 |
| VN-07 | `business_hours`: campos (dias, janelas, feriados), fuso, por tenant único ou por filial/equipe; restrição de acesso ligada por padrão? a quem, bloqueio total ou só escrita, isenção de Admin/gestor; efeito na distribuição | F4.1, F4.3, F4.7 |
| VN-08 | Liberação excepcional: por usuário/temporária/escopo, duração, motivo obrigatório, quem solicita | F4.7 |
| VN-09 | Interações manuais: catálogo de canais/resultados, direção, o que conta como "interação" para `lastInteractionAt`, editar/excluir, timeline do Cliente inclui histórico do Lead de origem, Tarefas/Compromissos entram na timeline | F4.4 |
| VN-10 | Visibilidade de interações/conversas: próprio × equipe × tenant (D-058 é tenant-only) | F4.4, F4.6 |
| VN-11 | Notificações: quais eventos, destinatários, canais | F4.5 |
| VN-12 | Conversa: contato desconhecido, associação/unicidade de conversa aberta, "finalizada" e disposição obrigatória (BR-15), transferência, reabertura, "claim", filas na F4 ou só F5, SLA (BR-18) | F4.6 |
| VN-13 | **Ociosidade** (todos os itens da §12) | F4.8 |
| VN-14 | Lead convertido: destino do vínculo das conversas/interações | F4.4, F4.6 |
| VN-15 | Renomeação dos papéis "Supervisor/Operador de Call Center" (D-070 pendência 5) | seed/UI |
| VN-16 | **Política de distribuição posterior de Leads sem proprietário** (D-075): se a criação/importação distribui automaticamente ou mantém sem proprietário (por tenant, origem ou opção de importação); como/quando são atribuídos depois (distribuição em lote, reivindicação pelo consultor, atribuição por Gestor); se haverá filtro/indicador de "sem proprietário" | F4.3 (parcial), incrementos futuros |
| VN-17 | ✅ **DECIDIDO (Gate do F4.2, 2026-10-05)** — 17.1 sem registro = `INDISPONÍVEL`; 17.2 Admin/Gerente só colocam/retiram terceiros de Treinamento; 17.3 Treinamento sem duração automática; 17.4 `manage`: admin/gerente, `read`: admin/gerente/supervisor/diretor, `update`: vendedor/backoffice (sem `operador`); 17.5 habilitar = `tenant_settings:update` (Admin). *Derivações `PROPOSTO` a confirmar em [D-077](../00-governance/decision-register.md#d-077--disponibilidade-modelo-de-dados-e-permissões-td-01-td-08).* | — |

## 19. Riscos

| # | Risco | Mitigação |
|---|---|---|
| R1 | Ao habilitar a disponibilidade todos iniciam `INDISPONÍVEL` (VN-01/VN-17.1): ninguém recebe Leads até se colocar `DISPONÍVEL` — Leads criados nesse intervalo ficam sem proprietário (**estado legítimo**, D-075) | Flag desligada por padrão (VN-02); o painel de gestão mostra quem está disponível (proposta F4.2/F4.3); sem regra nova |
| R2 | Ator "Sistema" e execução por tenant fora de HTTP não existem (K4) — **não bloqueiam o F4.2** (o Sistema não altera estados agora), mas bloqueiam a ociosidade (F4.8) e a F5 (webhook/worker) | P1 antes do F4.8/F5 (`TD-13`), com teste |
| R3 | Conversas com dado pessoal sob RBAC tenant-only (C8) | VN-10 antes de F4.6; não expor leitura sem escopo |
| R4 | Modelar `Message` sem canal real → retrabalho na F5 | Ajustes A1–A2 (F4.6 condicional e mínimo) |
| R5 | Colisão `messages:*` legado | TD-08 |
| R6 | Restrição por horário pode trancar usuários/Admin | Guard desligado por padrão; rota de settings isenta; exceção auditada |
| R7 | Cursor de timeline sobre união é complexo e pode ficar lento | TD-02 com medição; índices por fonte já existem |
| R8 | Race entre leitura de elegibilidade e atribuição (K5) | Ler dentro da `tx` após o lock; aceitar janela de ms |
| R9 | Migrações Prisma: índice parcial e evolução de enum exigem SQL manual | TD-01/TD-12; revisar migration à mão |
| R10 | Polling em vez de WebSocket aumenta carga | Intervalos ≥ 30 s; WebSocket só na F5 (D-013) |
| R11 | Formato de `business_hours` difícil de mudar depois | `schema_version` no valor |
| R12 | Fuso/DST/virada de dia geram bugs | Avaliador puro + relógio fixo nos testes |
| R13 | `lastInteractionAt` editável pela API contradiz um escritor de sistema | Decidir no F4.4 se o campo continua aceito |
| R14 | `resetDatabase` e a suíte e2e crescem e ficam lentas | Manter lista atualizada; paralelizar só com isolamento |
| R15 | Volume de mensagens (D-014) e LGPD (WA-27) | Fora da F4; registrado |
| R16 | Cenário "lista de centenas de Leads" (D-075): a importação sem `owner_id` hoje distribui tudo pelo round-robin se houver elegíveis (K8) | Documentado; tratamento depende de `VN-16`; não alterar sem decisão |
| R18 | Treinamento esquecido mantém o usuário fora da distribuição (sem duração automática — VN-17.3) | Painel mostra "desde quando"; remoção manual; nenhuma regra automática (decisão) |
| R19 | Tenants existentes não têm as chaves `availability:*` nos papéis de fábrica (papéis de sistema são imutáveis pela API) | Rodar o seed idempotente ou passo manual (D-059); coberto no plano de execução do F4.2 |
| R17 | Sem política posterior (`VN-16`), a carteira "sem proprietário" pode crescer sem mecanismo de escoamento (K9, K10) | Registrado como pendente; não inventar no F4.3; decidir antes de qualquer incremento que a implemente |

## 20. Critérios de aceite da Fase 4

1. Timeline única de leads, oportunidades e atendimentos manuais por entidade (critério do roadmap) — F4.4.
2. Disponibilidade com 5 estados, histórico, trava de Treinamento e auditoria — F4.2.
3. Distribuição de Leads respeita *ativo + Disponível + permissão* para **novos** Leads quando a flag do tenant está ligada, é **idêntica** à atual quando desligada, e **não** altera a carteira existente — F4.3.
4. `business_hours` configurável e auditado; nenhuma alteração automática de status — F4.1.
5. Isolamento de tenant e RBAC provados por teste em **todo** recurso novo.
6. Nada específico de canal no código da F4; Lead nunca tratado como Cliente.
7. Toda decisão dependente de negócio aplicada só após registrada no Decision Register.
8. `openapi.yaml`, `entities.md`, `relationships.md`, `business-rules.md`, `roadmap.md`, `workflows.md`, `personas.md` atualizados **antes** do código de cada incremento.
9. Itens condicionais (F4.6, F4.7, F4.8) só entram na aceitação se suas decisões (VN-12, VN-07/08, VN-13) tiverem sido fechadas; caso contrário são movidos com registro explícito (F5.0 / fase posterior).
10. **Lead sem proprietário** é suportado naturalmente (criação, listagem, atribuição manual posterior, conversão) e a indisponibilidade **não** retira nem redistribui a carteira existente (D-075, VN-03).

## 21. Documentação que precisará ser atualizada (a partir da aprovação)

| Documento | Alteração |
|---|---|
| decision-register.md | **Feito no F4.0**: D-071 (VN-01/02/03/05), D-075 (VN-04), D-076 (A1–A3), tabela de portões da F4. **Feito no Gate do F4.2**: D-071 (VN-17), D-077 (TD-01/TD-08). **Pendente**: demais `VN`/`TD` conforme forem decididas |
| entities.md / relationships.md | **Parcial no F4.0** (notas em `leads.owner_id` e `agent_status_log`; FKs de `conversations`). **Feito no Gate do F4.2**: `user_availability` e `availability_log` (substituem `agent_status_log`). **Pendente**: `conversations` (lead/opportunity, canal neutro, campos de ociosidade); `messages` (`sender_type`); `interactions`; `conversation_assignments`; `access_exceptions`; remover/marcar legado `queues/calls` conforme VN-12 |
| openapi.yaml | **Feito no Gate do F4.2**: rotas de disponibilidade da §7.1 (rascunho, marcadas "ainda não implementado"). **Pendente**: corrigir `Interaction.type` (remover `call`); documentar as demais rotas da §7 **antes** de cada código |
| business-rules.md | **Feito no F4.0 e no Gate do F4.2**: BR-14 (estado inicial, quem altera, tenant sem disponibilidade, carteira, Treinamento sem duração, sem registro, mecanismo desabilitado) e BR-29. **Pendente**: BR-05 (efeito do horário na distribuição — C5), BR-16 conforme VN-06; novas regras de conversa/ociosidade **somente** após VN-12/13 |
| requirements.md | **Feito no F4.0 e no Gate do F4.2**: RF-12, RF-15. **Pendente**: RF-16/18; seção Notificações |
| roadmap.md | **Feito no F4.0**: fronteira F4/F5 (D-076), estado do F4.0, Lead sem proprietário. **Pendente**: detalhar subincrementos F4.1–F4.8 conforme forem aprovados; reescrever a lista de funcionalidades da F5 |
| workflows.md / use-cases.md | **Feito no F4.0**: fluxo comercial §1 e UC-01 (Lead sem proprietário). **Feito no Gate do F4.2**: workflow §8 e UC-11 (alterar disponibilidade). **Pendente**: reescrever §2–4 e UC-05–07 como fluxos de conversa; novos casos (alterar status, registrar interação, fora do horário) |
| personas.md | Matriz sem "Call Center/Telefonia"; papéis (VN-15); escopo de visibilidade (VN-10) |
| whatsapp-architecture.md | **Feito no F4.0**: notas de status em §3 e no critério G7. **Pendente**: ajustar §4 e F5.0/F5.2 ao concluir a F4 |
| CLAUDE.md (spec) | "Estado atual" desatualizado (C9) — **não alterado** no F4.0 (fora do escopo pedido) |
| PROJECT-CONTEXT.md | A cada incremento |
| crm-frontend (código) | Rótulo "CRM + Call Center", comentário de `AuthUser.permissions` — **fora do escopo desta etapa** (nenhum código alterado) |
