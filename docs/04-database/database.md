# Banco de Dados — Convenções

Tecnologia: **PostgreSQL** (ADR-001). Este documento define convenções gerais; entidades detalhadas estão em [entities.md](entities.md) e relacionamentos em [relationships.md](relationships.md). Migrations reais não são escritas nesta etapa (documentação, não implementação).

## 1. Convenções gerais

- **Chave primária**: **UUID v7** em todas as tabelas de negócio ([D-001](../00-governance/decision-register.md#d-001--estratégia-de-identificador-primário), `DECIDIDO` — ver [ADR-009](../adr/ADR-009.md)). Nunca usar ID autoincremental como identificador público.
- **`tenant_id`**: coluna obrigatória (UUID, FK para `tenants`, indexada) em toda tabela de dado de negócio. Tabelas verdadeiramente globais (ex.: `tenants`, `plans`) não têm essa coluna.
- **Timestamps**: `created_at`, `updated_at` (timestamptz, default now / on update) em todas as tabelas; `deleted_at` (nullable) nas tabelas com soft delete.
- **Soft delete**: exclusão lógica via `deleted_at`; toda query de aplicação filtra `deleted_at IS NULL` por padrão. Exclusão física não é exposta via API (ver [../02-business/business-rules.md](../02-business/business-rules.md) BR-22).
- **Auditoria**: mudanças relevantes também são registradas em `audit_log` (ver [entities.md](entities.md)), independente do `updated_at` da própria tabela.
- **Nomenclatura**: tabelas e colunas em `snake_case`, inglês; nomes de tabela no plural (`customers`, `leads`).
- **Foreign Keys**: sempre explícitas, com `ON DELETE` definido conscientemente por relação (em geral `RESTRICT` para dados de negócio, `CASCADE` apenas para entidades filhas que não fazem sentido sem o pai, ex. `opportunity_stage_history`).

## 2. Índices

- Índice obrigatório em toda `tenant_id`.
- Índice composto `(tenant_id, <coluna de filtro comum>)` nas tabelas de listagem frequente (ex.: `(tenant_id, status)` em `leads`, `(tenant_id, owner_id)` em `opportunities`).
- Índices para busca textual (ex. nome/telefone de cliente) via `pg_trgm` ou índice funcional — avaliado quando a busca for implementada, não bloqueia o modelo inicial.
- Chaves estrangeiras sempre indexadas.

## 3. Paginação, busca e filtros (nível de banco)

- Paginação **híbrida** ([D-007](../00-governance/decision-register.md#d-007--estratégia-de-paginação), `DECIDIDO`): **offset** para recursos administrativos de volume moderado (usuários, clientes, leads, oportunidades, pipelines, configurações) e **cursor** para recursos cronológicos/volumosos (mensagens, interações, eventos, chamadas, logs, histórico). O UUID v7 ([D-001](../00-governance/decision-register.md#d-001--estratégia-de-identificador-primário)) serve como cursor por ser monotonicamente crescente. Ver contrato em [../05-api/api-guidelines.md](../05-api/api-guidelines.md).
- Filtros comuns (status, responsável, período, fila) devem ter índice de suporte antes de ir para produção.

## 4. Particionamento futuro

Tabelas de alto volume (`interactions`, `messages`, `calls`, `audit_log`) são candidatas a particionamento por `tenant_id` e/ou por período (mês) quando o volume justificar (ver [../03-architecture/scalability.md](../03-architecture/scalability.md)). A modelagem inicial evita chaves/relacionamentos que impeçam particionar depois, mas o particionamento em si **não é implementado no MVP**.

## 5. Multi-tenancy no banco

Estratégia adotada: banco compartilhado com `tenant_id` ([ADR-004](../adr/ADR-004.md), [D-002](../00-governance/decision-register.md#d-002--estratégia-de-multi-tenancy), `DECIDIDO`, detalhado em [../03-architecture/security.md](../03-architecture/security.md)). Row Level Security (RLS) como camada adicional: [D-003](../00-governance/decision-register.md#d-003--postgresql-row-level-security) (`PROPOSTO`, avaliar até o fim da Fase 2) — não substitui o filtro na aplicação nem os testes de isolamento.

## 6. Campos personalizados (custom fields)

Coluna **`JSONB`** (`custom_fields`) nas entidades que precisarem, começando por Clientes e Leads ([D-008](../00-governance/decision-register.md#d-008--campos-personalizados-mvp), `DECIDIDO`). Exemplo do conteúdo esperado:

```json
{ "interesse": "Consórcio", "origem": "Instagram", "renda": 5000 }
```

A estrutura permite evolução futura para definições de campo por tenant. Fora do MVP ([D-009](../00-governance/decision-register.md#d-009--sistema-completo-de-campos-personalizados), `ADIADO`): criação visual de campos, permissões por campo, validação complexa, workflows baseados em campos e engine EAV. O objetivo é preparar a arquitetura sem construir uma plataforma de customização prematuramente.
