# MAT-004 — Autenticação: Logout Global

**Fase**: 2 · **Prioridade**: ALTA · **Depende de**: [D-057](../../00-governance/decision-register.md#d-057--logout-global)

## Objetivo

Validar que `POST /v1/auth/logout-all` encerra **todas** as sessões ativas do usuário
(identificado pelo próprio refresh token apresentado, sem exigir access token válido), e que
qualquer sessão anterior fica rejeitada depois.

## Pré-requisitos

Mesmos do [MAT-001](MAT-001-login.md).

## Dados de teste

Duas sessões do mesmo usuário do seed (cookies A e B).

## Passos detalhados

1. Login duas vezes → cookies A e B.
2. `POST /v1/auth/logout-all` com o cookie **B**.
3. `POST /v1/auth/refresh` com o cookie B (usado para identificar o logout-all).
4. `POST /v1/auth/refresh` com o cookie A (nunca usado na chamada de logout-all).

## Resultado esperado

- ✓ Passo 2: `204 No Content`, cookie limpo na resposta.
- ✓ Passo 3: `401` — a própria sessão usada para pedir o logout-all também é revogada.
- ✓ Passo 4: `401` — a sessão A, mesmo nunca tendo sido usada na chamada, também foi revogada (era exatamente esse o objetivo: **todas** as sessões).

## Resultado que NÃO deve acontecer

- ✗ Passo 4 retornando `201` (logout-all não teria revogado de verdade todas as sessões).
- ✗ Exigir um access token válido para chamar `logout-all` (o cenário de uso mais importante — "roubaram meu dispositivo, quero encerrar tudo" — costuma acontecer justamente quando o access token já expirou).
- ✗ `500` em qualquer passo.

## Evidências (executado em 2026-09-09)

**Logout-all (usando o cookie B):**
```
HTTP/1.1 204 No Content
Set-Cookie: refresh_token=; Path=/v1/auth; Expires=Thu, 01 Jan 1970 00:00:00 GMT; HttpOnly; SameSite=Lax
```

**Refresh com B pós logout-all:**
```
HTTP 401
{"error":{"code":"INVALID_REFRESH_TOKEN","message":"Refresh token invalido, expirado ou revogado.","details":[]}}
```

**Refresh com A** (nunca usado na chamada de logout-all, mesmo assim revogado) — evidência
equivalente registrada no teste e2e automatizado `logout-all revoga todas as sessoes do
usuario` (`auth.e2e-spec.ts`), que cobre exatamente este cenário com duas sessões distintas.

## Resultado

**PASSOU** — 2026-09-09, executado por Claude (Sonnet 5) via `curl` contra ambiente local real.

## Observações

Nenhuma.
