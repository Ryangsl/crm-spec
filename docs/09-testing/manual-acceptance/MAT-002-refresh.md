# MAT-002 — Autenticação: Refresh

**Fase**: 2 · **Prioridade**: CRÍTICA · **Depende de**: [ADR-008](../../adr/ADR-008.md), [D-056](../../00-governance/decision-register.md#d-056--política-de-reuso-de-refresh-token-família-de-sessões)

## Objetivo

Validar a rotação do refresh token, a rejeição de refresh sem cookie, e — o ponto mais crítico
desta fase — que **reapresentar um token já rotacionado revoga toda a família de sessões do
usuário**, não só o token reutilizado.

## Pré-requisitos

Mesmos do [MAT-001](MAT-001-login.md).

## Dados de teste

Usuário do seed logado duas vezes (duas sessões independentes, cookies A e B).

## Passos detalhados

1. Login → guardar cookie A.
2. `POST /v1/auth/refresh` com o cookie A → guardar o novo cookie A'.
3. `POST /v1/auth/refresh` reapresentando o cookie A **antigo** (já rotacionado no passo 2).
4. `POST /v1/auth/refresh` **sem** cookie nenhum.
5. Login de novo (sessão nova, cookie A2) e, em paralelo, login de uma segunda sessão (cookie B) do mesmo usuário.
6. Refresh com A2 (rotaciona A2 → A2').
7. Reuso do A2 antigo (reproduz o passo 3, evidência de reuso comprovado).
8. Refresh com o cookie B, que **nunca foi reutilizado** — verificar se foi varrido junto (família).

## Resultado esperado

- ✓ Passo 2: `201`, novo `access_token`, novo cookie com valor diferente do original.
- ✓ Passo 3: `401`, `INVALID_REFRESH_TOKEN`.
- ✓ Passo 4: `401`, mesmo código (ausência de cookie tratada como token inválido, não erro diferente).
- ✓ Passo 8: `401` — a sessão B, embora nunca reutilizada, é revogada porque o reuso do passo 7 foi de um token com `revoked_reason=rotated` (evidência confiável de comprometimento — D-056).

## Resultado que NÃO deve acontecer

- ✗ Refresh bem-sucedido reutilizando um token já rotacionado.
- ✗ O cookie novo (rotacionado) ser igual ao antigo.
- ✗ Mensagem de erro diferente entre "sem cookie" e "cookie inválido" (vazaria informação de diagnóstico a um atacante testando o endpoint).
- ✗ A sessão B continuar válida após o reuso comprovado da sessão A (falha da política de família — a checagem mais importante deste MAT).
- ✗ `500` em qualquer passo.

## Evidências (executado em 2026-09-09)

**Rotação:**
```
HTTP/1.1 201 Created
Set-Cookie: refresh_token=01a0877a-3d87-...  (id novo, diferente do original 01a0877a-1c7b-...)
```

**Reuso do token antigo:**
```
HTTP 401
{"error":{"code":"INVALID_REFRESH_TOKEN","message":"Refresh token invalido, expirado ou revogado.","details":[]}}
```

**Sem cookie** — mesma resposta exata do reuso acima.

**Família varrida** (sessão B, nunca reutilizada, após reuso comprovado de outra sessão do mesmo usuário):
```
HTTP 401
{"error":{"code":"INVALID_REFRESH_TOKEN", ...}}
```

## Resultado

**PASSOU** — 2026-09-09, executado por Claude (Sonnet 5) via `curl` contra ambiente local real.

## Observações

O comportamento de "família" foi o motivo pelo qual D-056 precisou distinguir
`revoked_reason` (`rotated` vs. `logout`): reuso pós-**logout** normal não deveria varrer a
família (ver [MAT-003](MAT-003-logout.md)), só reuso pós-**rotação** deveria. Este MAT cobre
o caminho que deve varrer; o MAT-003 cobre o caminho que não deve.
