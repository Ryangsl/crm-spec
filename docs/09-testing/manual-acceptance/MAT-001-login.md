# MAT-001 — Autenticação: Login

**Fase**: 2 · **Prioridade**: CRÍTICA · **Depende de**: [ADR-008](../../adr/ADR-008.md), [D-006](../../00-governance/decision-register.md#d-006--topologia-de-domínio-samesite-e-csrf)

## Objetivo

Validar que `POST /v1/auth/login` autentica com credenciais válidas, rejeita credenciais
inválidas sem distinguir "senha errada" de "e-mail inexistente", e entrega o refresh token
exclusivamente via cookie httpOnly — nunca no corpo da resposta (D1).

## Pré-requisitos

- `docker compose up -d` (Postgres + Redis) no `crm-workspace`.
- `npm run db:setup` no `crm-backend` (migrations + seed).
- `npm run dev` no `crm-backend` — API em `http://localhost:3000`.

## Dados de teste

Usuário do seed: `admin@exemplo.crm.local` / `Admin123!` (tenant "Empresa Exemplo", ativo).

## Passos detalhados

1. `POST http://localhost:3000/v1/auth/login` com corpo `{"email":"admin@exemplo.crm.local","password":"Admin123!"}`.
2. Inspecionar o corpo da resposta e o cabeçalho `Set-Cookie`.
3. Repetir com senha errada.
4. Repetir com e-mail que não existe em nenhum tenant.
5. Comparar as respostas dos passos 3 e 4.

## Resultado esperado

- ✓ Passo 1: `201`, corpo com `access_token` (string) e `expires_in: 900`.
- ✓ Passo 1: `Set-Cookie` presente com `HttpOnly`, `Path=/v1/auth`, `SameSite=Lax`.
- ✓ Passo 1: **sem `Secure`** (ambiente não é produção — `NODE_ENV≠production`).
- ✓ Passos 3 e 4: `401`, mesmo `error.code` (`INVALID_CREDENTIALS`), mesma mensagem — não dá para saber pela resposta se o e-mail existe.

## Resultado que NÃO deve acontecer

- ✗ `refresh_token` aparecendo em qualquer lugar do corpo JSON.
- ✗ Cookie sem `HttpOnly` (leitura por JavaScript no navegador).
- ✗ Cookie com `Path=/` (seria enviado para toda a API, não só `/v1/auth`).
- ✗ Resposta de "senha errada" diferente de "e-mail inexistente" (vazaria quais e-mails têm conta).
- ✗ `500` em qualquer um dos passos.

## Evidências (executado em 2026-09-09, backend real contra Postgres/Redis reais)

**Login válido:**
```
HTTP/1.1 201 Created
Set-Cookie: refresh_token=01a0877a-1c7b-...; Max-Age=604800; Path=/v1/auth; Expires=Wed, 16 Sep 2026 18:42:01 GMT; HttpOnly; SameSite=Lax

{"access_token":"eyJhbGci...","expires_in":900}
```

**Senha incorreta:**
```
HTTP 401
{"error":{"code":"INVALID_CREDENTIALS","message":"E-mail ou senha invalidos.","details":[]}}
```

**E-mail inexistente** — mesma resposta exata do caso acima (mesmo `code`, mesma `message`), confirmando a não-distinção.

## Resultado

**PASSOU** — 2026-09-09, executado por Claude (Sonnet 5) via `curl` contra ambiente local real.

## Observações

Nenhuma. O trecho do cookie foi truncado acima por brevidade — o valor completo (`id.secret`)
foi conferido como opaco e sem estrutura decodificável, conforme esperado.
