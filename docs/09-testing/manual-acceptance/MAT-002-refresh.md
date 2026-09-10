# MAT-002 — Autenticação: Refresh

## 1. Identificação

| Campo | Valor |
|---|---|
| ID | MAT-002 |
| Fase | 2 |
| Prioridade | CRÍTICA |
| Tipo | Segurança (Autenticação/Sessão) |
| Requisitos relacionados | RF-01 |
| ADRs relacionados | [ADR-008](../../adr/ADR-008.md) |
| Decisions relacionadas | [D-056](../../00-governance/decision-register.md#d-056--política-de-reuso-de-refresh-token-família-de-sessões) |

## 2. Objetivo

Validar a rotação do refresh token, a rejeição de refresh sem cookie, e — o ponto mais crítico
desta fase — que **reapresentar um token já rotacionado revoga toda a família de sessões do
usuário**, não só o token reutilizado.

## 3. Escopo

**Cobre**: `POST /v1/auth/refresh` — rotação, ausência de cookie, e a política de
reuso-revoga-família (D-056).

**Não cobre**: o efeito de um **logout normal** sobre outras sessões — esse é o caminho oposto
(reuso pós-logout NÃO deve varrer a família) e está no [MAT-003](MAT-003-logout.md).

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
logada **duas vezes** para gerar duas sessões independentes — chamadas aqui de sessão **A** e
sessão **B**, identificadas pelo cookie `refresh_token` que cada login devolve.

## 6. Tutorial de execução manual

### Passo 1 — Criar a sessão A e rotacioná-la

**Ação**: logar e guardar o cookie; em seguida usá-lo para renovar.

**Comando**:
```bash
# login -> guarda o cookie em cookie-a.txt
curl -i -c cookie-a.txt -X POST http://localhost:3000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@exemplo.crm.local","password":"Admin123!"}'

# refresh usando o cookie A -> sobrescreve cookie-a.txt com o token rotacionado
curl -i -b cookie-a.txt -c cookie-a.txt -X POST http://localhost:3000/v1/auth/refresh
```

**Resultado esperado**: `HTTP/1.1 201 Created` no refresh.

**O que observar**:
- novo `access_token` no corpo;
- o valor do cookie `refresh_token` retornado é **diferente** do valor original do login.

> Antes de continuar, copie o valor do cookie **original** do login (antes da rotação) para um
> arquivo separado (`cookie-a-antigo.txt`) — o Passo 2 precisa dele de propósito, para simular
> reuso.

### Passo 2 — Reusar o token antigo (já rotacionado)

**Ação**: repetir o refresh usando o cookie **antigo** de A (o de antes da rotação do Passo 1).

**Comando**:
```bash
curl -i -b cookie-a-antigo.txt -X POST http://localhost:3000/v1/auth/refresh
```

**Resultado esperado**: `HTTP 401`, `error.code = "INVALID_REFRESH_TOKEN"`.

**O que observar**:
- o refresh deve falhar — reusar um token já rotacionado é o gatilho da política de família (D-056).

### Passo 3 — Refresh sem nenhum cookie

**Ação**: chamar o endpoint sem enviar cookie nenhum.

**Comando**:
```bash
curl -i -X POST http://localhost:3000/v1/auth/refresh
```

**Resultado esperado**: `HTTP 401`, mesmo `error.code` do Passo 2.

**O que observar**: a mensagem deve ser idêntica à do Passo 2 — ausência de cookie tratada como
token inválido, não como um erro diferente (não deve vazar qual é o problema exato).

### Passo 4 — Provar a varredura de família

**Ação**: gerar duas sessões novas do mesmo usuário (C e D), reusar o token já rotacionado de
C, e então checar se D — que nunca foi reutilizado — também foi revogado.

**Comando**:
```bash
# duas sessões novas
curl -i -c cookie-c.txt -X POST http://localhost:3000/v1/auth/login \
  -H "Content-Type: application/json" -d '{"email":"admin@exemplo.crm.local","password":"Admin123!"}'
curl -i -c cookie-d.txt -X POST http://localhost:3000/v1/auth/login \
  -H "Content-Type: application/json" -d '{"email":"admin@exemplo.crm.local","password":"Admin123!"}'

# copiar cookie-c.txt para cookie-c-antigo.txt ANTES do próximo passo
cp cookie-c.txt cookie-c-antigo.txt

# rotaciona C
curl -i -b cookie-c.txt -c cookie-c.txt -X POST http://localhost:3000/v1/auth/refresh

# reusa o C antigo (evidência de reuso comprovado)
curl -i -b cookie-c-antigo.txt -X POST http://localhost:3000/v1/auth/refresh

# tenta usar D, que nunca foi reutilizado
curl -i -b cookie-d.txt -X POST http://localhost:3000/v1/auth/refresh
```

**Resultado esperado**: a última chamada (com D) retorna `HTTP 401`.

**O que observar**: D nunca foi reutilizado, mas cai junto porque o reuso do C antigo (com
`revoked_reason=rotated`) é evidência confiável de comprometimento e revoga **toda a família**
de sessões do usuário — esta é a checagem mais importante do MAT.

## 7. Resultado que NÃO deve acontecer

- ✗ Refresh bem-sucedido reutilizando um token já rotacionado.
- ✗ O cookie novo (rotacionado) ser igual ao antigo.
- ✗ Mensagem de erro diferente entre "sem cookie" e "cookie inválido" (vazaria informação de diagnóstico a um atacante testando o endpoint).
- ✗ A sessão D continuar válida após o reuso comprovado da sessão C (falha da política de família).
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

Rotação:
```
HTTP/1.1 201 Created
Set-Cookie: refresh_token=01a0877a-3d87...redacted  (id novo, diferente do original 01a0877a-1c7b...)
```

Reuso do token antigo:
```
HTTP 401
{"error":{"code":"INVALID_REFRESH_TOKEN","message":"Refresh token invalido, expirado ou revogado.","details":[]}}
```

Sem cookie — mesma resposta exata do reuso acima.

Família varrida (sessão irmã, nunca reutilizada, após reuso comprovado de outra sessão do
mesmo usuário):
```
HTTP 401
{"error":{"code":"INVALID_REFRESH_TOKEN", ...}}
```

**Observações**: o comportamento de "família" foi o motivo pelo qual D-056 precisou distinguir
`revoked_reason` (`rotated` vs. `logout`): reuso pós-**logout** normal não deveria varrer a
família (ver [MAT-003](MAT-003-logout.md)), só reuso pós-**rotação** deveria. Este MAT cobre o
caminho que deve varrer; o MAT-003 cobre o caminho que não deve.

## 9. Validação Manual do Responsável

> **Não preencher automaticamente.** Esta seção é responsabilidade do responsável pelo projeto,
> preenchida após executar de verdade os passos da seção 6.

- **Executor**: _______________________________
- **Data**: _______________________________
- **Ambiente**: _______________________________
- **Resultado**: [ ] PASSOU  [ ] FALHOU  [ ] BLOQUEADO

**Passos executados:**
- [ ] Passo 1 — Criar a sessão A e rotacioná-la
- [ ] Passo 2 — Reusar o token antigo
- [ ] Passo 3 — Refresh sem cookie
- [ ] Passo 4 — Provar a varredura de família

**Observações:**

_______________________________

**Evidências** (screenshot / vídeo / log / outro):

_______________________________

## 10. Critério de Aceite

- 🟢 **PASSOU** — o comportamento observado manualmente corresponde integralmente ao esperado em cada passo da seção 6, sem nenhuma ocorrência da seção 7.
- 🔴 **FALHOU** — qualquer resultado da seção 7 ocorreu, ou o comportamento esperado de algum passo não foi observado. Especial atenção ao Passo 4 — é o mais crítico do MAT.
- 🟡 **BLOQUEADO** — o teste não pôde ser executado por problema de ambiente, dependência ou pré-requisito.

> **Importante**: "Resultado da IA = PASSOU" (seção 8) **não** significa automaticamente
> "Validação manual = PASSOU" (seção 9).

## 11. Histórico

| Data | Executor | Tipo | Resultado |
|---|---|---|---|
| 2026-09-09 | Claude (Sonnet 5) | IA | PASSOU |
| _(a preencher)_ | _(responsável pelo projeto)_ | Manual | PENDENTE |
