# MAT-007 — Isolamento entre Tenants

**Fase**: 2 · **Prioridade**: CRÍTICA (o mais crítico de toda a Fase 2) · **Depende de**: [ADR-004](../../adr/ADR-004.md), [BR-01/BR-02/BR-26](../../02-business/business-rules.md), [security.md](../../03-architecture/security.md) §1.3

## Objetivo

Provar que um usuário autenticado de um tenant nunca lê, altera ou apaga dado de outro
tenant, em nenhuma operação — e que a resposta a uma tentativa é sempre `404` (recurso "não
existe" do ponto de vista de quem não tem acesso), nunca `403` (que confirmaria a existência
do recurso) nem, pior, sucesso.

Este é o MAT de onde nasce o [padrão reutilizável MAT-SEC-TENANT-001](MAT-SEC-TENANT-001-template.md), que toda entidade tenant-scoped futura (Customers, Leads, Opportunities...) precisa repetir.

## Pré-requisitos

Mesmos do [MAT-001](MAT-001-login.md), mais um segundo tenant com admin próprio ("MAT Tenant
B", ver dados de teste).

## Dados de teste

- **Tenant A**: "Empresa Exemplo" (seed), admin `admin@exemplo.crm.local`.
- **Tenant B**: "MAT Tenant B", admin `admin@mat-tenant-b.test` — papel com `users:*` completo, mas só dentro do próprio tenant.

## Passos detalhados

1. Login como admin do Tenant A → anotar o `id` de um usuário existente nesse tenant.
2. Login como admin do Tenant B.
3. `GET /v1/users/{id do usuário de A}` com o token de B.
4. `PATCH /v1/users/{id do usuário de A}` com o token de B, tentando mudar o nome.
5. `DELETE /v1/users/{id do usuário de A}` com o token de B.
6. `GET /v1/users` com o token de B — conferir que nenhum usuário de A aparece na lista.
7. Conferir no banco que o usuário de A não foi alterado por nenhuma das tentativas.

## Resultado esperado

- ✓ Passos 3, 4 e 5: `404`, `error.code = "NOT_FOUND"` — idêntico ao que aconteceria se o `id` simplesmente não existisse em lugar nenhum.
- ✓ Passo 6: lista contém só usuários do Tenant B.
- ✓ Passo 7: o registro do usuário de A no banco está exatamente como estava antes.

## Resultado que NÃO deve acontecer

- ✗ `200`/`204` em qualquer uma das tentativas de B contra o recurso de A.
- ✗ `403` em vez de `404` (revelaria que o recurso existe, mesmo sem acesso — viola BR-26).
- ✗ Qualquer dado do usuário de A aparecendo no corpo de alguma resposta a B.
- ✗ O nome do usuário de A alterado após a tentativa de PATCH do passo 4.
- ✗ O usuário de A desativado (`status=inactive`) após a tentativa de DELETE do passo 5.

## Evidências (executado em 2026-09-09)

**GET cross-tenant:**
```json
HTTP 404
{"error":{"code":"NOT_FOUND","message":"Not Found","details":[]}}
```

**PATCH cross-tenant** — mesma resposta exata do GET acima.

**DELETE cross-tenant** — mesma resposta exata.

**Listagem do Tenant B** (confirmando ausência de qualquer usuário de A):
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

## Resultado

**PASSOU** — 2026-09-09, executado por Claude (Sonnet 5) via `curl` contra ambiente local real.

## Observações

Este é o MAT com maior sobreposição com testes automatizados (`tenant-isolation.e2e-spec.ts`
cobre os mesmos cenários, com mais variações — payload forjando `tenant_id`, criação sempre
no tenant do token). A execução manual aqui não substitui os automatizados; confirma
independentemente, com dados e sessões diferentes dos que o CI usa, que o comportamento é
real e não um artefato do fixture de teste.
