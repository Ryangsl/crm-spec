# MAT-005 — Usuários: CRUD

**Fase**: 2 · **Prioridade**: CRÍTICA · **Depende de**: [personas.md](../../01-product/personas.md) §2.2, [BR-23/BR-24](../../02-business/business-rules.md), [D-060](../../00-governance/decision-register.md#d-060--auditoria-básica-write-only-nesta-fase), [D-061](../../00-governance/decision-register.md#d-061--paginação-de-users-corrigida-para-offset)

## Objetivo

Validar o ciclo completo de um usuário — criar, listar (paginação offset), atualizar,
desativar — e que cada mutação gera entrada de auditoria imutável.

## Pré-requisitos

Mesmos do [MAT-001](MAT-001-login.md).

## Dados de teste

Usuário admin do seed (permissões `users:*` completas).

## Passos detalhados

1. `POST /v1/users` com nome, e-mail e senha de um usuário novo.
2. `GET /v1/users?page=1&limit=20` — conferir formato da resposta.
3. `PATCH /v1/users/{id}` do usuário criado, mudando o nome.
4. `DELETE /v1/users/{id}` do mesmo usuário.
5. Consultar `audit_log` no banco filtrando pelo `entity_id` do usuário criado.
6. Consultar a linha do usuário no banco (`status`, `deleted_at`).

## Resultado esperado

- ✓ Passo 1: `201`, corpo com `id`, `name`, `email`, `status: "active"`, `created_at` — **sem** `password`/`password_hash`.
- ✓ Passo 2: corpo com `{data, page, limit, total}` — **não** `next_cursor` (offset, não cursor — D-061).
- ✓ Passo 3: `200`, `name` atualizado no corpo.
- ✓ Passo 4: `204 No Content`.
- ✓ Passo 5: três linhas — `user.created`, `user.updated`, `user.deactivated`, todas com o mesmo `entity_id`.
- ✓ Passo 6: `status = 'inactive'`, `deleted_at` **nulo** — desativação lógica, não soft delete via `deletedAt` (personas.md §2.2, distinto de BR-22).

## Resultado que NÃO deve acontecer

- ✗ `password`/`password_hash` em qualquer resposta.
- ✗ `next_cursor` no corpo de `GET /users` (sinal de que a paginação regrediu para cursor).
- ✗ `deleted_at` preenchido após `DELETE` (confundiria desativação de usuário com soft delete de dado de negócio).
- ✗ Ausência de qualquer uma das três entradas de auditoria.
- ✗ `500` em qualquer passo.

## Evidências (executado em 2026-09-09)

**Criação:**
```json
HTTP 201
{"id":"01a0877b-4b74-...","name":"MAT Usuario","email":"mat-usuario@exemplo.crm.local","status":"active","created_at":"2026-09-09T18:43:19.540Z"}
```

**Listagem (offset):**
```json
HTTP 200
{"data":[...3 usuarios...],"page":1,"limit":20,"total":3}
```

**Atualização:**
```json
HTTP 200
{"id":"01a0877b-4b74-...","name":"MAT Usuario Renomeado", ...}
```

**Desativação:**
```
HTTP 204
```

**Auditoria** (consulta direta ao Postgres, `entity_id` do usuário criado):
```
user.created   | user | 01a0877b-4b74-...
user.updated   | user | 01a0877b-4b74-...
user.deactivated | user | 01a0877b-4b74-...
```

**Estado final do usuário no banco:**
```
status=inactive | deleted_at=(vazio)
```

## Resultado

**PASSOU** — 2026-09-09, executado por Claude (Sonnet 5) via `curl` + consulta direta ao Postgres.

## Observações

`role_ids` no create/update (com UUID v7) não foi reexercitado manualmente aqui — já coberto
com evidência de banco no teste e2e `atualiza nome e papeis do proprio tenant e registra
auditoria (BR-23)`, que foi o teste que revelou e corrigiu o bug de validação `@IsUUID('4')`
(D-062).
