# Arquitetura Geral

Decisões formalizadas em ADRs: [../adr/](../adr/). Este documento descreve a arquitetura resultante.

## 1. Visão geral

```
                         ┌───────────────────────┐
   crm-frontend (PWA) ──▶│   API Gateway/Nginx    │
                         └───────────┬───────────┘
                                     ▼
                     ┌───────────────────────────────┐
                     │      crm-backend (NestJS)      │
                     │  Monólito modular              │
                     │  ┌─────────┐  ┌──────────────┐ │
                     │  │ Módulos │  │  Shared/Infra │ │
                     │  └─────────┘  └──────────────┘ │
                     └───┬───────────────┬────────────┘
                         ▼               ▼
                 ┌───────────────┐  ┌──────────┐
                 │ PostgreSQL    │  │  Redis    │
                 │ (dados)       │  │ (cache/   │
                 └───────────────┘  │ filas/ws) │
                                     └────┬──────┘
                                          ▼
                                 ┌──────────────────┐
                                 │  Workers (BullMQ) │
                                 └────────┬──────────┘
                                          ▼
                     ┌───────────────────────────────────┐
                     │ Adaptadores de canal (abstração)   │
                     │  Telefonia | WhatsApp | E-mail/SMS │
                     └───────────────┬─────────────────────┘
                                     ▼
                       Provedores externos (telefonia, WABA, etc.)
```

O backend é um **monólito modular** (ADR-003): um único processo/deploy, mas com fronteiras internas de módulo bem definidas (comunicação interna via services/eventos, nunca acesso direto ao repositório de outro módulo), permitindo extração futura de serviços sem reescrita completa.

## 2. Módulos do sistema

Cada módulo é uma pasta em `src/modules/<nome>` no backend, com controllers, services, repositories e DTOs próprios (ver [../07-backend/backend-architecture.md](../07-backend/backend-architecture.md)).

| Módulo | Objetivo | Entidades principais | Depende de | Eventos gerados | Riscos |
|---|---|---|---|---|---|
| Autenticação | Login, sessão, tokens | Session, RefreshToken | Usuários | `user.logged_in`, `user.logged_out` | Vazamento de token, brute force |
| Usuários | Cadastro e papéis de usuário | User, Role, Permission | Tenants | `user.created`, `user.role_changed` | Escalonamento indevido de privilégio |
| Empresas/Tenants | Ciclo de vida do tenant | Tenant, Plan, Branch (filial) | — | `tenant.created`, `tenant.suspended` | Vazamento cross-tenant |
| Clientes | Cadastro único do cliente | Customer, Contact | Tenants | `customer.created`, `customer.merged` | Duplicidade de cadastro |
| Leads | Captação e qualificação | Lead, LeadSource | Clientes, Usuários | `lead.created`, `lead.qualified`, `lead.lost` | Distribuição injusta/perda de lead |
| Oportunidades | Negociação comercial | Opportunity | Leads, Clientes, Pipeline | `opportunity.created`, `opportunity.stage_changed`, `opportunity.won`, `opportunity.lost` | Dados de receita incorretos |
| Pipeline | Configuração de funil | Pipeline, Stage | Tenants | `pipeline.updated` | Mudança de pipeline quebrar oportunidades em andamento |
| Atendimentos | Registro de interação | Interaction | Clientes, Call Center, Messaging | `interaction.created` | Histórico incompleto |
| Call Center | Operação de voz | Call, AgentStatus, Queue | Telefonia, Filas | `call.started`, `call.ended`, `agent.status_changed` | Indisponibilidade do provedor |
| Telefonia | Integração com provedor de voz | ProviderConfig, CallLog | Call Center | `call.provider_event` | Acoplamento a um único provedor |
| Filas | Distribuição de atendimento | Queue, QueueMember | Usuários | `queue.member_joined`, `queue.sla_breached` | Fila mal dimensionada |
| Discadores | Modo de discagem | DialingList (pós-MVP) | Call Center | `dial.attempted` | Complexidade de compliance (preditivo) |
| WhatsApp | Canal de mensageria | Conversation, Message | Messaging | `message.received`, `message.sent`, `message.failed` | Bloqueio/banimento pelo provedor |
| Agenda | Compromissos | Appointment | Usuários, Clientes | `appointment.created`, `appointment.reminder` | Conflito de horário |
| Tarefas | Follow-up e pendências | Task | Usuários | `task.created`, `task.completed`, `task.overdue` | Tarefas esquecidas sem alerta |
| Campanhas | Ações comerciais em massa | Campaign, CampaignTarget | Leads, Messaging | `campaign.started`, `campaign.finished` | Envio em massa mal configurado (spam) |
| Relatórios | Consolidação analítica | ReportSnapshot (materializações) | Todos | `report.generated` | Consulta pesada degradar produção |
| Dashboard | Indicadores em tempo real/quase real | — (leitura agregada) | Relatórios | — | Dados desatualizados sem indicação |
| Notificações | Avisos ao usuário | Notification | Todos | `notification.created` | Ruído/excesso de notificação |
| Arquivos | Anexos | FileAsset | Todos | `file.uploaded` | Upload malicioso |
| Auditoria | Trilha de ações | AuditLog | Todos | `audit.recorded` | Volume de dados/custo de retenção |
| Configurações | Parâmetros do tenant | TenantSetting | Tenants | `setting.updated` | Configuração inconsistente entre módulos |
| Billing/Planos *(futuro)* | Cobrança da plataforma | Subscription, Invoice | Tenants | `invoice.created` | Fora do MVP |
| IA *(futuro)* | Recursos de IA no produto | — | Vários | — | Fora do MVP |

Permissões por módulo seguem a matriz de [../01-product/personas.md](../01-product/personas.md); regras de negócio detalhadas por módulo estão em [../02-business/business-rules.md](../02-business/business-rules.md).

## 3. Atendimento e disponibilidade (legado "Call Center")

> **Nota de escopo ([D-070](../00-governance/decision-register.md#d-070--definição-de-produto-crm-comercial--atendimentoconversas--whatsapp-sem-call-center-telefônico), 2026-09-21)**: o produto não é um Call Center telefônico. Os conceitos de voz desta seção e os módulos "Call Center", "Telefonia" e "Discadores" da tabela de módulos (chamadas, discagem, gravação, eventos `call.*`, `TelephonyAdapter`) estão **fora de escopo**. Permanecem como conceitos reaproveitáveis para atendimento/conversas: status de disponibilidade ([D-071](../00-governance/decision-register.md#d-071--disponibilidade-de-consultoratendente-para-distribuição-automática)), filas de atendimento, disposição e SLA (BR-15/BR-18). O texto original é mantido por rastreabilidade e deve ser revisado antes da implementação.

### 3.1 Conceitos modelados
Status de operador (`Disponível`, `Ocupado`, `Pausa`, `Offline`), tempos (pausa, atendimento, ocioso), transferência, conferência, callback, disposição de chamada, gravação, SLA de fila e métricas — ver definição de dados em [../04-database/entities.md](../04-database/entities.md).

### 3.2 Modos de discagem — análise *(fora de escopo — D-070)*

| Modo | Descrição | Complexidade | Decisão |
|---|---|---|---|
| Registro manual de atendimento | Operador liga por fora e registra a interação no sistema | Nenhuma (não há telefonia) | **MVP** ([D-015](../00-governance/decision-register.md#d-015--escopo-oficial-do-mvp)) |
| Manual | Operador disca número a partir da tela | Baixa | **Fase 5** |
| Click-to-call | Discagem originada por um clique no CRM, sem digitar número | Baixa/Média | **Fase 5** |
| Preview Dialer | Sistema mostra o registro antes de discar, operador confirma | Média | Pós-Fase 5 |
| Power Dialer | Sistema disca automaticamente o próximo da lista ao encerrar o atual | Média/Alta | Pós-Fase 5 |
| Predictive Dialer | Sistema disca múltiplos números antecipando disponibilidade de operador (pacing algorítmico) | Alta (+ requisitos legais de abandono de chamada) | Fora do roadmap inicial ([D-045](../00-governance/decision-register.md#d-045--discador-preditivo), `ADIADO` — pós-Fase 5, mediante validação de negócio) |

**Justificativa**: o MVP do produto não integra telefonia — entrega o histórico unificado do cliente com registro manual de atendimento, sem depender de nenhum provedor externo ([D-015](../00-governance/decision-register.md#d-015--escopo-oficial-do-mvp)). Quando a Fase 5 iniciar, o MVP *de telefonia* é manual + click-to-call: cobre atendimento receptivo em fila e discagem ativa individual sem exigir motor de pacing, reduzindo risco técnico e de compliance. A escolha do provedor ([D-010](../00-governance/decision-register.md#d-010--provedor-de-telefonia)) está `ADIADO` até a Fase 5 e não bloqueia as Fases 1 a 4.

## 4. Omnichannel — camada de abstração

O CRM nunca fala diretamente com a API de um provedor específico. Toda comunicação passa por uma interface interna `ChannelAdapter`:

```
interface ChannelAdapter {
  sendMessage(conversation, payload): Promise<ChannelSendResult>
  handleWebhook(rawPayload): NormalizedMessage
}
```

Cada provedor implementa esse contrato. Se a telefonia voltar ao escopo (hoje fora — D-070), a mesma ideia se aplicaria sob o nome `TelephonyAdapter` (`ProviderAAdapter`, `AsteriskAdapter`, etc.). O restante do sistema (Conversas, Mensagens, filas de atendimento) trabalha apenas com o modelo normalizado interno, o que permite trocar/adicionar provedor sem alterar regras de negócio. Nenhum provedor concreto é escolhido agora ([D-010](../00-governance/decision-register.md#d-010--provedor-de-telefonia) e [D-011](../00-governance/decision-register.md#d-011--provedor-de-whatsapp), `ADIADO`) — ver [integrations.md](integrations.md).

## 5. Tempo real (WebSocket)

[D-013](../00-governance/decision-register.md#d-013--websocket) (`ADIADO` para a **Fase 5**): WebSocket não é implementado na Fase 1. Os casos que o exigem — status de disponibilidade dos atendentes, estado de filas de atendimento, conversa em andamento, supervisão em tempo real — só existem a partir da Fase 5. O MVP não depende de tempo real.

Quando a Fase 5 chegar, a forma é:

- Canal: WebSocket (namespace por tenant), autenticado via token de curta duração emitido após autenticação HTTP.
- **Fallback obrigatório**: se a conexão cair ou não for suportada, o frontend recorre a polling do mesmo recurso (intervalo maior, ex. 5-10s) — nenhuma funcionalidade crítica depende exclusivamente de WebSocket (RNF-04).

## 6. Processamento assíncrono (filas)

Redis + BullMQ é a solução padrão de fila ([ADR-006](../adr/ADR-006.md), [D-012](../00-governance/decision-register.md#d-012--redis--bullmq), `DECIDIDO`). Candidatos naturais a processamento assíncrono: envio de mensagens, importação de leads, processamento de gravação, relatórios pesados, notificações, consumo de webhooks, integrações externas e futuramente IA.

**Regra de contenção**: não criar filas desnecessárias no MVP. A infraestrutura existe desde a Fase 1, mas cada fila só é criada quando houver necessidade real — a operação permanece síncrona enquanto o processamento couber na requisição sem prejudicar a experiência. No MVP, o caso concreto que justifica fila é a importação de leads em lote (CSV).

- **Retry**: backoff exponencial, limite de tentativas configurável por tipo de job.
- **Dead-letter**: jobs que esgotam tentativas vão para uma fila de falhas, visível para operação/observabilidade — nunca descartados silenciosamente.
- **Idempotência**: todo job que tem efeito externo (enviar mensagem, originar chamada) usa uma chave de idempotência para evitar duplicação em reprocessamento.
- **Observabilidade**: métricas de tamanho de fila, taxa de falha e tempo de processamento expostas (ver [../03-architecture/scalability.md](scalability.md) e [../09-testing/testing-strategy.md](../09-testing/testing-strategy.md)).

## 7. Comunicação interna entre módulos

Módulos não acessam o repositório/tabela de outro módulo diretamente. Comunicação é feita via:
1. **Chamada de serviço direta** (mesmo processo) quando é uma dependência síncrona forte e simples (ex.: Oportunidades lê dados de Clientes).
2. **Eventos de domínio internos** (event emitter in-process, podendo evoluir para fila) quando o efeito é um "side effect" desacoplado (ex.: `lead.qualified` dispara notificação, não é a Notificação que pergunta a cada segundo se um lead foi qualificado).

Isso mantém o monólito modular e evita o acoplamento que inviabilizaria uma extração futura de serviço (ADR-003).
