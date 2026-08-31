# Relacionamentos

Visão de alto nível dos relacionamentos entre as entidades definidas em [entities.md](entities.md). Cardinalidade: `1:N` (um para muitos), `N:N` (muitos para muitos via tabela associativa).

## 1. Tenancy e Acesso

```
tenants 1───N branches
tenants 1───N teams
tenants 1───N users
teams   1───N users        (users.team_id)
branches 1───N teams
teams   N───1 users         (teams.manager_id → users)

users   N───N roles         (via user_roles)
roles   N───N permissions   (via role_permissions)
users   1───N refresh_tokens
plans   1───N tenants
```

## 2. CRM Core

```
customers 1───N contacts
customers 1───N leads
customers 1───N opportunities
lead_sources 1───N leads
users(owner) 1───N leads
users(owner) 1───N opportunities
leads     1───1 opportunities   (opcional: lead pode não gerar oportunidade; opportunity pode não vir de lead)

pipelines 1───N stages
pipelines 1───N opportunities
stages    1───N opportunities
opportunities 1───N opportunity_stage_history
stages    1───N opportunity_stage_history (from_stage_id / to_stage_id)

notes  N───1 (lead | customer | opportunity)   [polimórfico via entity_type/entity_id]
tasks  N───1 (lead | customer | opportunity)   [polimórfico, opcional]
tasks  N───1 users (assigned_to)
appointments N───1 (lead | customer | opportunity) [polimórfico, opcional]
appointments N───1 users
```

## 3. Call Center

```
queues 1───N calls
queues N───N users        (via queue_members)
users  1───N agent_status_log
users  1───N calls (agent_id)
customers 1───N calls
queues 1───N dispositions
dispositions 1───N calls
```

## 4. Omnichannel

```
customers 1───N conversations
queues    1───N conversations
users     1───N conversations (assigned_to)
conversations 1───N messages
file_assets 1───N messages (attachment_id)
```

## 5. Campanhas

```
campaigns 1───N campaign_targets
customers 1───N campaign_targets
```

## 6. Sistema

```
users 1───N notifications
users 1───N file_assets (owner)
tenants 1───N tenant_settings
tenants 1───N audit_log (via tenant_id, exceto ações de plataforma)
```

## 7. Diagrama consolidado (simplificado)

```
                    tenants
                       │
        ┌──────────────┼──────────────┬───────────────┐
        ▼              ▼              ▼               ▼
     branches        users         pipelines        queues
        │            │  │             │                │
        ▼            │  ▼             ▼                ▼
      teams ◀─────────┘ roles       stages           calls / conversations
                                                          │
customers ──┬── contacts                                 │
     │       ├── leads ──── opportunities ── opportunity_stage_history
     │       ├── notes / tasks / appointments (polimórfico)
     │       └── conversations ── messages
     └── campaign_targets ── campaigns
```

## 8. Observações de modelagem

- Relações **polimórficas** (`notes`, `tasks`, `appointments` referenciando lead/customer/opportunity) são controladas por `entity_type` + `entity_id` na aplicação — não há FK de banco nativa para esse padrão; a integridade é garantida por validação na camada de serviço (ver [../07-backend/backend-architecture.md](../07-backend/backend-architecture.md)). `[DECISÃO PENDENTE]`: avaliar se compensa modelar como três tabelas de junção dedicadas em vez de polimorfismo, trade-off de simplicidade vs. integridade referencial nativa.
- `leads.customer_id` é preenchido apenas quando o lead é vinculado/convertido — antes disso pode representar um contato ainda não cadastrado como cliente.
- Toda entidade com `tenant_id` só se relaciona com entidades do mesmo `tenant_id` — validado na camada de serviço, não apenas por FK (FK sozinha não impede relacionar registros de tenants diferentes que compartilham o mesmo espaço de tabelas).
