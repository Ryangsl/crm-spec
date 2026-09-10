# MAT-001 — Autenticação: Login

## 1. Identificação

| Campo | Valor |
|---|---|
| ID | MAT-001 |
| Fase | 2 |
| Prioridade | CRÍTICA |
| Tipo | Segurança (Autenticação) |
| Requisitos relacionados | RF-01 |
| ADRs relacionados | [ADR-008](../../adr/ADR-008.md) |
| Decisions relacionadas | [D-005](../../00-governance/decision-register.md#d-005--armazenamento-do-refresh-token), [D-006](../../00-governance/decision-register.md#d-006--topologia-de-domínio-samesite-e-csrf) |

## 2. Objetivo

Validar que `POST /v1/auth/login` autentica com credenciais válidas, rejeita credenciais
inválidas sem distinguir "senha errada" de "e-mail inexistente", e entrega o refresh token
exclusivamente via cookie httpOnly — nunca no corpo da resposta.

## 3. Escopo

**Cobre**: o endpoint `POST /v1/auth/login`, o formato da resposta de sucesso, os atributos do
cookie de refresh token, e a não-distinção entre os dois tipos de credencial inválida.

**Não cobre**: rotação/reuso de refresh token (ver [MAT-002](MAT-002-refresh.md)), tenant
suspenso (ver [MAT-008](MAT-008-tenant-suspended.md)), nem nenhuma tela de login — a Fase 2 não
tem UI ([D-063](../../00-governance/decision-register.md#d-063--fase-2-não-exige-interface-mínima-opção-b)).

## 4. Pré-requisitos

Não presumir que quem for executar já tem o ambiente de pé. Na ordem:

```bash
cd crm-workspace
docker compose up -d          # sobe Postgres + Redis

cd ../crm-backend
npm run db:setup              # migrations + seed
npm run dev                   # API em http://localhost:3000
```

## 5. Dados de teste

Credencial de teste já existente no seed do projeto — não é um secret real, é fixture pública
do ambiente de desenvolvimento:

| Campo | Valor |
|---|---|
| Tenant | "Empresa Exemplo" (ativo) |
| E-mail | `admin@exemplo.crm.local` |
| Senha | `Admin123!` |

## 6. Tutorial de execução manual

### Passo 1 — Login com credenciais válidas

**Ação**: autenticar com o usuário admin do seed.

**Comando**:
```bash
curl -i -X POST http://localhost:3000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@exemplo.crm.local","password":"Admin123!"}'
```

**Resultado esperado**: `HTTP/1.1 201 Created`

**O que observar**:
- corpo contém `access_token` (string) e `expires_in: 900`;
- corpo **não** contém `refresh_token` em nenhum campo;
- cabeçalho `Set-Cookie` presente, com `HttpOnly`, `Path=/v1/auth`, `SameSite=Lax`;
- cookie **sem** `Secure` (ambiente local, `NODE_ENV≠production` — em produção `Secure` é obrigatório).

### Passo 2 — Login com senha incorreta

**Ação**: repetir a chamada com o mesmo e-mail e uma senha errada.

**Comando**:
```bash
curl -i -X POST http://localhost:3000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@exemplo.crm.local","password":"SenhaErrada123!"}'
```

**Resultado esperado**: `HTTP 401`

**O que observar**:
- `error.code` = `INVALID_CREDENTIALS`;
- guardar a mensagem exata (`error.message`) para comparar com o Passo 3.

### Passo 3 — Login com e-mail inexistente

**Ação**: repetir a chamada com um e-mail que não existe em nenhum tenant do banco.

**Comando**:
```bash
curl -i -X POST http://localhost:3000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"naoexiste@nenhumtenant.test","password":"QualquerCoisa123!"}'
```

**Resultado esperado**: `HTTP 401`

**O que observar**:
- `error.code` e `error.message` devem ser **idênticos** aos do Passo 2 — se forem diferentes, o sistema está vazando quais e-mails têm conta.

## 7. Resultado que NÃO deve acontecer

- ✗ `refresh_token` aparecendo em qualquer lugar do corpo JSON.
- ✗ Cookie sem `HttpOnly` (leitura por JavaScript no navegador).
- ✗ Cookie com `Path=/` (seria enviado para toda a API, não só `/v1/auth`).
- ✗ Resposta de "senha errada" diferente de "e-mail inexistente" (vazaria quais e-mails têm conta).
- ✗ `500` em qualquer um dos passos.

---

## 8. Resultado da IA — Execução anterior

> Evidência histórica de execução automatizada pela IA/agente contra um ambiente real. **Não é
> validação manual do responsável** — ver seção 9.

| Campo | Valor |
|---|---|
| Executor | Claude (Sonnet 5) |
| Data | 2026-09-09 |
| Ambiente | `crm-workspace` local (Postgres + Redis reais), backend via `npm run dev` |
| Método | `curl` contra `http://localhost:3000` |
| Resultado | **PASSOU** |

**Evidências:**

Login válido:
```
HTTP/1.1 201 Created
Set-Cookie: refresh_token=01a0877a-1c7b...redacted; Max-Age=604800; Path=/v1/auth; Expires=Wed, 16 Sep 2026 18:42:01 GMT; HttpOnly; SameSite=Lax

{"access_token":"eyJhbGci...redacted","expires_in":900}
```

Senha incorreta:
```
HTTP 401
{"error":{"code":"INVALID_CREDENTIALS","message":"E-mail ou senha invalidos.","details":[]}}
```

E-mail inexistente — mesma resposta exata do caso acima (mesmo `code`, mesma `message`), confirmando a não-distinção.

**Observações**: o valor do cookie foi conferido como opaco e sem estrutura decodificável,
conforme esperado; truncado/redigido acima porque não deve haver token completo registrado em
documentação (ver regra de segurança de evidências no [README](README.md)).

## 9. Validação Manual do Responsável

> **Não preencher automaticamente.** Esta seção é responsabilidade do responsável pelo projeto,
> preenchida após executar de verdade os passos da seção 6.

- **Executor**: _______________________________
- **Data**: _______________________________
- **Ambiente**: _______________________________
- **Resultado**: [ ] PASSOU  [ ] FALHOU  [ ] BLOQUEADO

**Passos executados:**
- [ ] Passo 1 — Login com credenciais válidas
- [ ] Passo 2 — Login com senha incorreta
- [ ] Passo 3 — Login com e-mail inexistente

**Observações:**

_______________________________

**Evidências** (screenshot / vídeo / log / outro):

_______________________________

## 10. Critério de Aceite

- 🟢 **PASSOU** — o comportamento observado manualmente corresponde integralmente ao esperado em cada passo da seção 6, sem nenhuma ocorrência da seção 7.
- 🔴 **FALHOU** — qualquer resultado da seção 7 ocorreu, ou o comportamento esperado de algum passo não foi observado.
- 🟡 **BLOQUEADO** — o teste não pôde ser executado por problema de ambiente, dependência ou pré-requisito (seção 4).

> **Importante**: "Resultado da IA = PASSOU" (seção 8) **não** significa automaticamente
> "Validação manual = PASSOU" (seção 9). São registros independentes — o aceite formal deste MAT
> depende da validação manual, não apenas da execução anterior da IA.

## 11. Histórico

| Data | Executor | Tipo | Resultado |
|---|---|---|---|
| 2026-09-09 | Claude (Sonnet 5) | IA | PASSOU |
| _(a preencher)_ | _(responsável pelo projeto)_ | Manual | PENDENTE |
