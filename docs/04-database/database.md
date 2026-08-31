# Banco de Dados — Convenções

Tecnologia: **PostgreSQL** (ADR-001). Este documento define convenções gerais; entidades detalhadas estão em [entities.md](entities.md) e relacionamentos em [relationships.md](relationships.md). Migrations reais não são escritas nesta etapa (documentação, não implementação).

## 1. Convenções gerais

- **Chave primária**: UUID (v4 ou v7 — `[DECISÃO PENDENTE]`, v7 preferível por ordenação temporal/performance de índice) em todas as tabelas de negócio. Não usar IDs sequenciais expostos publicamente.
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

- Paginação por cursor (`[DECISÃO PENDENTE]`: cursor vs. offset — cursor é preferível para listas de alto volume/tempo real como `interactions`, offset é aceitável para telas administrativas pequenas). Ver contrato em [../05-api/api-guidelines.md](../05-api/api-guidelines.md).
- Filtros comuns (status, responsável, período, fila) devem ter índice de suporte antes de ir para produção.

## 4. Particionamento futuro

Tabelas de alto volume (`interactions`, `messages`, `calls`, `audit_log`) são candidatas a particionamento por `tenant_id` e/ou por período (mês) quando o volume justificar (ver [../03-architecture/scalability.md](../03-architecture/scalability.md)). A modelagem inicial evita chaves/relacionamentos que impeçam particionar depois, mas o particionamento em si **não é implementado no MVP**.

## 5. Multi-tenancy no banco

Estratégia adotada: banco compartilhado com `tenant_id` (ADR-004, detalhado em [../03-architecture/security.md](../03-architecture/security.md)). Row Level Security (RLS) como camada adicional é `[DECISÃO PENDENTE]`.

## 6. Campos personalizados (custom fields)

`[DECISÃO PENDENTE]`: representação de campos personalizados por tenant em Leads/Clientes — opções em avaliação: coluna `JSONB` (`custom_fields`) por entidade (mais simples, sem migração por tenant, busca mais limitada) vs. tabela EAV dedicada (mais flexível para filtros/relatórios, mais complexa). Recomendação inicial: `JSONB`, revisitar se a necessidade de filtro/relatório sobre campos customizados crescer.
