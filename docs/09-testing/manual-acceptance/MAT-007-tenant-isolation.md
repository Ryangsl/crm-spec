# MAT-007 — Isolamento entre Tenants

## 1. Identificação

| Campo | Valor |
|---|---|
| ID | MAT-007 |
| Fase | 2 |
| Prioridade | CRÍTICA (o mais crítico de toda a Fase 2) |
| Tipo | Segurança (Multi-tenancy) |
| Requisitos relacionados | RF-05, RF-06 |
| ADRs relacionados | [ADR-004](../../adr/ADR-004.md) |
| Decisions relacionadas | — |

Referências adicionais: [BR-01/BR-02/BR-26](../../02-business/business-rules.md), [security.md](../../03-architecture/security.md) §1.3.

## 2. Objetivo

Provar que um usuário autenticado de um tenant nunca lê, altera ou apaga dado de outro
tenant, em nenhuma operação — e que a resposta a uma tentativa é sempre `404` (recurso "não
existe" do ponto de vista de quem não tem acesso), nunca `403` (que confirmaria a existência
do recurso) nem, pior, sucesso.

Este é o MAT de onde nasce o [padrão reutilizável MAT-SEC-TENANT-001](MAT-SEC-TENANT-001-template.md), que toda entidade tenant-scoped futura (Customers, Leads, Opportunities...) precisa repetir.

## 3. Escopo

**Cobre**: isolamento de `tenant_id` para o módulo `users` — leitura, atualização, exclusão,
listagem e tentativa de forjar `tenant_id` na criação.

**Não cobre**: RBAC (permissão concedida/negada dentro do próprio tenant) — isso é o
[MAT-006](MAT-006-rbac.md). Nem outras entidades — quando Customers/Leads/etc. existirem, cada
uma precisa do seu próprio MAT seguindo o [template](MAT-SEC-TENANT-001-template.md).

## 4. Pré-requisitos

```bash
cd crm-workspace
docker compose up -d

cd ../crm-backend
npm run db:setup
npm run dev
```

Um segundo tenant com admin próprio ("MAT Tenant B") — ver seção 5 e a nota de lacuna abaixo.

> ⚠️ **Lacuna conhecida**: o tenant "MAT Tenant B" **não faz parte** do seed padrão versionado
> (`crm-backend/prisma/seed.ts`) — foi provisionado manualmente durante a execução de
> 2026-09-09 (não há API de criação de tenant nesta fase, D-059). Para reexecutar este MAT do
> zero, é necessário recriar o tenant e o admin primeiro, replicando a estrutura do tenant
> "Empresa Exemplo" já presente em `prisma/seed.ts`. Registrado como lacuna para decisão futura
> (ex.: promover este fixture para o seed oficial, já que este é o MAT mais crítico da fase).

## 5. Dados de teste

- **Tenant A**: "Empresa Exemplo" (seed), admin `admin@exemplo.crm.local` / `Admin123!`.
- **Tenant B**: "MAT Tenant B", admin `admin@mat-tenant-b.test` — papel com `users:*` completo, mas só dentro do próprio tenant.

## 6. Tutorial de execução manual

### Passo 1 — Login como admin do Tenant A e anotar um `id`

**Ação**: autenticar como A e guardar o `id` de um usuário existente nesse tenant (pode ser o
próprio admin, via `GET /v1/users/me`).

**Comando**:
```bash
curl -s -X POST http://localhost:3000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@exemplo.crm.local","password":"Admin123!"}'
# usar o access_token retornado para:
curl -s http://localhost:3000/v1/users/me -H "Authorization: Bearer <access_token_A>"
```

**O que observar**: anotar o `id` do usuário de A retornado — é o alvo das tentativas cross-tenant abaixo.

### Passo 2 — Login como admin do Tenant B

**Ação**: autenticar como B.

**Comando**:
```bash
curl -s -X POST http://localhost:3000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@mat-tenant-b.test","password":"<senha do fixture>"}'
```

**O que observar**: guardar o `access_token` de B.

### Passo 3 — Tentar ler o usuário de A com o token de B

**Comando**:
```bash
curl -i http://localhost:3000/v1/users/<id do usuário de A> \
  -H "Authorization: Bearer <access_token_B>"
```

**Resultado esperado**: `HTTP 404`, `error.code = "NOT_FOUND"`.

### Passo 4 — Tentar alterar o usuário de A com o token de B

**Comando**:
```bash
curl -i -X PATCH http://localhost:3000/v1/users/<id do usuário de A> \
  -H "Authorization: Bearer <access_token_B>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Nome Forjado Por B"}'
```

**Resultado esperado**: `HTTP 404` — resposta idêntica à do Passo 3.

### Passo 5 — Tentar excluir o usuário de A com o token de B

**Comando**:
```bash
curl -i -X DELETE http://localhost:3000/v1/users/<id do usuário de A> \
  -H "Authorization: Bearer <access_token_B>"
```

**Resultado esperado**: `HTTP 404` — resposta idêntica às anteriores.

### Passo 6 — Confirmar que a listagem de B nunca mostra usuários de A

**Comando**:
```bash
curl -s http://localhost:3000/v1/users -H "Authorization: Bearer <access_token_B>"
```

**Resultado esperado**: `HTTP 200`, `data` contém **somente** usuários do Tenant B.

### Passo 7 — Confirmar no banco que o usuário de A não mudou

**Comando** (SQL, exemplo via `psql`):
```sql
SELECT name, status FROM users WHERE id = '<id do usuário de A>';
```

**Resultado esperado**: `name` e `status` exatamente como estavam antes dos Passos 3-5 (nome
**não** virou "Nome Forjado Por B"; `status` continua `active`, não `inactive`).

## 7. Resultado que NÃO deve acontecer

- ✗ `200`/`204` em qualquer uma das tentativas de B contra o recurso de A.
- ✗ `403` em vez de `404` (revelaria que o recurso existe, mesmo sem acesso — viola BR-26).
- ✗ Qualquer dado do usuário de A aparecendo no corpo de alguma resposta a B.
- ✗ O nome do usuário de A alterado após a tentativa de PATCH do Passo 4.
- ✗ O usuário de A desativado (`status=inactive`) após a tentativa de DELETE do Passo 5.

---

## 8. Resultado da IA — Execução anterior

> Evidência histórica de execução automatizada pela IA/agente. **Não é validação manual do
> responsável** — ver seção 9.

| Campo | Valor |
|---|---|
| Executor | Claude (Sonnet 5) |
| Data | 2026-09-09 |
| Ambiente | `crm-workspace` local (Postgres + Redis reais) |
| Método | `curl` contra `http://localhost:3000` |
| Resultado | **PASSOU** |

**Evidências:**

GET cross-tenant:
```json
HTTP 404
{"error":{"code":"NOT_FOUND","message":"Not Found","details":[]}}
```

PATCH cross-tenant — mesma resposta exata do GET acima.

DELETE cross-tenant — mesma resposta exata.

Listagem do Tenant B (confirmando ausência de qualquer usuário de A):
```json
HTTP 200
{"data":[
  {"id":"...","email":"sempermissao@mat-tenant-b.test",...},
  {"id":"...","email":"admin@mat-tenant-b.test",...}
],"page":1,"limit":20,"total":2}
```
— só os 2 usuários do próprio Tenant B, nenhum de A ou de qualquer outro tenant do banco (que
tinha, neste momento, também o Tenant "Empresa Exemplo" e o "MAT Tenant Suspenso" com dados
próprios).

**Observações**: este é o MAT com maior sobreposição com testes automatizados
(`tenant-isolation.e2e-spec.ts` cobre os mesmos cenários, com mais variações — payload forjando
`tenant_id`, criação sempre no tenant do token). A execução manual aqui não substitui os
automatizados; confirma independentemente, com dados e sessões diferentes dos que o CI usa, que
o comportamento é real e não um artefato do fixture de teste.

## 9. Validação Manual do Responsável

> **Não preencher automaticamente.** Esta seção é responsabilidade do responsável pelo projeto,
> preenchida após executar de verdade os passos da seção 6. **Este é o MAT mais crítico da
> fase — recomenda-se priorizar sua validação manual sobre os demais.**

- **Executor**: _______________________________
- **Data**: _______________________________
- **Ambiente**: _______________________________
- **Resultado**: [ ] PASSOU  [ ] FALHOU  [ ] BLOQUEADO

**Passos executados:**
- [ ] Passo 1 — Login como admin do Tenant A e anotar um `id`
- [ ] Passo 2 — Login como admin do Tenant B
- [ ] Passo 3 — Tentar ler o usuário de A com o token de B
- [ ] Passo 4 — Tentar alterar o usuário de A com o token de B
- [ ] Passo 5 — Tentar excluir o usuário de A com o token de B
- [ ] Passo 6 — Confirmar que a listagem de B nunca mostra usuários de A
- [ ] Passo 7 — Confirmar no banco que o usuário de A não mudou

**Observações:**

_______________________________

**Evidências** (screenshot / vídeo / log / outro):

_______________________________

## 10. Critério de Aceite

- 🟢 **PASSOU** — o comportamento observado manualmente corresponde integralmente ao esperado em cada passo da seção 6, sem nenhuma ocorrência da seção 7.
- 🔴 **FALHOU** — qualquer resultado da seção 7 ocorreu. Dado o nível crítico deste MAT, um `FALHOU` aqui deve ser tratado como bloqueador imediato do aceite da fase.
- 🟡 **BLOQUEADO** — o teste não pôde ser executado por problema de ambiente, dependência ou pré-requisito (ex.: fixture do Tenant B ainda não recriado).

> **Importante**: "Resultado da IA = PASSOU" (seção 8) **não** significa automaticamente
> "Validação manual = PASSOU" (seção 9).

## 11. Histórico

| Data | Executor | Tipo | Resultado |
|---|---|---|---|
| 2026-09-09 | Claude (Sonnet 5) | IA | PASSOU |
| _(a preencher)_ | _(responsável pelo projeto)_ | Manual | PENDENTE |
