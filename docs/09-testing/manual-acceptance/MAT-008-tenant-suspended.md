# MAT-008 — Tenant Suspenso

## 1. Identificação

| Campo | Valor |
|---|---|
| ID | MAT-008 |
| Fase | 2 |
| Prioridade | ALTA |
| Tipo | Segurança (Autenticação/Multi-tenancy) |
| Requisitos relacionados | RF-07 (efeito da suspensão sobre login; não o mecanismo de suspender em si, que é manual — D-059) |
| ADRs relacionados | [ADR-008](../../adr/ADR-008.md) |
| Decisions relacionadas | — |

Implementação de referência: [`TenantsService.assertActive`](../../../../crm-backend/src/modules/tenants/tenants.service.ts).

## 2. Objetivo

Validar que um usuário de um tenant com `status = suspended` não consegue autenticar, com uma
mensagem que diferencia claramente "sua empresa está suspensa" de "credenciais inválidas" —
sem, porém, vazar essa informação antes de confirmar a senha (ordem de checagem).

## 3. Escopo

**Cobre**: o efeito de `tenant.status = suspended` sobre `POST /v1/auth/login`, e a ordem de
checagem (senha antes de status do tenant).

**Não cobre**: como um tenant é suspenso (hoje é manual/assistido — D-059, RF-07), nem
provisionamento de tenant em geral.

## 4. Pré-requisitos

```bash
cd crm-workspace
docker compose up -d

cd ../crm-backend
npm run db:setup
npm run dev
```

Um tenant com `status = suspended` — ver seção 5 e a nota de lacuna abaixo.

> ⚠️ **Lacuna conhecida**: o tenant "MAT Tenant Suspenso" **não faz parte** do seed padrão
> versionado (`crm-backend/prisma/seed.ts`) — foi provisionado manualmente durante a execução
> de 2026-09-09 (não há API de suspensão de tenant nesta fase, D-059). Para reexecutar este MAT
> do zero, é necessário recriar o tenant (com `status = suspended`) e o usuário primeiro,
> replicando a estrutura do tenant "Empresa Exemplo" já presente em `prisma/seed.ts`.
> Registrado como lacuna para decisão futura.

## 5. Dados de teste

Tenant "MAT Tenant Suspenso" (`status: suspended`), usuário `admin@mat-tenant-suspenso.test` / `MatSusp12345!`.

## 6. Tutorial de execução manual

### Passo 1 — Login com credenciais corretas em tenant suspenso

**Ação**: autenticar com as credenciais corretas do usuário do tenant suspenso.

**Comando**:
```bash
curl -i -X POST http://localhost:3000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@mat-tenant-suspenso.test","password":"MatSusp12345!"}'
```

**Resultado esperado**: `HTTP 403`, `error.code = "TENANT_NOT_ACTIVE"`.

**O que observar**: nenhum `access_token`/cookie emitido.

### Passo 2 — Login com senha errada no mesmo tenant suspenso

**Ação**: repetir com a mesma conta e senha errada.

**Comando**:
```bash
curl -i -X POST http://localhost:3000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@mat-tenant-suspenso.test","password":"SenhaErrada123!"}'
```

**Resultado esperado**: `HTTP 401`, `error.code = "INVALID_CREDENTIALS"`.

**O que observar**: este código precisa ser diferente do Passo 1 — mas a checagem de senha
acontece **antes** da checagem de tenant ativo, então quem erra a senha nunca descobre, pela
resposta, que a empresa também está suspensa.

## 7. Resultado que NÃO deve acontecer

- ✗ Login bem-sucedido (qualquer token emitido) para um tenant suspenso.
- ✗ Senha errada de um usuário de tenant suspenso retornando `TENANT_NOT_ACTIVE` em vez de `INVALID_CREDENTIALS` (isso revelaria "a empresa existe e está suspensa" para alguém que nem provou saber a senha).
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

Credenciais corretas, tenant suspenso:
```json
HTTP 403
{"error":{"code":"TENANT_NOT_ACTIVE","message":"Esta empresa nao esta ativa no momento. Contate o suporte.","details":[]}}
```

**Observações**: o Passo 2 (senha errada + tenant suspenso) não foi reexecutado manualmente
naquela rodada — é exatamente o mesmo caminho de código do [MAT-001](MAT-001-login.md)
(checagem de senha primeiro), já provado correto ali; refazer não agregaria evidência nova, só
duplicaria o mesmo teste com um tenant diferente. Fica registrado como próxima verificação caso
a ordem das checagens em `AuthService.login` mude no futuro — **por isso o Passo 2 está no
tutorial da seção 6 mesmo sem evidência própria registrada aqui**, para que a validação manual
o cubra.

## 9. Validação Manual do Responsável

> **Não preencher automaticamente.** Esta seção é responsabilidade do responsável pelo projeto,
> preenchida após executar de verdade os passos da seção 6.

- **Executor**: _______________________________
- **Data**: _______________________________
- **Ambiente**: _______________________________
- **Resultado**: [ ] PASSOU  [ ] FALHOU  [ ] BLOQUEADO

**Passos executados:**
- [ ] Passo 1 — Login com credenciais corretas em tenant suspenso
- [ ] Passo 2 — Login com senha errada no mesmo tenant suspenso

**Observações:**

_______________________________

**Evidências** (screenshot / vídeo / log / outro):

_______________________________

## 10. Critério de Aceite

- 🟢 **PASSOU** — o comportamento observado manualmente corresponde integralmente ao esperado em cada passo da seção 6, sem nenhuma ocorrência da seção 7.
- 🔴 **FALHOU** — qualquer resultado da seção 7 ocorreu.
- 🟡 **BLOQUEADO** — o teste não pôde ser executado por problema de ambiente, dependência ou pré-requisito (ex.: fixture do tenant suspenso ainda não recriado).

> **Importante**: "Resultado da IA = PASSOU" (seção 8) **não** significa automaticamente
> "Validação manual = PASSOU" (seção 9). O Passo 2 em particular só tem evidência de IA
> indireta (ver seção 8) — a validação manual deste passo agrega evidência nova de fato.

## 11. Histórico

| Data | Executor | Tipo | Resultado |
|---|---|---|---|
| 2026-09-09 | Claude (Sonnet 5) | IA | PASSOU |
| _(a preencher)_ | _(responsável pelo projeto)_ | Manual | PENDENTE |
