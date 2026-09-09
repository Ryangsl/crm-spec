# MAT-003 — Autenticação: Logout individual

**Fase**: 2 · **Prioridade**: ALTA · **Depende de**: [ADR-008](../../adr/ADR-008.md), [D-056](../../00-governance/decision-register.md#d-056--política-de-reuso-de-refresh-token-família-de-sessões)

## Objetivo

Validar que `POST /v1/auth/logout` encerra **só** a sessão do cookie apresentado, limpa o
cookie na resposta, e — ponto que já foi um bug real durante a implementação — que reusar o
token pós-logout **não** varre as outras sessões do usuário (ao contrário do reuso pós-rotação, ver [MAT-002](MAT-002-refresh.md)).

## Pré-requisitos

Mesmos do [MAT-001](MAT-001-login.md).

## Dados de teste

Duas sessões do mesmo usuário do seed (cookies A e B).

## Passos detalhados

1. Login duas vezes → cookies A e B.
2. `POST /v1/auth/logout` com o cookie A.
3. Inspecionar o `Set-Cookie` da resposta do passo 2.
4. `POST /v1/auth/refresh` com o cookie A (já revogado por logout).
5. `POST /v1/auth/refresh` com o cookie B — verificar se **continua** válido.

## Resultado esperado

- ✓ Passo 2: `204 No Content`.
- ✓ Passo 3: `Set-Cookie: refresh_token=; ... Expires=Thu, 01 Jan 1970 00:00:00 GMT` (limpa o cookie no navegador).
- ✓ Passo 4: `401`, `INVALID_REFRESH_TOKEN`.
- ✓ Passo 5: `201` — sessão B **não afetada** pelo logout individual de A.

## Resultado que NÃO deve acontecer

- ✗ Passo 5 retornando `401` (seria o bug de família-varrida-por-engano que foi encontrado e corrigido durante a implementação — regressão crítica se voltar a acontecer).
- ✗ Logout de um token inexistente/já inválido retornando erro (deve ser idempotente — ver observação).
- ✗ `500` em qualquer passo.

## Evidências (executado em 2026-09-09)

**Logout:**
```
HTTP/1.1 204 No Content
Set-Cookie: refresh_token=; Path=/v1/auth; Expires=Thu, 01 Jan 1970 00:00:00 GMT; HttpOnly; SameSite=Lax
```

**Refresh com A pós-logout:**
```
HTTP 401
{"error":{"code":"INVALID_REFRESH_TOKEN","message":"Refresh token invalido, expirado ou revogado.","details":[]}}
```

**Refresh com B (sessão irmã, intocada):**
```
HTTP/1.1 201 Created
Set-Cookie: refresh_token=01a0877a-931f-...; ...
{"access_token":"eyJhbGci...","expires_in":900}
```

## Resultado

**PASSOU** — 2026-09-09, executado por Claude (Sonnet 5) via `curl` contra ambiente local real.

## Observações

Idempotência (`POST /v1/auth/logout` com token já inválido não é erro) está coberta pelo
teste e2e automatizado (`auth.e2e-spec.ts`), não repetida manualmente aqui — não agrega
evidência nova, é o mesmo código já validado.
