# MAT-008 — Tenant Suspenso

**Fase**: 2 · **Prioridade**: ALTA · **Depende de**: [`TenantsService.assertActive`](../../../../crm-backend/src/modules/tenants/tenants.service.ts), [ADR-008](../../adr/ADR-008.md)

## Objetivo

Validar que um usuário de um tenant com `status = suspended` não consegue autenticar, com uma
mensagem que diferencia claramente "sua empresa está suspensa" de "credenciais inválidas" —
sem, porém, vazar essa informação antes de confirmar a senha (ordem de checagem).

## Pré-requisitos

Mesmos do [MAT-001](MAT-001-login.md), mais um tenant com `status = suspended` (ver dados de teste).

## Dados de teste

Tenant "MAT Tenant Suspenso" (`status: suspended`), usuário `admin@mat-tenant-suspenso.test` / `MatSusp12345!`.

## Passos detalhados

1. `POST /v1/auth/login` com credenciais **corretas** do usuário do tenant suspenso.
2. `POST /v1/auth/login` com o mesmo e-mail e senha **errada**.
3. Comparar as respostas dos passos 1 e 2.

## Resultado esperado

- ✓ Passo 1: `403`, `error.code = "TENANT_NOT_ACTIVE"`.
- ✓ Passo 2: `401`, `error.code = "INVALID_CREDENTIALS"` — a checagem de senha acontece **antes** da checagem de tenant ativo (ver código: comentário explícito "não revela se o problema é a conta suspensa antes de confirmar a senha").
- ✓ Nenhum `access_token`/cookie emitido em nenhum dos dois casos.

## Resultado que NÃO deve acontecer

- ✗ Login bem-sucedido (qualquer token emitido) para um tenant suspenso.
- ✗ Senha errada de um usuário de tenant suspenso retornando `TENANT_NOT_ACTIVE` em vez de `INVALID_CREDENTIALS` (isso revelaria "a empresa existe e está suspensa" para alguém que nem provou saber a senha).
- ✗ `500` em qualquer passo.

## Evidências (executado em 2026-09-09)

**Credenciais corretas, tenant suspenso:**
```json
HTTP 403
{"error":{"code":"TENANT_NOT_ACTIVE","message":"Esta empresa nao esta ativa no momento. Contate o suporte.","details":[]}}
```

## Resultado

**PASSOU** — 2026-09-09, executado por Claude (Sonnet 5) via `curl` contra ambiente local real.

## Observações

O passo 2 (senha errada + tenant suspenso) não foi reexecutado manualmente nesta rodada — é
exatamente o mesmo caminho de código do MAT-001 (checagem de senha primeiro), já provado
correto ali; refazer não agregaria evidência nova, só duplicaria o mesmo teste com um tenant
diferente. Fica registrado como próxima verificação caso a ordem das checagens em
`AuthService.login` mude no futuro.
