# MAT-005 — Usuários: CRUD

## 1. Identificação

| Campo | Valor |
|---|---|
| ID | MAT-005 |
| Fase | 2 |
| Prioridade | CRÍTICA |
| Tipo | Funcional + Auditoria |
| Requisitos relacionados | RF-04 |
| ADRs relacionados | — |
| Decisions relacionadas | [D-060](../../00-governance/decision-register.md#d-060--auditoria-básica-write-only-nesta-fase), [D-061](../../00-governance/decision-register.md#d-061--paginação-de-users-corrigida-para-offset), [D-062](../../00-governance/decision-register.md#d-062--validação-de-uuid-nos-dtos-deve-aceitar-v7-não-v4) |

Referências adicionais: [personas.md](../../01-product/personas.md) §2.2, [BR-23/BR-24](../../02-business/business-rules.md).

## 2. Objetivo

Validar o ciclo completo de um usuário — criar, listar (paginação offset), atualizar,
desativar — e que cada mutação gera entrada de auditoria imutável.

## 3. Escopo

**Cobre**: `POST/GET/PATCH/DELETE /v1/users`, formato de paginação, e a gravação transacional
em `audit_log` para cada mutação.

**Não cobre**: isolamento entre tenants nessas mesmas rotas — isso é o
[MAT-007](MAT-007-tenant-isolation.md). Nem RBAC (permissão negada) — isso é o
[MAT-006](MAT-006-rbac.md).

## 4. Pré-requisitos

```bash
cd crm-workspace
docker compose up -d

cd ../crm-backend
npm run db:setup
npm run dev
```

Acesso direto ao Postgres para os passos 4 e 5 (ex.: `psql` apontando para a conexão definida
em `crm-backend/.env`, ou o client gráfico de sua preferência).

## 5. Dados de teste

Usuário admin do seed (`admin@exemplo.crm.local` / `Admin123!`), com permissões `users:*`
completas — usar o `access_token` obtido no login em todas as chamadas abaixo (cabeçalho
`Authorization: Bearer <access_token>`).

## 6. Tutorial de execução manual

### Passo 1 — Criar um usuário

**Ação**: criar um usuário novo no tenant do admin logado.

**Comando**:
```bash
curl -i -X POST http://localhost:3000/v1/users \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"MAT Usuario","email":"mat-usuario@exemplo.crm.local","password":"MatSenha123!"}'
```

**Resultado esperado**: `HTTP 201`.

**O que observar**:
- corpo com `id`, `name`, `email`, `status: "active"`, `created_at`;
- corpo **sem** `password`/`password_hash` em nenhum campo;
- guardar o `id` retornado — é usado nos próximos passos.

### Passo 2 — Listar usuários

**Ação**: listar a primeira página de usuários do tenant.

**Comando**:
```bash
curl -i "http://localhost:3000/v1/users?page=1&limit=20" \
  -H "Authorization: Bearer <access_token>"
```

**Resultado esperado**: `HTTP 200`.

**O que observar**: corpo no formato `{data, page, limit, total}` — **não** `next_cursor`
(offset, não cursor).

### Passo 3 — Atualizar o usuário criado

**Ação**: mudar o nome do usuário do Passo 1.

**Comando**:
```bash
curl -i -X PATCH http://localhost:3000/v1/users/<id> \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"MAT Usuario Renomeado"}'
```

**Resultado esperado**: `HTTP 200`, `name` atualizado no corpo.

### Passo 4 — Desativar o usuário

**Ação**: desativar (soft) o usuário criado.

**Comando**:
```bash
curl -i -X DELETE http://localhost:3000/v1/users/<id> \
  -H "Authorization: Bearer <access_token>"
```

**Resultado esperado**: `HTTP/1.1 204 No Content`.

### Passo 5 — Conferir auditoria no banco

**Ação**: consultar `audit_log` filtrando pelo `entity_id` do usuário criado.

**Comando** (exemplo via `psql`):
```sql
SELECT action, entity, entity_id FROM audit_log WHERE entity_id = '<id>' ORDER BY created_at;
```

**Resultado esperado**: três linhas — `user.created`, `user.updated`, `user.deactivated`,
todas com o mesmo `entity_id`.

### Passo 6 — Conferir o estado final do usuário no banco

**Ação**: consultar a própria linha do usuário.

**Comando**:
```sql
SELECT status, deleted_at FROM users WHERE id = '<id>';
```

**Resultado esperado**: `status = 'inactive'`, `deleted_at` **nulo** — desativação lógica via
campo próprio, não soft delete via `deletedAt` (distinto do soft delete de dado de negócio, BR-22).

## 7. Resultado que NÃO deve acontecer

- ✗ `password`/`password_hash` em qualquer resposta.
- ✗ `next_cursor` no corpo de `GET /users` (sinal de que a paginação regrediu para cursor).
- ✗ `deleted_at` preenchido após `DELETE` (confundiria desativação de usuário com soft delete de dado de negócio).
- ✗ Ausência de qualquer uma das três entradas de auditoria.
- ✗ `500` em qualquer passo.

---

## 8. Resultado da IA — Execução anterior

> Evidência histórica de execução automatizada pela IA/agente. **Não é validação manual do
> responsável** — ver seção 9.

| Campo | Valor |
|---|---|
| Executor | Claude (Sonnet 5) |
| Data | 2026-09-09 |
| Ambiente | `crm-workspace` local (Postgres + Redis reais) |
| Método | `curl` + consulta direta ao Postgres |
| Resultado | **PASSOU** |

**Evidências:**

Criação:
```json
HTTP 201
{"id":"01a0877b-4b74...redacted","name":"MAT Usuario","email":"mat-usuario@exemplo.crm.local","status":"active","created_at":"2026-09-09T18:43:19.540Z"}
```

Listagem (offset):
```json
HTTP 200
{"data":[...3 usuarios...],"page":1,"limit":20,"total":3}
```

Atualização:
```json
HTTP 200
{"id":"01a0877b-4b74...redacted","name":"MAT Usuario Renomeado", ...}
```

Desativação:
```
HTTP 204
```

Auditoria (consulta direta ao Postgres, `entity_id` do usuário criado):
```
user.created      | user | 01a0877b-4b74...redacted
user.updated      | user | 01a0877b-4b74...redacted
user.deactivated  | user | 01a0877b-4b74...redacted
```

Estado final do usuário no banco:
```
status=inactive | deleted_at=(vazio)
```

**Observações**: `role_ids` no create/update (com UUID v7) não foi reexercitado manualmente
aqui — já coberto com evidência de banco no teste e2e `atualiza nome e papeis do proprio
tenant e registra auditoria (BR-23)`, que foi o teste que revelou e corrigiu o bug de validação
`@IsUUID('4')` (D-062).

## 9. Validação Manual do Responsável

> **Não preencher automaticamente.** Esta seção é responsabilidade do responsável pelo projeto,
> preenchida após executar de verdade os passos da seção 6.

- **Executor**: _______________________________
- **Data**: _______________________________
- **Ambiente**: _______________________________
- **Resultado**: [ ] PASSOU  [ ] FALHOU  [ ] BLOQUEADO

**Passos executados:**
- [ ] Passo 1 — Criar um usuário
- [ ] Passo 2 — Listar usuários
- [ ] Passo 3 — Atualizar o usuário criado
- [ ] Passo 4 — Desativar o usuário
- [ ] Passo 5 — Conferir auditoria no banco
- [ ] Passo 6 — Conferir estado final no banco

**Observações:**

_______________________________

**Evidências** (screenshot / vídeo / log / outro):

_______________________________

## 10. Critério de Aceite

- 🟢 **PASSOU** — o comportamento observado manualmente corresponde integralmente ao esperado em cada passo da seção 6, sem nenhuma ocorrência da seção 7.
- 🔴 **FALHOU** — qualquer resultado da seção 7 ocorreu.
- 🟡 **BLOQUEADO** — o teste não pôde ser executado por problema de ambiente, dependência ou pré-requisito.

> **Importante**: "Resultado da IA = PASSOU" (seção 8) **não** significa automaticamente
> "Validação manual = PASSOU" (seção 9).

## 11. Histórico

| Data | Executor | Tipo | Resultado |
|---|---|---|---|
| 2026-09-09 | Claude (Sonnet 5) | IA | PASSOU |
| _(a preencher)_ | _(responsável pelo projeto)_ | Manual | PENDENTE |
