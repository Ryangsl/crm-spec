# MAT-003 — Autenticação: Logout individual

## 1. Identificação

| Campo | Valor |
|---|---|
| ID | MAT-003 |
| Fase | 2 |
| Prioridade | ALTA |
| Tipo | Segurança (Autenticação/Sessão) |
| Requisitos relacionados | RF-02 |
| ADRs relacionados | [ADR-008](../../adr/ADR-008.md) |
| Decisions relacionadas | [D-056](../../00-governance/decision-register.md#d-056--política-de-reuso-de-refresh-token-família-de-sessões) |

## 2. Objetivo

Validar que `POST /v1/auth/logout` encerra **só** a sessão do cookie apresentado, limpa o
cookie na resposta, e — ponto que já foi um bug real durante a implementação — que reusar o
token pós-logout **não** varre as outras sessões do usuário (ao contrário do reuso pós-rotação,
ver [MAT-002](MAT-002-refresh.md)).

## 3. Escopo

**Cobre**: `POST /v1/auth/logout` — encerramento de uma sessão específica, limpeza de cookie, e
o não-vazamento do efeito para sessões irmãs.

**Não cobre**: logout de **todas** as sessões — isso é o [MAT-004](MAT-004-logout-global.md).

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
logada duas vezes para gerar duas sessões independentes — A e B.

## 6. Tutorial de execução manual

### Passo 1 — Criar duas sessões

**Ação**: logar duas vezes com o mesmo usuário, guardando os cookies separadamente.

**Comando**:
```bash
curl -i -c cookie-a.txt -X POST http://localhost:3000/v1/auth/login \
  -H "Content-Type: application/json" -d '{"email":"admin@exemplo.crm.local","password":"Admin123!"}'
curl -i -c cookie-b.txt -X POST http://localhost:3000/v1/auth/login \
  -H "Content-Type: application/json" -d '{"email":"admin@exemplo.crm.local","password":"Admin123!"}'
```

**Resultado esperado**: `HTTP 201` nas duas chamadas.

**O que observar**: os dois cookies (`cookie-a.txt`, `cookie-b.txt`) têm valores diferentes.

### Passo 2 — Logout da sessão A

**Ação**: encerrar só a sessão A.

**Comando**:
```bash
curl -i -b cookie-a.txt -X POST http://localhost:3000/v1/auth/logout
```

**Resultado esperado**: `HTTP/1.1 204 No Content`.

**O que observar**: o cabeçalho `Set-Cookie` da resposta limpa o cookie — formato
`refresh_token=; ... Expires=Thu, 01 Jan 1970 00:00:00 GMT`.

### Passo 3 — Confirmar que A foi revogada

**Ação**: tentar renovar usando o cookie A (já revogado por logout).

**Comando**:
```bash
curl -i -b cookie-a.txt -X POST http://localhost:3000/v1/auth/refresh
```

**Resultado esperado**: `HTTP 401`, `error.code = "INVALID_REFRESH_TOKEN"`.

### Passo 4 — Confirmar que B NÃO foi afetada

**Ação**: tentar renovar usando o cookie B (sessão irmã, nunca tocada pelo logout de A).

**Comando**:
```bash
curl -i -b cookie-b.txt -X POST http://localhost:3000/v1/auth/refresh
```

**Resultado esperado**: `HTTP 201` — sessão B continua válida.

**O que observar**: este é o ponto mais importante do MAT — se B também tivesse sido revogada,
seria a regressão do bug de "família varrida por engano" encontrado durante a implementação.

## 7. Resultado que NÃO deve acontecer

- ✗ Passo 4 retornando `401` (bug de família-varrida-por-engano — regressão crítica se voltar a acontecer).
- ✗ Logout de um token inexistente/já inválido retornando erro (deve ser idempotente).
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

Logout:
```
HTTP/1.1 204 No Content
Set-Cookie: refresh_token=; Path=/v1/auth; Expires=Thu, 01 Jan 1970 00:00:00 GMT; HttpOnly; SameSite=Lax
```

Refresh com A pós-logout:
```
HTTP 401
{"error":{"code":"INVALID_REFRESH_TOKEN","message":"Refresh token invalido, expirado ou revogado.","details":[]}}
```

Refresh com B (sessão irmã, intocada):
```
HTTP/1.1 201 Created
Set-Cookie: refresh_token=01a0877a-931f...redacted; ...
{"access_token":"eyJhbGci...redacted","expires_in":900}
```

**Observações**: idempotência (`POST /v1/auth/logout` com token já inválido não é erro) está
coberta pelo teste e2e automatizado (`auth.e2e-spec.ts`), não repetida manualmente aqui — não
agrega evidência nova, é o mesmo código já validado.

## 9. Validação Manual do Responsável

> **Não preencher automaticamente.** Esta seção é responsabilidade do responsável pelo projeto,
> preenchida após executar de verdade os passos da seção 6.

- **Executor**: _______________________________
- **Data**: _______________________________
- **Ambiente**: _______________________________
- **Resultado**: [ ] PASSOU  [ ] FALHOU  [ ] BLOQUEADO

**Passos executados:**
- [ ] Passo 1 — Criar duas sessões
- [ ] Passo 2 — Logout da sessão A
- [ ] Passo 3 — Confirmar que A foi revogada
- [ ] Passo 4 — Confirmar que B não foi afetada

**Observações:**

_______________________________

**Evidências** (screenshot / vídeo / log / outro):

_______________________________

## 10. Critério de Aceite

- 🟢 **PASSOU** — o comportamento observado manualmente corresponde integralmente ao esperado em cada passo da seção 6, sem nenhuma ocorrência da seção 7.
- 🔴 **FALHOU** — qualquer resultado da seção 7 ocorreu, especialmente o Passo 4 retornando `401`.
- 🟡 **BLOQUEADO** — o teste não pôde ser executado por problema de ambiente, dependência ou pré-requisito.

> **Importante**: "Resultado da IA = PASSOU" (seção 8) **não** significa automaticamente
> "Validação manual = PASSOU" (seção 9).

## 11. Histórico

| Data | Executor | Tipo | Resultado |
|---|---|---|---|
| 2026-09-09 | Claude (Sonnet 5) | IA | PASSOU |
| _(a preencher)_ | _(responsável pelo projeto)_ | Manual | PENDENTE |
