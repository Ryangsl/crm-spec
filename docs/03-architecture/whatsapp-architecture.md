# WhatsApp — Discovery e Arquitetura de Referência (Fase 5)

> **Natureza deste documento**: discovery e planejamento técnico/arquitetural. **Não autoriza implementação.** Nenhum código, migration, endpoint, componente, dependência ou integração é criado por ele. A implementação só pode começar quando o **[Gate de entrada](#10-gate-de-entrada-para-implementação)** estiver integralmente atendido.
>
> **Base**: [D-072](../00-governance/decision-register.md#d-072--whatsapp-é-uma-frente-própria-fase-5-núcleo-de-conversas-agnóstico-ao-canal-fase-4) (escopo e fronteira) e [D-073](../00-governance/decision-register.md#d-073--módulo-communications-implementado-fora-da-especificação-whatsapp-outbound-e-automações) (divergência com o código existente). Levantamento feito em 2026-09-30 sobre o `crm-spec`, o `crm-backend` e o `crm-frontend` reais.
>
> **Convenção**: `DEFINIDO` = já decidido/documentado (com a origem). `PROPOSTO` = proposta técnica deste documento, ainda **não aprovada**. `PENDENTE` = decisão necessária, **não inventada aqui**. Regras de negócio nunca são deduzidas — o que não está documentado aparece como `PENDENTE`.

## 1. Contexto

O CRM Universal terá integração com o **WhatsApp oficial**, configurada **por tenant** ([D-074](../00-governance/decision-register.md#d-074--integração-de-whatsapp-configurada-por-tenant-por-conta-de-canal-wa-02)). Por ser uma frente grande e de alto impacto arquitetural (canal externo, tempo real, mídia, filas, compliance de plataforma de terceiro), ela **não** é tratada como uma feature da Fase 4:

- **Fase 4 — Atendimento/Conversas**: núcleo de Conversas/Mensagens, disponibilidade e distribuição, **agnóstico ao canal**.
- **Fase 5 — WhatsApp**: a frente específica do canal.
- **Fase 6 — Omnichannel**: novos canais sobre o mesmo núcleo, sem mudança estrutural.

> **WA-02 — resolvido no princípio ([D-074](../00-governance/decision-register.md#d-074--integração-de-whatsapp-configurada-por-tenant-por-conta-de-canal-wa-02))**: cada tenant possui **sua própria configuração** de integração de WhatsApp, que pode variar conforme o negócio. O modelo admite tenant **sem** WhatsApp, com **um** número, com **múltiplos** números/contas, e configurações **diferentes** entre tenants. O CRM **não assume** WhatsApp global da plataforma, credencial global, número único para todos os tenants nem quantidade fixa de números por tenant. Não foi decidido (fica na F5): quantidade máxima, onboarding, UI de configuração, modelo comercial, provedor/BSP e armazenamento definitivo de secrets. O código legado (credenciais globais por ambiente) **diverge** desse princípio — ver [D-073](../00-governance/decision-register.md#d-073--módulo-communications-implementado-fora-da-especificação-whatsapp-outbound-e-automações).

## 2. Estado atual encontrado

### 2.1 crm-spec (documentação)

| Tema | O que existe | Observação |
|---|---|---|
| Produto | [D-070](../00-governance/decision-register.md#d-070--definição-de-produto-crm-comercial--atendimentoconversas--whatsapp-sem-call-center-telefônico): WhatsApp é canal de conversa; sem telefonia | Fase 5 = WhatsApp/Conversas |
| Abstração de canal | `ChannelAdapter` ([architecture.md §4](architecture.md), [integrations.md §1](integrations.md), RF-22) com `sendMessage`, `receiveWebhook`/`handleWebhook`, `sendTemplate`, `getMedia` | Interface só descrita; **não existe no código** |
| Provedor | [D-011](../00-governance/decision-register.md#d-011--provedor-de-whatsapp) `ADIADO`: API oficial ou BSP oficial; não oficial só POC | Falta escolher **qual** (Cloud API direta vs. BSP) |
| Webhook | [integrations.md §5](integrations.md), [security.md §7](security.md): validar assinatura → persistir payload bruto → normalizar → idempotência → enfileirar | Padrão definido |
| Regras | BR-19 (mensagem → Conversa → Cliente/Lead), BR-20 (idempotência por `external_message_id`), BR-21 (retry com backoff, status "Falha" visível) | Definidas |
| Modelo de dados | `conversations`, `messages`, `message_templates`, `file_assets`, `queues`, `queue_members`, `dispositions`, `agent_status_log`, `notifications` ([entities.md](../04-database/entities.md)) | **Nenhuma existe no `schema.prisma`**; `agent_status_log` é legado com 4 estados (D-071 fechou 5) |
| Disponibilidade | [D-071](../00-governance/decision-register.md#d-071--disponibilidade-de-consultoratendente-para-distribuição-automática): 5 estados, só *Disponível* recebe distribuição, global por usuário, `business_hours` não altera status | Regras fechadas; implementação na Fase 4 |
| Lead x Cliente | BR-28 | Lead não é Cliente |
| Tempo real | [D-013](../00-governance/decision-register.md#d-013--websocket) `ADIADO` p/ Fase 5; polling obrigatório como fallback (RNF-04) | |
| Fila | Redis + BullMQ ([D-012](../00-governance/decision-register.md#d-012--redis--bullmq), ADR-006); retry com backoff + dead-letter (RNF-06) | |
| Segredos | [D-024](../00-governance/decision-register.md#d-024--convenção-de-variáveis-de-ambiente-de-provedores) e [D-025](../00-governance/decision-register.md#d-025--secrets-management-em-produção) `PROPOSTO`; [security.md](security.md): nunca em texto puro no banco | |
| OpenAPI | Só `GET /customers/{id}/interactions` (schema `Interaction`) | **Sem** `/conversations`, `/messages`, `/whatsapp`, `/webhooks`, `/automations` |
| Referências desatualizadas | `integrations.md §3`, `workflows.md §5` e `use-cases.md` UC-08 diziam "Fase 6" para WhatsApp | Corrigidas junto deste documento (a fase é a 5, [D-070](../00-governance/decision-register.md#d-070--definição-de-produto-crm-comercial--atendimentoconversas--whatsapp-sem-call-center-telefônico)) |

### 2.2 crm-backend (código real)

| Tema | Estado real |
|---|---|
| Módulo `communications` | **Existe** (commit `3ed66f2`, anterior à F3.6): regras de automação (`birthday`/`inactivity`/`campaign`) + envio de **template** WhatsApp **somente outbound**. **Não coberto pela spec** — ver [D-073](../00-governance/decision-register.md#d-073--módulo-communications-implementado-fora-da-especificação-whatsapp-outbound-e-automações) |
| Provider | `MetaWhatsAppProvider` (Meta Cloud API direta) atrás de `WhatsAppProvider { sendTemplate() }` — **só** `sendTemplate`; não é o `ChannelAdapter` da spec |
| Credenciais | `WHATSAPP_PHONE_NUMBER_ID` / `WHATSAPP_ACCESS_TOKEN` / `WHATSAPP_API_VERSION` **globais por variável de ambiente**, iguais para todos os tenants; nada por tenant — **diverge de [D-074](../00-governance/decision-register.md#d-074--integração-de-whatsapp-configurada-por-tenant-por-conta-de-canal-wa-02)** |
| Modelo | `whatsapp_messages` (ligada a `customer_id`, `template_name`, status `queued|sent|failed`) e `automation_rules`. Sem conversa, sem direção, sem `delivered/read`, sem conteúdo livre |
| Fila | BullMQ `whatsapp`; job `send-template` com 5 tentativas e backoff exponencial (5 s); job repetido `scan-automations` a cada 1 h |
| Inbound | **Inexistente**: sem controller de webhook, sem verificação de assinatura, sem `rawBody` habilitado no bootstrap, sem status de entrega |
| API | `GET/POST /v1/automations`, `PATCH /:id`, `POST /:id/run`, `DELETE /:id`; `GET/POST /v1/whatsapp/messages`. Permissões `automations:*` e `messages:create|read` já no seed |
| Testes | 1 unit (`communications.service.spec.ts`) e 1 e2e (cria automação); envio real não é exercitado |
| Conversation/Message/Interações | **Não existem**. Não há módulo `interactions` (o endpoint do OpenAPI não está implementado) |
| Disponibilidade / `business_hours` | Não implementadas. `RoundRobinService` só emite aviso quando `crm.business_hours` existe (formato indefinido) |
| Base reutilizável | `TenantContextStorage` + JWT; `RequirePermissions`; `AuditService.record(input, tx)` (`userId` do contexto); `TenantSettings` (chave/valor por tenant); BullMQ/Redis já configurados (`QueueModule`); padrão Controller→Service→Repository; soft delete; `RoundRobinService`/`UsersService.listActiveIdsWithPermission` (ativo + permissão) como base da distribuição; `Customer.primaryPhone` (E.164 validado no DTO), `Lead.phone`, `Contact.phone` |
| Lacunas de infraestrutura | Rota pública (`@Public()`) **não preenche** `TenantContextStorage` (`get()` falha por desenho) → webhook precisa de caminho próprio de resolução de tenant; `rawBody` não habilitado; sem rate limit/throttling; sem armazenamento de arquivos (`file_assets` inexistente); sem WebSocket; sem circuit breaker |

### 2.3 crm-frontend (código real)

Features existentes: `auth`, `customers`, `leads`, `opportunities`, `follow-up`, `status`. **Nenhuma** tela/serviço de WhatsApp, automações, conversas ou disponibilidade; sem cliente WebSocket; sem seletor de usuário (decisão F3.6). Tudo do frontend de conversas é trabalho novo.

## 3. Fronteira arquitetural F4 × F5 × F6

> **Estado**: `PROPOSTO` — depende de aprovação explícita (item do Gate). O texto atual do roadmap lista "Conversas, Mensagens, Templates" na Fase 5; esta proposta move o **núcleo agnóstico** para a Fase 4 e mantém na Fase 5 apenas o que é específico do canal.

| Capacidade | F4 — Atendimento/Conversas (agnóstico) | F5 — WhatsApp (específico do canal) | F6 — Omnichannel |
|---|---|---|---|
| Conversation / Message (modelo normalizado) | ✅ cria | usa | usa |
| Ciclo de vida da conversa (abrir, atribuir, transferir, encerrar, reabrir, disposição) | ✅ | usa | usa |
| Identidade de contato por canal (identificador normalizado ↔ Customer/Lead) | ✅ estrutura genérica | ✅ regra E.164 do WhatsApp | ✅ e-mail/SMS |
| Disponibilidade (D-071) e distribuição (elegibilidade ativo + Disponível + permissão + `business_hours`) | ✅ | aplica a conversas WhatsApp | aplica |
| `business_hours` (configuração do tenant e regra de acesso) | ✅ | usa | usa |
| Ociosidade de atendimento de Cliente (BR-28) | ✅ (incremento próprio) | usa | usa |
| Notificações (primeira versão) e linha do tempo / Interações | ✅ | mensagens aparecem na linha do tempo | idem |
| Interface `ChannelAdapter` + registro de adapters | ✅ define a interface e um adapter de teste/"manual" | ✅ `WhatsAppAdapter` | ✅ novos adapters |
| Conta/número do canal, credenciais, webhook, assinatura, tenant-por-`phone_number_id` | — | ✅ | ✅ (por canal) |
| Janela de 24 h, templates aprovados, categorias, opt-in/opt-out | — | ✅ | — |
| Mídia/anexos do WhatsApp (download, armazenamento, tipos) | — (só o `attachment_id` no modelo) | ✅ | ✅ (por canal) |
| Envio assíncrono, retry por classe de erro, circuit breaker do provedor | — | ✅ ([D-039](../00-governance/decision-register.md#d-039--circuit-breaker-para-provedores-externos)) | ✅ |
| Tempo real (WebSocket + polling) e painel de supervisão | — | ✅ ([D-013](../00-governance/decision-register.md#d-013--websocket)) | usa |
| Caixa de entrada unificada multicanal | — | — | ✅ |

**Regra de fronteira**: nenhum módulo da F4 (nem do CRM core) importa código de WhatsApp. O núcleo só conhece `ChannelAdapter` e o modelo normalizado; o WhatsApp entra como *plugin* registrado (RF-22, [integrations.md §1](integrations.md)).

**Regra de fronteira (tenant)**: o núcleo do CRM **não depende de configuração global de WhatsApp**. A integração é orientada **por tenant e por conta de canal configurada** (`ChannelAccount`, §6.9); um tenant sem nenhuma conta usa o núcleo normalmente ([D-074](../00-governance/decision-register.md#d-074--integração-de-whatsapp-configurada-por-tenant-por-conta-de-canal-wa-02)).

## 4. O que a Fase 4 precisa fornecer para o WhatsApp

Pré-requisitos que a F5 **consome** e que, sem eles, o WhatsApp não pode começar:

1. **Modelo `Conversation` e `Message` normalizado**, com `channel_type` extensível, `direction`, `status` (`pending|sent|delivered|read|failed`), `external_message_id` único por tenant (BR-20), `assigned_to`, `attachment_id` opcional, ligação a Customer **ou** Lead (BR-19, BR-28) — e opcional a Opportunity (`PENDENTE` WA-07).
2. **Ciclo de vida**: abertura, atribuição, transferência, encerramento (com disposição, BR-15), reabertura — com regras de negócio fechadas (`PENDENTE` WA-13, WA-14).
3. **Disponibilidade (D-071)**: estado corrente por usuário + histórico; permissões (Treinamento só Gestor/Sistema).
4. **Motor de distribuição** generalizado a partir do `RoundRobinService`: elegibilidade *ativo + Disponível + permissão* (+ `business_hours` quando configurado), reutilizável para Lead e Conversa; comportamento "nenhum elegível" definido (`PENDENTE` WA-10).
5. **`business_hours`**: formato, configuração administrativa por tenant, regra de acesso fora do horário e liberação excepcional do Admin (BR-27; detalhes técnicos `PENDENTE` WA-11/WA-12).
6. **Interface `ChannelAdapter`** (contrato e registro) e um adapter de teste que permita provar o núcleo sem provedor real.
7. **Módulo de Interações / linha do tempo** (`GET /customers/{id}/interactions`) para receber mensagens/conversas (RF-18).
8. **Notificações (primeira versão)** — "nova conversa atribuída" precisa de um destino.
9. **Escopo de visibilidade de conversas** por consultor (WA-24) — hoje o RBAC é tenant-only ([D-058](../00-governance/decision-register.md#d-058--escopo-de-rbac-na-fase-2-e-na-fase-3-apenas-tenant)).
10. **Identidade de contato genérica**: resolução `identificador de canal → Customer/Lead` com tratamento de múltiplos candidatos (mesmo espírito de [D-067](../00-governance/decision-register.md#d-067--deduplicação-de-customer-é-bloqueante-409): nunca escolher automaticamente).
11. **Não estender o módulo `communications` legado**: ele permanece congelado ([D-073](../00-governance/decision-register.md#d-073--módulo-communications-implementado-fora-da-especificação-whatsapp-outbound-e-automações)); a F4 **não** acrescenta WhatsApp nele nem o usa como base do núcleo. A reconciliação é escopo da **F5.0**.

## 5. O que pertence exclusivamente à Fase 5

- Escolha do provedor/BSP e criação de conta de teste/sandbox ([D-011](../00-governance/decision-register.md#d-011--provedor-de-whatsapp)).
- Modelo e configuração da **conta do canal** por tenant (`ChannelAccount`, 0..N por tenant: número, provider, credenciais/secrets, segredo de webhook, status) — [D-074](../00-governance/decision-register.md#d-074--integração-de-whatsapp-configurada-por-tenant-por-conta-de-canal-wa-02).
- **Reconciliação do módulo `communications` legado** com a nova arquitetura (F5.0): decidir o que é reutilizado, migrado, refatorado ou substituído ([D-073](../00-governance/decision-register.md#d-073--módulo-communications-implementado-fora-da-especificação-whatsapp-outbound-e-automações)).
- `WhatsAppAdapter` (implementação do `ChannelAdapter`).
- Endpoint público de webhook (verificação de desafio, assinatura sobre o corpo bruto, resolução de tenant).
- Persistência do payload bruto e pipeline de ingestão (inbound e status de entrega).
- Envio: mensagens livres dentro da janela de 24 h, templates fora dela, mapeamento de erros do provedor → retry/falha (BR-21).
- Catálogo de templates (sincronização/aprovação/variáveis/categoria) — `message_templates`.
- Mídia: download (URLs do provedor expiram), armazenamento, tipos/limites, áudio.
- Opt-in/opt-out e política de consentimento do canal.
- Limites e qualidade da API do provedor (throughput, limites de mensageria, custo por categoria) — **verificar na documentação vigente do provedor no momento da implementação**; este documento não fixa valores.
- WebSocket com fallback de polling e painel de supervisão ([D-013](../00-governance/decision-register.md#d-013--websocket), RF-19).
- Circuit breaker e timeout do provedor ([D-039](../00-governance/decision-register.md#d-039--circuit-breaker-para-provedores-externos), RNF-05).
- Observabilidade específica do canal (filas, taxa de falha, latência de webhook).

## 6. Arquitetura de referência (F5) — `PROPOSTO`

### 6.1 Módulos e responsabilidades

| Módulo | Fase | Responsabilidade | Depende de |
|---|---|---|---|
| `conversations` | F4 | Conversa: ciclo de vida, atribuição, transferência, encerramento/reabertura, disposição | `customers`, `leads`, `users`, `audit` |
| `messages` | F4 | Persistência de mensagens normalizadas e máquina de estados de status | `conversations` |
| `availability` | F4 | Estado corrente + histórico do consultor (D-071) | `users` |
| `distribution` | F4 | Elegibilidade e escolha do responsável (generaliza `RoundRobinService`) | `availability`, `users`, `tenant-settings` |
| `channels` | F4 (interface) / F5 (contas) | `ChannelAdapter`, registro de adapters, conta do canal por tenant | — |
| `whatsapp` | F5 | `WhatsAppAdapter`, controller de webhook, processors de ingestão/envio/mídia, templates | `channels`, `conversations`, `messages` |
| `communications` (existente) | a reconciliar | Automações outbound + `whatsapp_messages` — destino definido por D-073 | — |

Comunicação entre módulos: chamada direta de serviço público (síncrona) ou evento de domínio interno (side effects), conforme [architecture.md §7](architecture.md). Eventos já previstos: `message.received`, `message.sent`, `message.failed`, `agent.status_changed`; propostos: `conversation.opened|assigned|transferred|closed`.

### 6.2 Entidades (todas `PROPOSTO` — modelo a validar no Gate)

| Entidade | Origem | Notas |
|---|---|---|
| `conversations`, `messages` | [entities.md](../04-database/entities.md) | `channel_type` hoje `enum(whatsapp,email,sms)` — a F4 precisa de valor neutro/extensível; ligação a Lead além de Customer; `closed_at`, motivo/disposição |
| `message_templates` | entities.md | Precisa de status de aprovação, idioma, categoria, variáveis (`PENDENTE` WA-20) |
| `file_assets` | entities.md | Mídia; armazenamento `PENDENTE` WA-19 |
| `queues`, `queue_members`, `dispositions` | entities.md (legado D-070) | Existência de "filas" na F4 ou só F5 continua `PENDENTE` (D-070 item 4) |
| disponibilidade (estado corrente + `agent_status_log`) | D-071 | Enum precisa refletir os 5 estados; nomenclatura neutra |
| `channel_accounts` (`ChannelAccount`) | **nova** — avaliada sob [D-074](../00-governance/decision-register.md#d-074--integração-de-whatsapp-configurada-por-tenant-por-conta-de-canal-wa-02): mantida como proposta | Conta de canal **por tenant, cardinalidade 0..N** (sem máximo definido): canal, provider, configuração, número/identificador externo (ex.: `phone_number_id`), status e **referência** a secrets (nunca o segredo em texto puro). Conversas/mensagens referenciam a conta pela qual trafegam (vínculo genérico; conta concreta é F5) |
| `channel_webhook_events` | **nova** | Payload bruto + assinatura verificada + estado de processamento, para reprocessamento/auditoria ([integrations.md §5](integrations.md)) |
| `whatsapp_messages`, `automation_rules` | **existentes no schema** | Ver D-073 — coexistência/migração `PENDENTE` |

### 6.3 Integrações externas

WhatsApp Business Platform (Cloud API direta **ou** BSP — `PENDENTE` WA-01). Saída: HTTPS com **timeout curto** (RNF-05) e, na F5, circuit breaker ([D-039](../00-governance/decision-register.md#d-039--circuit-breaker-para-provedores-externos)). Entrada: webhook HTTPS público do provedor.

### 6.4 Filas (BullMQ, [D-012](../00-governance/decision-register.md#d-012--redis--bullmq))

Cada fila só existe com necessidade real ([architecture.md §6](architecture.md)). A F5 justifica: `whatsapp-inbound` (consumo de webhook), `whatsapp-outbound` (envio), `whatsapp-media` (download). Jobs carregam **apenas ids internos** e recuperam o tenant do registro persistido (padrão já usado). Retry com backoff exponencial **por classe de erro** (erro permanente do provedor não é reenfileirado), dead-letter visível, chave de idempotência em todo job com efeito externo.

### 6.5 Fluxo — mensagem recebida

```
Provedor ──POST──▶ /v1/webhooks/whatsapp  (rota pública; corpo bruto preservado)
  1. valida assinatura sobre o corpo bruto            └─ inválida → 401, nada persistido além de log
  2. resolve a channel_account pelo identificador externo (uma das N contas de algum tenant) → define o tenant (sem JWT)
  3. persiste payload bruto (channel_webhook_events)  → responde 200 rápido
  4. enfileira whatsapp-inbound
Worker:
  5. idempotência por external_message_id             └─ duplicada → descarta (BR-20)
  6. normaliza (ChannelAdapter) → Message normalizada
  7. identifica contato (E.164 → Customer/Lead)       └─ 0 candidatos: WA-06 · N candidatos: WA-05
  8. resolve/abre Conversation                        (regra de associação: WA-07)
  9. persiste Message + evento message.received
 10. atribui responsável via distribution             (elegibilidade D-071; "nenhum elegível": WA-10)
 11. notifica/tempo real; audita
```

### 6.6 Fluxo — mensagem enviada

```
Consultor ─▶ POST /v1/conversations/{id}/messages
  1. RBAC + tenant + é responsável/tem escopo (WA-24) + conversa em estado que permite envio
  2. conta de canal = a da conversa (envio sai pela mesma conta) · janela de 24 h aberta? → texto livre; senão → exige template (WA-17/WA-20)
  3. cria Message(status=pending) + chave de idempotência → enfileira whatsapp-outbound
Worker:
  4. adapter.sendMessage/sendTemplate (timeout curto) → grava external_message_id
  5. erro transitório → retry com backoff · erro permanente/esgotou → status=failed visível (BR-21)
Webhook de status:
  6. sent → delivered → read/failed, aplicados de forma monotônica (eventos fora de ordem não regridem o estado)
```

### 6.7 Pontos de falha

| Ponto | Efeito | Mitigação proposta |
|---|---|---|
| Provedor indisponível/lento | Envio trava/atrasa | Timeout curto, circuit breaker (F5), fila com retry; sistema segue operando (RNF-05) |
| Webhook duplicado / reentregue | Mensagem duplicada | Idempotência por `external_message_id` (BR-20) + payload bruto persistido |
| Eventos de status fora de ordem | Status regride | Ordem de estados monotônica |
| Worker cai entre "provedor aceitou" e "gravei o id" | **Reenvio duplicado** no retry | Gravar intenção antes; reconciliar por id/idempotência do envio (WA-16/WA-17) — hoje o código existente **tem** essa janela |
| Assinatura de webhook inválida ou segredo rotacionado | Mensagens rejeitadas | Rotação documentada (D-025), alerta de taxa de rejeição |
| Tenant não resolvido no webhook | Mensagem sem dono / vazamento | Falhar fechado: sem `channel_account` conhecido → descarta e alerta; nunca "adivinhar" tenant |
| Ninguém elegível (todos indisponíveis / fora do horário) | Conversa sem responsável | Estado "não atribuída" explícito (análogo a D-069) — regra `PENDENTE` WA-10 |
| Redis indisponível | Filas param | Webhook já persistiu o bruto → reprocessável; monitorar fila |
| Número bloqueado/qualidade baixa | Perda do canal | Opt-in, limites por tenant, revisão de templates (WA-21/WA-22) |
| WebSocket cai | Painel sem tempo real | Polling de fallback (RNF-04) |

### 6.8 Fronteiras com o core do CRM

- O core (Customers/Leads/Opportunities/Follow-up) **não** conhece WhatsApp. Ele vê apenas `Conversation`/`Message` normalizadas e a linha do tempo.
- Tenant vem **sempre** do contexto autenticado ou, no webhook/worker, de `channel_account`/registro persistido — nunca de payload do provedor nem de DTO ([D-002](../00-governance/decision-register.md#d-002--estratégia-de-multi-tenancy)).
- Auditoria de eventos de sistema (webhook/worker) grava `userId = null` (o schema permite) — convenção `PENDENTE` WA-23.

### 6.9 Integração orientada por tenant e por conta de canal

Orientação arquitetural **conceitual** ([D-074](../00-governance/decision-register.md#d-074--integração-de-whatsapp-configurada-por-tenant-por-conta-de-canal-wa-02)) — sem schema nem código:

```
Tenant
└── ChannelAccount            (0..N por tenant)
    ├── channel = whatsapp
    ├── provider
    ├── configuração
    ├── credenciais/secrets   (referência; nunca texto puro no banco)
    ├── número
    └── status
```

| Cenário | Comportamento esperado |
|---|---|
| Tenant sem WhatsApp | Núcleo (conversas, disponibilidade, distribuição, follow-up) funciona normalmente; nenhuma rota de WhatsApp é exigida |
| Tenant com uma conta | Webhook resolve conta → tenant; envio usa a credencial daquela conta |
| Tenant com várias contas | Cada conversa fica associada à conta pela qual trafega; segredos, limites e status são **por conta** |
| Tenants diferentes | Configuração, provider e credenciais independentes; nenhuma credencial ou número compartilhado entre tenants |

Implicações: (i) o tenant do webhook vem da conta resolvida, nunca do payload; (ii) fila, limites e observabilidade devem poder ser segmentados por tenant e por conta; (iii) `ChannelAdapter` é instanciado **por conta** (provider + credenciais da conta), não como singleton global; (iv) nenhuma variável de ambiente global de WhatsApp é fonte de credenciais em produção multi-tenant. Detalhes de cardinalidade máxima, onboarding, UI e armazenamento de secrets: F5 (WA-02/WA-03).

## 7. Catálogo de decisões

### 7.1 Já definidas (`DEFINIDO`)

| Tema | Decisão | Origem |
|---|---|---|
| Escopo | Produto é CRM Comercial + Atendimento/Conversas + WhatsApp; sem telefonia | D-070 |
| Fronteira de fases | F4 agnóstica ao canal; F5 = WhatsApp; F6 = Omnichannel; nada implementado agora | D-072 |
| Provedor | Oficial (Cloud API ou BSP oficial); não oficial só POC | D-011 (direção) |
| Abstração | Toda comunicação passa por `ChannelAdapter` | RF-22, architecture §4 |
| Webhook | Validar assinatura → persistir bruto → normalizar → idempotência → enfileirar | integrations §5, security §7 |
| Idempotência | `external_message_id`, único por tenant | BR-20, entities.md |
| Vínculo | Mensagem → Conversa → Cliente/Lead por identificador de canal | BR-19 |
| Falha de envio | Retry com backoff; "Falha" visível ao usuário | BR-21, RNF-06 |
| Janela/Template | Mensagem ativa fora da janela de 24 h exige template | integrations §3 |
| Disponibilidade | 5 estados; só *Disponível* recebe distribuição; global; `business_hours` não altera status | D-071 |
| Lead x Cliente | Lead não é Cliente; ociosidade é de atendimento de Cliente | D-071, BR-28 |
| Tempo real | WebSocket na F5 com fallback de polling | D-013, RNF-04 |
| Fila | BullMQ; sem filas desnecessárias | D-012, ADR-006 |
| Segredos | Nunca em texto puro no banco | security §5 |
| Integração por tenant (WA-02) | Cada tenant tem sua própria configuração de WhatsApp (sem/1/N contas; configurações distintas); sem WhatsApp global, credencial global, número único ou quantidade fixa; integração isolada por tenant e por conta de canal | D-074 |
| Módulo legado `communications` | Congelado: sem evolução funcional, sem apagar/refatorar agora, sem duplicar WhatsApp nele; reconciliação na F5.0 | D-073 |
| Isolamento | `tenant_id` derivado do contexto, nunca do cliente | D-002, BR-01/02 |
| Exclusão | Soft delete; auditoria imutável | BR-22/23/24 |
| Timeout | Timeout curto desde a primeira integração; circuit breaker na F5 | RNF-05, D-039 |
| Número desconhecido (texto histórico) | "vira lead/atendimento avulso até vinculação manual" — texto pré-D-070, **não validado** contra BR-28 | use-cases UC-08 (tratar como `PENDENTE` WA-06) |

### 7.2 Pendentes — `PENDENTE` / DECISÃO NECESSÁRIA

`Dono`: fase que precisa decidir. **Nenhuma resposta foi assumida.**

| ID | Tema | Pergunta / lacuna | Dono | Tipo |
|---|---|---|---|---|
| WA-01 | Provedor/API oficial | Cloud API direta ou qual BSP? critérios de escolha; custo | F5 | Negócio + técnica |
| WA-02 | Configuração de WhatsApp por tenant | **Princípio decidido ([D-074](../00-governance/decision-register.md#d-074--integração-de-whatsapp-configurada-por-tenant-por-conta-de-canal-wa-02))**: cada tenant tem sua própria configuração (sem WhatsApp / um número / múltiplas contas; configurações distintas). **Permanece PENDENTE (F5)**: quantidade máxima, onboarding, UI de configuração, modelo comercial, qual conta inicia uma conversa ativa quando há várias | F5 (o modelo da F4 já respeita o princípio) | Negócio — princípio ✅ · detalhes pendentes |
| WA-03 | Credenciais | Forma definitiva de armazenamento dos secrets **por conta de canal** (criptografia em repouso × cofre — nunca credencial global, [D-074](../00-governance/decision-register.md#d-074--integração-de-whatsapp-configurada-por-tenant-por-conta-de-canal-wa-02)); rotação; revisão de D-024/D-025 (`WHATSAPP_*` global não serve como fonte por tenant) | F5 | Técnica + negócio |
| WA-04 | Webhook | Verificação de desafio, assinatura, resolução do tenant a partir do identificador do número, rate limit do endpoint | F5 | Técnica |
| WA-05 | Identificação do contato | Regra de match (Customer.primaryPhone, Contact.phone, Lead.phone); múltiplos candidatos; quem decide | F4/F5 | Negócio |
| WA-06 | Contato desconhecido | Cria Lead? Cliente? conversa sem vínculo? Qual `LeadSource`? Compatível com BR-28? | F4/F5 | **Negócio** |
| WA-07 | Associação da conversa | Uma conversa aberta por contato+canal? Lead que vira Cliente migra a conversa? Vínculo com Oportunidade? | F4 | Negócio |
| WA-08 | Responsável | Conversa nova de cliente existente vai ao dono do cliente/lead ou à distribuição? | F4 | Negócio |
| WA-09 | Distribuição | Critério de escolha e prioridade; existência de filas (D-070 item 4) | F4 | Negócio |
| WA-10 | Consultor indisponível / ninguém elegível | Conversa em andamento e conversa nova: fila, mensagem automática, transferência, alerta? (D-071 adiou) | F4 | **Negócio** |
| WA-11 | Horário comercial / fora do horário | Formato de `business_hours`; mensagem recebida fora do horário: enfileira, responde automático, ignora? | F4 | Negócio |
| WA-12 | Exceções | Mecanismo de liberação excepcional do Admin (BR-27) — detalhes técnicos | F4 | Técnica + negócio |
| WA-13 | Transferência | Quem transfere, para quem, motivo obrigatório, histórico, efeito em SLA/ociosidade | F4 | Negócio |
| WA-14 | Encerramento/reabertura | O que é "finalizada" (BR-15, D-070 item 1); disposição obrigatória; nova mensagem reabre ou abre nova conversa? | F4 | **Negócio** |
| WA-15 | Ociosidade | Regra de 5 min (só Cliente): eventos que reiniciam, próximo consultor, mensagens automáticas | F4 | Negócio (D-071) |
| WA-16 | Idempotência | Dedupe de eventos de status; chave de envio; reconciliação após falha parcial | F5 | Técnica |
| WA-17 | Envio | Quem envia; texto livre × template; máquina de estados; classificação de erros (retry × falha definitiva) | F5 | Técnica + negócio |
| WA-18 | Retry/falhas/DLQ | Nº de tentativas e intervalos (o código atual usa 5 × 5 s exp., sem decisão registrada); visibilidade da DLQ; alerta | F5 | Técnica |
| WA-19 | Mídia/anexos | Tipos e tamanhos aceitos; armazenamento (não existe `file_assets`); download de URLs expiráveis; áudio; varredura; retenção | F5 | Técnica + negócio |
| WA-20 | Templates | Cadastro/sincronização/aprovação, variáveis, categoria, quem gerencia (o código atual envia por nome, sem catálogo) | F5 | Técnica + negócio |
| WA-21 | Limites da API | Throughput, limites de mensageria por qualidade do número, custo por categoria — **conferir documentação vigente** | F5 | Técnica |
| WA-22 | Opt-in / opt-out | Consentimento para mensagens ativas/automações (política do canal + LGPD); registro do consentimento | F5 | **Negócio/jurídico** |
| WA-23 | Auditoria | Eventos auditáveis (envio, transferência, encerramento, acesso excepcional); conteúdo de mensagem no `audit_log`? `userId` de eventos de sistema | F4/F5 | Negócio + técnica |
| WA-24 | Segurança / permissões | Permissões (`conversations:*`, `messages:*`); **escopo de visibilidade** (consultor vê só as suas? — RBAC hoje é tenant-only, D-058); PII em logs; segredo de webhook | F4/F5 | **Negócio + técnica** |
| WA-25 | Observabilidade | Métricas/alertas de fila, falha, latência de webhook; correlação por tenant/conversa | F5 | Técnica |
| WA-26 | Multi-tenancy operacional | Rate limit e cota por tenant; isolamento de fila (ruído entre tenants) | F5 | Técnica |
| WA-27 | LGPD / retenção | **Não há requisito documentado de retenção** de conteúdo de mensagem/mídia; D-047 pendente; exclusão de titular × soft delete | F4/F5 | **Negócio/jurídico** |
| WA-28 | Tempo real | Quem recebe o quê por WebSocket; formato de eventos; multi-instância ([D-046](../00-governance/decision-register.md#d-046--adapter-redis-para-websocket-multi-instância)) | F5 | Técnica |
| WA-29 | Notificações | Canal de notificação de "nova conversa/mensagem" (primeira versão de Notificações, "quando definida") | F4 | Negócio |
| WA-30 | Módulo existente | **Congelado** (D-073). Na F5.0: decidir o que é reutilizado, migrado, refatorado ou substituído | F5.0 | Técnica + negócio |

**Decisões que pertencem à F4**: WA-05 (estrutura), WA-06 (regra), WA-07 a WA-15, WA-23 (parte), WA-24 (escopo de visibilidade), WA-27 (parte), WA-29. **Exclusivamente F5**: WA-01 a WA-04, WA-16 a WA-22, WA-25, WA-26, WA-28. O princípio de WA-02 ([D-074](../00-governance/decision-register.md#d-074--integração-de-whatsapp-configurada-por-tenant-por-conta-de-canal-wa-02)) já orienta o modelo de dados da F4; WA-30 (D-073) só é reconciliado na F5.0 e não bloqueia o modelo da F4, desde que a F4 não estenda o módulo legado.

## 8. Riscos e gaps encontrados

| # | Achado | Severidade | Onde |
|---|---|---|---|
| 1 | **Módulo `communications` implementado fora da spec**: integração real com WhatsApp e automações existem, apesar de D-015 (integração real de WhatsApp e engine de automação **fora do MVP**), D-011 `ADIADO`, regra do `crm-backend/CLAUDE.md` ("não adicionar módulo de fase futura") e Fase 8 = Automações. Sem decisão, OpenAPI, entities.md ou testes de envio | **Alta** | D-073 |
| 2 | **Credenciais globais no código legado**: um único número/token para todos os tenants, contra [D-074](../00-governance/decision-register.md#d-074--integração-de-whatsapp-configurada-por-tenant-por-conta-de-canal-wa-02) — risco de envio sob identidade errada e violação de isolamento entre tenants enquanto o módulo existir. Mitigação decidida: módulo **congelado** (D-073) e reconciliado na F5.0 | **Alta** | D-074 / WA-03 |
| 3 | **Sem timeout** na chamada ao provedor (`fetch` sem `AbortSignal`) — contraria RNF-05 ("desde a primeira integração"); um provedor lento pode segurar o worker | Alta | `whatsapp.provider.ts` |
| 4 | **Janela de envio duplicado**: se o provedor aceita e o `UPDATE` falha (ou o worker cai), o retry reenvia; sem chave de idempotência no envio | Alta | `CommunicationsService.deliver` |
| 5 | **Sem opt-in/opt-out nem cota**: automações varrem até 5.000 clientes por regra a cada hora e disparam templates; risco de spam, queda de qualidade e bloqueio do número; sem rate limit por tenant | Alta | WA-22, WA-26 |
| 6 | **Modelo divergente**: `whatsapp_messages` (cliente + template, `queued|sent|failed`) não representa inbound, conteúdo livre, `delivered/read` nem conversa; coexistir com `messages` duplicaria o conceito | Média | D-073 |
| 7 | **Sem auditoria de envio** (BR-23): só criação/edição/exclusão de regras são auditadas; envios não | Média | `send()` |
| 8 | **`last_interaction_at` nunca é atualizado por interação**: só é gravado se o cliente da API enviar o valor; o gatilho `inactivity` cai no fallback `updatedAt`, o que distorce o resultado. Ociosidade/linha do tempo precisam de escritor real | Média | `customers`, F4 |
| 9 | **Interações/linha do tempo inexistentes** apesar do endpoint no OpenAPI; a F5 depende dela (RF-18) | Média | F4 |
| 10 | **Webhook sem base de infraestrutura**: rota pública não tem tenant; `rawBody` não habilitado (necessário à assinatura); sem throttling; sem `file_assets` | Média | bootstrap / common |
| 11 | **Visibilidade de conversas**: RBAC é tenant-only (D-058), mas personas definem que o vendedor não vê registros de outros; conversas exigem decisão | Média | WA-24 |
| 12 | **`business_hours` sem formato**; distribuição por disponibilidade e regra de acesso fora do horário dependem dele | Média | D-071, WA-11 |
| 13 | **UC-08 pré-D-070**: "número não vinculado vira lead/atendimento avulso" não foi validado contra Lead x Cliente | Média | WA-06 |
| 14 | `WHATSAPP_API_VERSION` sem default: falha só no primeiro envio, não na subida | Baixa | `env.validation.ts` |
| 15 | Referências "Fase 6" para WhatsApp na spec (corrigidas neste passo) | Baixa | docs |
| 16 | Frontend sem nenhuma base de conversas, tempo real ou seletor de usuário | Info | crm-frontend |

## 9. Incrementos propostos para a Fase 5 — somente planejamento

> Numeração provisória. Cada incremento só inicia após o Gate e a aprovação do anterior. Todos herdam os padrões consolidados (tenant isolation, RBAC, soft delete, auditoria, OpenAPI, testes).

### F5.0 — Reconciliação e fundação do canal
- **Objetivo**: **reconciliar o módulo `communications` legado** com a nova arquitetura (reutilizar, migrar, refatorar ou substituir — [D-073](../00-governance/decision-register.md#d-073--módulo-communications-implementado-fora-da-especificação-whatsapp-outbound-e-automações)); implementar o `ChannelAdapter` real e a conta de canal por tenant ([D-074](../00-governance/decision-register.md#d-074--integração-de-whatsapp-configurada-por-tenant-por-conta-de-canal-wa-02)).
- **Backend**: `channels` (interface, registro, `channel_accounts`), decisão de destino do `communications`; timeout no provedor; `rawBody` para rotas de webhook.
- **Frontend**: UI administrativa de configuração/estado das contas do tenant — escopo a definir (WA-02: onboarding e UI não decididos).
- **Banco**: `channel_accounts`; ajustes de `whatsapp_messages` conforme D-073.
- **API**: CRUD/estado de conta do canal (contrato no OpenAPI antes do código).
- **Integrações**: conta de teste/sandbox do provedor.
- **Testes**: unit do adapter (provedor simulado); e2e de isolamento entre tenants da conta do canal.
- **Dependências**: Gate; WA-01, WA-03, WA-30 e os detalhes pendentes de WA-02 (máximo de contas, onboarding).
- **Conclusão**: nenhum segredo em texto puro no banco; envio existente ou migrado, ou explicitamente adiado; adapter passa em testes com provedor simulado.

### F5.1 — Webhook e ingestão bruta
- **Objetivo**: receber eventos do provedor com segurança e sem perda.
- **Backend**: controller público de webhook, verificação de desafio e assinatura, resolução de tenant, `channel_webhook_events`, fila `whatsapp-inbound` (ainda sem criar conversa).
- **Frontend**: nenhum.
- **Banco**: `channel_webhook_events`.
- **API**: `GET/POST /v1/webhooks/whatsapp` (contrato documentado).
- **Integrações**: webhook configurado no provedor de teste.
- **Testes**: assinatura inválida rejeitada; reentrega não duplica (BR-20); tenant desconhecido falha fechado; payload bruto persistido.
- **Dependências**: F5.0; WA-04, WA-16.
- **Conclusão**: reentrega de webhook comprovadamente idempotente; nada é processado de forma síncrona na requisição.

### F5.2 — Mensagem recebida → Conversa
- **Objetivo**: transformar evento em `Message` associada a `Conversation`, Customer/Lead e responsável.
- **Backend**: normalização, identificação de contato, associação, atribuição via `distribution` (F4), eventos.
- **Frontend**: caixa de conversas do consultor (lista + detalhe), leitura; polling.
- **Banco**: apenas o que a F4 já criou + ajustes validados no Gate.
- **API**: leitura de conversas/mensagens (contrato já da F4).
- **Testes**: contato conhecido, desconhecido e ambíguo; indisponibilidade de todos; isolamento entre tenants.
- **Dependências**: F4 completa (núcleo, disponibilidade, distribuição); WA-05 a WA-10.
- **Conclusão**: UC-08 (recebimento) executável ponta a ponta; regras de WA-05/06/10 implementadas conforme validadas.

### F5.3 — Envio e status de entrega
- **Objetivo**: consultor responde; ciclo `pending → sent → delivered → read/failed`.
- **Backend**: `whatsapp-outbound`, classificação de erros, retry por classe, chave de idempotência, webhook de status monotônico, DLQ visível.
- **Frontend**: composição/envio, indicadores de status, falha visível e reenvio.
- **API**: `POST /v1/conversations/{id}/messages`.
- **Testes**: janela de 24 h; retry esgotado → falha visível (BR-21); provedor lento (timeout); envio sem duplicar após falha parcial.
- **Dependências**: F5.2; WA-17, WA-18.
- **Conclusão**: falha de envio visível após esgotar retries; sem duplicidade em cenário de falha parcial.

### F5.4 — Templates e mensagem ativa
- **Objetivo**: mensagem fora da janela via template aprovado.
- **Backend**: `message_templates`, sincronização/estado de aprovação, variáveis; reconciliação com as automações existentes (D-073).
- **Frontend**: seleção de template com variáveis.
- **Testes**: fora da janela exige template; template não aprovado é recusado.
- **Dependências**: F5.3; WA-20, WA-22.
- **Conclusão**: envio ativo apenas com template válido e base de consentimento definida.

### F5.5 — Mídia e anexos
- **Objetivo**: enviar/receber imagem, documento, áudio.
- **Backend**: `whatsapp-media`, armazenamento (`file_assets`), validação de tipo/tamanho (RNF-10).
- **Frontend**: pré-visualização, upload, player de áudio.
- **Testes**: tipo/tamanho inválidos; URL expirada do provedor; acesso a arquivo respeita tenant.
- **Dependências**: F5.3; WA-19, WA-27.
- **Conclusão**: mídia baixada e servida com isolamento de tenant e sem execução direta do arquivo.

### F5.6 — Tempo real, notificações e supervisão
- **Objetivo**: WebSocket com fallback e painel de supervisão.
- **Backend**: gateway WebSocket por tenant (token de curta duração), eventos; notificações.
- **Frontend**: cliente WebSocket + polling de fallback, painel de disponibilidade/filas (RF-19).
- **Testes**: **fallback de polling com WebSocket desligado** (critério do roadmap); isolamento de canal por tenant.
- **Dependências**: F5.2; D-013; WA-28, WA-29.
- **Conclusão**: nenhuma função crítica depende exclusivamente do WebSocket (RNF-04).

### F5.7 — Endurecimento
- **Objetivo**: prontidão para produção.
- **Backend**: circuit breaker (D-039), cotas/rate limit por tenant, métricas/alertas, política de retenção/exclusão (LGPD).
- **Testes**: carga do pipeline de webhook; degradação com provedor fora; exclusão de titular.
- **Dependências**: F5.1–F5.6; WA-21, WA-25, WA-26, WA-27; D-047.
- **Conclusão**: falha do provedor não derruba o restante (RNF-05); indicadores de fila/falha visíveis.

## 10. Gate de entrada para implementação

**A implementação do WhatsApp (F5) somente poderá começar quando todos os itens abaixo estiverem atendidos, com evidência registrada no `crm-spec` e aprovação explícita do responsável pelo produto.**

| # | Critério | Evidência exigida | Situação (2026-09-30) |
|---|---|---|---|
| G1 | **Arquitetura definida** | Este documento aprovado, com os `PROPOSTO` das seções 3 e 6 promovidos a `DECIDIDO` | ❌ não atendido — só proposta |
| G2 | **Modelo de dados validado** | `entities.md`/`relationships.md` atualizados (conversas/mensagens agnósticas, `channel_accounts`, `channel_webhook_events`, disponibilidade, destino de `whatsapp_messages`) e aprovados | ❌ não atendido |
| G3 | **Fluxos definidos** | `workflows.md` §5 e UC-08 reescritos com os fluxos 6.5/6.6 validados (incl. contato desconhecido, sem elegível, fora do horário) | ❌ não atendido |
| G4 | **Regras de negócio validadas** | WA-05 a WA-15, WA-22 e WA-27 respondidas pelo responsável pelo produto e refletidas em `business-rules.md` | ❌ não atendido |
| G5 | **Decisões críticas registradas** | WA-03, WA-24 e demais pendências do catálogo 7.2 aplicáveis resolvidas no Decision Register (WA-02: princípio ✅ em [D-074](../00-governance/decision-register.md#d-074--integração-de-whatsapp-configurada-por-tenant-por-conta-de-canal-wa-02); detalhes na F5; WA-30 na F5.0) | ❌ não atendido |
| G6 | **Provedor/API definido** | D-011 `DECIDIDO` (WA-01), conta de teste/sandbox disponível, D-024/D-025 revistas | ❌ não atendido |
| G7 | **Fronteira F4/F5 aprovada** | Seção 3 aprovada; roadmap atualizado ([D-072](../00-governance/decision-register.md#d-072--whatsapp-é-uma-frente-própria-fase-5-núcleo-de-conversas-agnóstico-ao-canal-fase-4)) | ❌ não atendido |
| G8 | **F4 concluída no que a F5 consome** | Itens 1–10 da seção 4 entregues e aceitos | ❌ não atendido (F4 não iniciada) |
| G9 | **Módulo legado sob controle (D-073)** | Congelamento registrado e respeitado (✅ 2026-09-30); reconciliação executada na F5.0 | 🟡 parcial — congelamento decidido; reconciliação é escopo da F5.0 |
| G10 | **OpenAPI antes do código** | Contratos de F5.0/F5.1 documentados em `openapi.yaml` | ❌ não atendido |

**O Gate continua FECHADO.** Enquanto qualquer item estiver ❌: **não** criar migration, endpoint, componente, dependência nem integração de WhatsApp. O módulo existente permanece congelado (D-073) — sem novas funcionalidades e sem duplicar WhatsApp nele; qualquer alteração exige decisão explícita.

## 11. Documentos relacionados

[D-070](../00-governance/decision-register.md#d-070--definição-de-produto-crm-comercial--atendimentoconversas--whatsapp-sem-call-center-telefônico) · [D-071](../00-governance/decision-register.md#d-071--disponibilidade-de-consultoratendente-para-distribuição-automática) · [D-072](../00-governance/decision-register.md#d-072--whatsapp-é-uma-frente-própria-fase-5-núcleo-de-conversas-agnóstico-ao-canal-fase-4) · [D-073](../00-governance/decision-register.md#d-073--módulo-communications-implementado-fora-da-especificação-whatsapp-outbound-e-automações) · [integrations.md](integrations.md) · [architecture.md](architecture.md) · [security.md](security.md) · [business-rules.md](../02-business/business-rules.md) · [roadmap.md](../10-roadmap/roadmap.md) · [entities.md](../04-database/entities.md) · [workflows.md](../02-business/workflows.md) · [use-cases.md](../01-product/use-cases.md)
