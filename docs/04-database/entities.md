# Entidades

Convenções gerais (UUID, `tenant_id`, timestamps, soft delete) em [database.md](database.md) aplicam-se a toda entidade abaixo, salvo indicação contrária. Campo `id` (UUID, PK) e `tenant_id` (UUID, FK) são omitidos das tabelas individuais para não repetir, exceto onde a entidade **não** tem `tenant_id` (marcado explicitamente).

## Grupo: Tenancy e Acesso

### `tenants` *(sem tenant_id — é a raiz)*
| Campo | Tipo | Obrigatório | Notas |
|---|---|---|---|
| name | string | sim | Razão social/nome fantasia |
| document | string | sim | CNPJ |
| plan_id | UUID (FK plans) | sim | |
| status | enum(active, suspended, trial) | sim | |
| settings | jsonb | não | Configurações gerais (ver `tenant_settings` para chave-valor estruturado) |

Índices: `document` único. Relacionamentos: 1:N com praticamente todas as entidades via `tenant_id`.

### `plans` *(sem tenant_id)*
| Campo | Tipo | Obrigatório | Notas |
|---|---|---|---|
| name | string | sim | |
| limits | jsonb | sim | Limites contratados (usuários, filas, mensagens/mês etc.) |

### `branches` (filiais)
| Campo | Tipo | Obrigatório |
|---|---|---|
| name | string | sim |

### `teams` (equipes)
| Campo | Tipo | Obrigatório | Notas |
|---|---|---|---|
| name | string | sim | |
| branch_id | UUID (FK branches) | sim | |
| manager_id | UUID (FK users) | não | |

### `users`
| Campo | Tipo | Obrigatório | Notas |
|---|---|---|---|
| name | string | sim | |
| email | string | sim | Único por tenant |
| password_hash | string | sim | bcrypt/argon2 |
| status | enum(active, inactive) | sim | |
| team_id | UUID (FK teams) | não | |
| branch_id | UUID (FK branches) | não | |

Índices: `(tenant_id, email)` único. Regras: e-mail único por tenant, não globalmente (mesma pessoa pode existir em tenants diferentes com mesmo e-mail).

### `roles`
| Campo | Tipo | Obrigatório | Notas |
|---|---|---|---|
| name | string | sim | |
| is_system | boolean | sim | true = papel de fábrica (somente leitura para o tenant) |

### `permissions` *(sem tenant_id — catálogo global do sistema)*
| Campo | Tipo | Obrigatório | Notas |
|---|---|---|---|
| key | string | sim | Ex.: `leads:create` |
| module | string | sim | |

### `role_permissions` (associativa)
`role_id`, `permission_id`.

### `user_roles` (associativa)
`user_id`, `role_id`.

### `refresh_tokens`
| Campo | Tipo | Obrigatório | Notas |
|---|---|---|---|
| user_id | UUID (FK users) | sim | |
| token_hash | string | sim | Nunca texto puro |
| expires_at | timestamptz | sim | |
| revoked_at | timestamptz | não | |

## Grupo: CRM Core

### `customers` (clientes)
| Campo | Tipo | Obrigatório | Notas |
|---|---|---|---|
| name | string | sim | |
| document | string | não | CPF/CNPJ, usado para deduplicação (BR-07) |
| primary_phone | string (E.164) | não | |
| primary_email | string | não | |
| owner_id | UUID (FK users) | não | Responsável |
| tags | string[] | não | |
| custom_fields | jsonb | não | Ver [database.md](database.md) seção 6 |

Índices: `(tenant_id, document)`, `(tenant_id, primary_phone)`. Regras: BR-07, BR-08.

### `contacts`
| Campo | Tipo | Obrigatório | Notas |
|---|---|---|---|
| customer_id | UUID (FK customers) | sim | |
| name | string | sim | |
| phone | string | não | |
| email | string | não | |
| role | string | não | Cargo/relação com o cliente |

### `lead_sources`
| Campo | Tipo | Obrigatório |
|---|---|---|
| name | string | sim |

### `leads`
| Campo | Tipo | Obrigatório | Notas |
|---|---|---|---|
| customer_id | UUID (FK customers) | não | Preenchido ao vincular/converter |
| source_id | UUID (FK lead_sources) | sim | BR-03 |
| owner_id | UUID (FK users) | não | |
| status | enum(new, in_progress, qualified, disqualified, converted) | sim | |
| disqualify_reason | string | não | Obrigatório se status=disqualified (BR-06) |

Índices: `(tenant_id, status)`, `(tenant_id, owner_id)`.

### `pipelines`
| Campo | Tipo | Obrigatório |
|---|---|---|
| name | string | sim |
| is_default | boolean | sim |

### `stages` (etapas do pipeline)
| Campo | Tipo | Obrigatório | Notas |
|---|---|---|---|
| pipeline_id | UUID (FK pipelines) | sim | |
| name | string | sim | |
| order | integer | sim | |
| is_won | boolean | sim | |
| is_lost | boolean | sim | |

### `opportunities`
| Campo | Tipo | Obrigatório | Notas |
|---|---|---|---|
| customer_id | UUID (FK customers) | sim | |
| lead_id | UUID (FK leads) | não | Origem, se veio de um lead |
| pipeline_id | UUID (FK pipelines) | sim | BR-09 |
| stage_id | UUID (FK stages) | sim | BR-09 |
| owner_id | UUID (FK users) | sim | |
| value | numeric | não | Obrigatório conforme config do pipeline (BR-13) |
| status | enum(open, won, lost) | sim | Estado terminal won/lost (BR-11) |
| lost_reason | string | não | Obrigatório se status=lost (BR-12) |

Índices: `(tenant_id, owner_id, status)`, `(tenant_id, stage_id)`.

### `opportunity_stage_history`
| Campo | Tipo | Obrigatório | Notas |
|---|---|---|---|
| opportunity_id | UUID (FK opportunities) | sim | `ON DELETE CASCADE` |
| from_stage_id | UUID (FK stages) | não | |
| to_stage_id | UUID (FK stages) | sim | |
| changed_by | UUID (FK users) | sim | |
| changed_at | timestamptz | sim | Imutável (BR-10) |

### `notes`
| Campo | Tipo | Obrigatório | Notas |
|---|---|---|---|
| entity_type | enum(lead, customer, opportunity) | sim | Polimórfico controlado |
| entity_id | UUID | sim | |
| author_id | UUID (FK users) | sim | |
| content | text | sim | |

### `tasks`
| Campo | Tipo | Obrigatório | Notas |
|---|---|---|---|
| entity_type | enum(lead, customer, opportunity) | não | |
| entity_id | UUID | não | |
| assigned_to | UUID (FK users) | sim | |
| title | string | sim | |
| due_at | timestamptz | sim | |
| status | enum(pending, done, overdue) | sim | |

### `appointments` (agenda)
| Campo | Tipo | Obrigatório |
|---|---|---|
| entity_type | enum(lead, customer, opportunity) | não |
| entity_id | UUID | não |
| user_id | UUID (FK users) | sim |
| starts_at | timestamptz | sim |
| ends_at | timestamptz | sim |

## Grupo: Call Center

### `queues` (filas)
| Campo | Tipo | Obrigatório | Notas |
|---|---|---|---|
| name | string | sim | |
| channel_type | enum(voice, whatsapp) | sim | |
| sla_seconds | integer | não | BR-18 |

### `queue_members`
`queue_id`, `user_id`.

### `agent_status_log`
| Campo | Tipo | Obrigatório | Notas |
|---|---|---|---|
| user_id | UUID (FK users) | sim | |
| status | enum(available, busy, paused, offline) | sim | |
| started_at | timestamptz | sim | |
| ended_at | timestamptz | não | |

### `calls`
| Campo | Tipo | Obrigatório | Notas |
|---|---|---|---|
| queue_id | UUID (FK queues) | não | |
| customer_id | UUID (FK customers) | não | |
| agent_id | UUID (FK users) | não | |
| direction | enum(inbound, outbound) | sim | |
| status | enum(ringing, answered, missed, failed) | sim | |
| started_at | timestamptz | sim | |
| answered_at | timestamptz | não | |
| ended_at | timestamptz | não | |
| disposition_id | UUID (FK dispositions) | não | Obrigatório ao encerrar (BR-15) |
| recording_url | string | não | BR-17 |

Índices: `(tenant_id, agent_id)`, `(tenant_id, customer_id)`.

### `dispositions` (motivos de disposição, configurável por tenant/fila)
| Campo | Tipo | Obrigatório |
|---|---|---|
| queue_id | UUID (FK queues) | não |
| name | string | sim |

## Grupo: Omnichannel

### `conversations`
| Campo | Tipo | Obrigatório | Notas |
|---|---|---|---|
| customer_id | UUID (FK customers) | não | |
| channel_type | enum(whatsapp, email, sms) | sim | |
| queue_id | UUID (FK queues) | não | |
| status | enum(open, closed) | sim | |
| assigned_to | UUID (FK users) | não | |

### `messages`
| Campo | Tipo | Obrigatório | Notas |
|---|---|---|---|
| conversation_id | UUID (FK conversations) | sim | |
| direction | enum(inbound, outbound) | sim | |
| content | text | não | |
| attachment_id | UUID (FK file_assets) | não | |
| external_message_id | string | não | Chave de idempotência (BR-20) |
| status | enum(pending, sent, delivered, read, failed) | sim | |

Índices: `(tenant_id, external_message_id)` único quando presente.

### `message_templates`
| Campo | Tipo | Obrigatório |
|---|---|---|
| name | string | sim |
| channel_type | enum(whatsapp) | sim |
| content | text | sim |

## Grupo: Campanhas

### `campaigns`
| Campo | Tipo | Obrigatório |
|---|---|---|
| name | string | sim |
| type | enum(call, whatsapp) | sim |
| status | enum(draft, running, finished) | sim |

### `campaign_targets`
| Campo | Tipo | Obrigatório |
|---|---|---|
| campaign_id | UUID (FK campaigns) | sim |
| customer_id | UUID (FK customers) | sim |
| status | enum(pending, done, failed) | sim |

## Grupo: Sistema

### `notifications`
| Campo | Tipo | Obrigatório |
|---|---|---|
| user_id | UUID (FK users) | sim |
| type | string | sim |
| payload | jsonb | sim |
| read_at | timestamptz | não |

### `file_assets`
| Campo | Tipo | Obrigatório |
|---|---|---|
| owner_id | UUID (FK users) | sim |
| entity_type | string | não |
| entity_id | UUID | não |
| storage_key | string | sim |
| mime_type | string | sim |
| size_bytes | integer | sim |

### `audit_log` *(imutável, sem soft delete, sem update)*
| Campo | Tipo | Obrigatório |
|---|---|---|
| user_id | UUID (FK users) | não |
| action | string | sim |
| entity_type | string | sim |
| entity_id | UUID | não |
| payload | jsonb | não |
| created_at | timestamptz | sim |

### `tenant_settings`
| Campo | Tipo | Obrigatório |
|---|---|---|
| key | string | sim |
| value | jsonb | sim |

Índices: `(tenant_id, key)` único.

---

Esta lista cobre o MVP e o roadmap próximo (ver [../10-roadmap/roadmap.md](../10-roadmap/roadmap.md)). Entidades de Billing e IA (módulos futuros) não são modeladas aqui — serão adicionadas quando essas fases forem iniciadas.
