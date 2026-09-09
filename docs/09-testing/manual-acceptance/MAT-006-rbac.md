# MAT-006 — RBAC: permissão concedida vs. negada

**Fase**: 2 · **Prioridade**: CRÍTICA · **Depende de**: [personas.md](../../01-product/personas.md) §1/§3, [BR-25/BR-26](../../02-business/business-rules.md), [D-058](../../00-governance/decision-register.md#d-058--escopo-de-rbac-na-fase-2-apenas-tenant)

## Objetivo

Validar que um usuário sem a permissão atômica exigida recebe `403` de forma consistente
(nunca execução parcial, nunca `500`), e que uma rota sem `@RequirePermissions` (própria do
usuário, como `/me`) continua acessível mesmo sem nenhuma permissão de módulo.

## Pré-requisitos

Mesmos do [MAT-001](MAT-001-login.md), mais um usuário do Tenant B com papel **sem nenhuma
permissão** (`sempermissao@mat-tenant-b.test`, ver dados de teste).

## Dados de teste

Tenant "MAT Tenant B" com um usuário cujo único papel não concede nenhuma `permission` (nem
`users:read`, nem `users:create`).

## Passos detalhados

1. Login com o usuário sem permissão.
2. `GET /v1/users` com o token desse usuário.
3. `POST /v1/users` com o token desse usuário.
4. `GET /v1/users/me` com o mesmo token.

## Resultado esperado

- ✓ Passo 2: `403`, `error.code = "FORBIDDEN"`.
- ✓ Passo 3: `403`, mesmo código.
- ✓ Passo 4: `200` — rota própria do usuário autenticado não passa por `@RequirePermissions`, então funciona independentemente de qualquer permissão de módulo.

## Resultado que NÃO deve acontecer

- ✗ Qualquer execução parcial (ex.: listar mas com dados incompletos) em vez de bloqueio total.
- ✗ `500` em vez de `403`.
- ✗ `401` em vez de `403` (o usuário está autenticado — o problema é permissão, não identidade; confundir os dois códigos dificulta o cliente diferenciar "faça login de novo" de "peça acesso ao seu admin").
- ✗ Passo 4 falhando por falta de permissão de módulo (RBAC mal implementado bloquearia até o próprio usuário se ver).

## Evidências (executado em 2026-09-09)

**Listar sem `users:read`:**
```json
HTTP 403
{"error":{"code":"FORBIDDEN","message":"Forbidden","details":[]}}
```

**Criar sem `users:create`:**
```json
HTTP 403
{"error":{"code":"FORBIDDEN","message":"Forbidden","details":[]}}
```

**`/me` mesmo sem nenhuma permissão de módulo:**
```json
HTTP 200
{"id":"01a08779-f5d9-...","name":"sempermissao@mat-tenant-b.test","email":"sempermissao@mat-tenant-b.test","status":"active","created_at":"2026-09-09T18:41:52.089Z"}
```

## Resultado

**PASSOU** — 2026-09-09, executado por Claude (Sonnet 5) via `curl` contra ambiente local real.

## Observações

Este MAT valida RBAC no **escopo de tenant** apenas (D-058) — não existe hoje nenhum cenário
de "permissão concedida mas escopo de equipe/filial nega o registro específico", porque esse
enforcement é explicitamente Fase 3+. Quando `Team`/`Branch` ganharem regra ativa, este MAT
precisa de uma seção nova para esse caso.
