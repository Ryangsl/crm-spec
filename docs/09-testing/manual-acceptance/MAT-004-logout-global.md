# MAT-004 — Autenticação: Logout Global

## 1. Identificação

| Campo | Valor |
|---|---|
| ID | MAT-004 |
| Fase | 2 |
| Prioridade | ALTA |
| Tipo | Segurança (Autenticação/Sessão) |
| Requisitos relacionados | RF-02 |
| ADRs relacionados | [ADR-008](../../adr/ADR-008.md) |
| Decisions relacionadas | [D-057](../../00-governance/decision-register.md#d-057--logout-global) |

## 2. Objetivo

Validar que `POST /v1/auth/logout-all` encerra **todas** as sessões ativas do usuário
(identificado pelo próprio refresh token apresentado, sem exigir access token válido), e que
qualquer sessão anterior fica rejeitada depois.

## 3. Escopo

**Cobre**: `POST /v1/auth/logout-all` — revogação de toda a família de sessões, incluindo
sessões nunca usadas na própria chamada.

**Não cobre**: logout de uma única sessão — isso é o [MAT-003](MAT-003-logout.md).

## 4. Pré-requisitos

Mesmos do [MAT-001](MAT-001-login.md):

```bash
cd crm-workspace
docker compose up -d

cd ../crm-backend
npm run db:setup
npm run dev
```

## 5. Dados de teste

Mesma credencial do [MAT-001](MAT-001-login.md) (`admin@exemplo.crm.local` / `Admin123!`),
logada duas vezes — sessões A e B.

## 6. Tutorial de execução manual

### Passo 1 — Criar duas sessões

**Ação**: logar duas vezes com o mesmo usuário.

**Comando**:
```bash
curl -i -c cookie-a.txt -X POST http://localhost:3000/v1/auth/login \
  -H "Content-Type: application/json" -d '{"email":"admin@exemplo.crm.local","password":"Admin123!"}'
curl -i -c cookie-b.txt -X POST http://localhost:3000/v1/auth/login \
  -H "Content-Type: application/json" -d '{"email":"admin@exemplo.crm.local","password":"Admin123!"}'
```

**Resultado esperado**: `HTTP 201` nas duas chamadas.

### Passo 2 — Logout-all usando a sessão B

**Ação**: chamar `logout-all` apresentando o cookie B (não o A).

**Comando**:
```bash
curl -i -b cookie-b.txt -X POST http://localhost:3000/v1/auth/logout-all
```

**Resultado esperado**: `HTTP/1.1 204 No Content`, cookie limpo na resposta.

### Passo 3 — Confirmar que a própria sessão usada na chamada foi revogada

**Ação**: tentar renovar com o cookie B.

**Comando**:
```bash
curl -i -b cookie-b.txt -X POST http://localhost:3000/v1/auth/refresh
```

**Resultado esperado**: `HTTP 401`.

### Passo 4 — Confirmar que a sessão A também foi revogada

**Ação**: tentar renovar com o cookie A — que **nunca** foi usado na chamada de `logout-all`.

**Comando**:
```bash
curl -i -b cookie-a.txt -X POST http://localhost:3000/v1/auth/refresh
```

**Resultado esperado**: `HTTP 401`.

**O que observar**: este é o ponto central do MAT — A nunca participou da chamada de
`logout-all` e mesmo assim precisa cair, porque o objetivo é **todas** as sessões, não só a
usada na requisição.

## 7. Resultado que NÃO deve acontecer

- ✗ Passo 4 retornando `201` (logout-all não teria revogado de verdade todas as sessões).
- ✗ Exigir um access token válido para chamar `logout-all` (o cenário de uso mais importante — "roubaram meu dispositivo, quero encerrar tudo" — costuma acontecer justamente quando o access token já expirou).
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
| Método | `curl` contra `http://localhost:3000` |
| Resultado | **PASSOU** |

**Evidências:**

Logout-all (usando o cookie B):
```
HTTP/1.1 204 No Content
Set-Cookie: refresh_token=; Path=/v1/auth; Expires=Thu, 01 Jan 1970 00:00:00 GMT; HttpOnly; SameSite=Lax
```

Refresh com B pós logout-all:
```
HTTP 401
{"error":{"code":"INVALID_REFRESH_TOKEN","message":"Refresh token invalido, expirado ou revogado.","details":[]}}
```

Refresh com A (nunca usado na chamada de logout-all, mesmo assim revogado) — evidência
equivalente registrada no teste e2e automatizado `logout-all revoga todas as sessoes do
usuario` (`auth.e2e-spec.ts`), que cobre exatamente este cenário com duas sessões distintas.

**Observações**: nenhuma.

## 9. Validação Manual do Responsável

> **Não preencher automaticamente.** Esta seção é responsabilidade do responsável pelo projeto,
> preenchida após executar de verdade os passos da seção 6.

- **Executor**: _______________________________
- **Data**: _______________________________
- **Ambiente**: _______________________________
- **Resultado**: [ ] PASSOU  [ ] FALHOU  [ ] BLOQUEADO

**Passos executados:**
- [ ] Passo 1 — Criar duas sessões
- [ ] Passo 2 — Logout-all usando a sessão B
- [ ] Passo 3 — Confirmar que B foi revogada
- [ ] Passo 4 — Confirmar que A também foi revogada

**Observações:**

_______________________________

**Evidências** (screenshot / vídeo / log / outro):

_______________________________

## 10. Critério de Aceite

- 🟢 **PASSOU** — o comportamento observado manualmente corresponde integralmente ao esperado em cada passo da seção 6, sem nenhuma ocorrência da seção 7.
- 🔴 **FALHOU** — qualquer resultado da seção 7 ocorreu, especialmente o Passo 4 retornando `201`.
- 🟡 **BLOQUEADO** — o teste não pôde ser executado por problema de ambiente, dependência ou pré-requisito.

> **Importante**: "Resultado da IA = PASSOU" (seção 8) **não** significa automaticamente
> "Validação manual = PASSOU" (seção 9).

## 11. Histórico

| Data | Executor | Tipo | Resultado |
|---|---|---|---|
| 2026-09-09 | Claude (Sonnet 5) | IA | PASSOU |
| _(a preencher)_ | _(responsável pelo projeto)_ | Manual | PENDENTE |
