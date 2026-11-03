# MAT-013 — Restrição por horário: isolamento entre tenants

## 1. Identificação

| Campo | Valor |
|---|---|
| ID | MAT-013 |
| Fase / incremento | 4 / F4.7 |
| Prioridade | CRÍTICA |
| Tipo | Segurança (isolamento multi-tenant) |
| Requisitos relacionados | BR-25, BR-26, BR-27 |
| Decisions relacionadas | [D-082](../../00-governance/decision-register.md#d-082--restrição-por-horário-comercial-e-liberação-excepcional-vn-07-vn-08), [D-083](../../00-governance/decision-register.md#d-083--exceções-de-acesso-modelo-técnico-e-critério-de-identificação-td-05-td-14) |
| Padrão seguido | [MAT-SEC-TENANT-001](MAT-SEC-TENANT-001-template.md) (entidade nova `access_exceptions`) |
| Ambiente | Ambiente de testes (API, banco descartável) com o fixture do tenant B |

## 2. Objetivo

Validar que as **liberações excepcionais**, o **toggle** e o **horário comercial** são isolados por tenant: o tenant B não lista, não revoga nem concede liberações do tenant A; uma liberação de A não libera usuários de B; e o estado de A (ligado) não afeta B.

## 3. Escopo

**Cobre**: `access_exceptions` (listar, revogar, conceder entre tenants), independência do toggle e do horário, acesso a Lead e Conversa de outro tenant.

**Não cobre**: o isolamento das demais entidades (cobertas nos MATs de cada módulo e em [MAT-007](MAT-007-tenant-isolation.md)).

## 4. Pré-requisitos

[F4-7-preparacao-do-ambiente.md](F4-7-preparacao-do-ambiente.md), **inclusive o fixture do Tenant B** (seção 3). **Estado**: tenant A com `$HORARIO_FORA` e restrição ligada; tenant B com a restrição **desligada** e sem horário. Função `grant` do [MAT-012](MAT-012-restricao-liberacao-excepcional.md), seção 4.

## 5. Dados de teste

Tenant A: Gerente, Vendedor (`UID_VENDEDOR`), `LEAD_ID`, `CONV_ID`. Tenant B: `admin@b.mat.test`, `gerente@b.mat.test`, `vendedor@b.mat.test` (`TK_ADMIN_B`, `TK_GERENTE_B`, `TK_VENDEDOR_B`, `UID_VENDEDOR_B`).

## 6. Tutorial de execução manual

### Passo 1 — Criar a liberação no tenant A
`grant $TK_GERENTE all` (Gerente A, por API) → `201`; guarde `EXC_A`.

### Passo 2 — Tenant B não a enxerga
Gerente B: `GET $API/v1/access-exceptions` → `200`, `{"data":[],"page":1,"limit":20,"total":0}`.

### Passo 3 — Tenant B não revoga a liberação de A
Gerente B: `DELETE $API/v1/access-exceptions/$EXC_A` → **`404 NOT_FOUND`** (nunca `403`, que vazaria a existência — BR-26).

### Passo 4 — Tenant B não concede a usuário de A
Gerente B: `POST /v1/access-exceptions` com `user_id = $UID_VENDEDOR` (usuário de A), `scope=all`, motivo e expiração válidos → **`404 NOT_FOUND`**.

### Passo 5 — Outros recursos de A seguem invisíveis a B
Gerente B: `GET $API/v1/leads/$LEAD_ID` e `GET $API/v1/conversations/$CONV_ID` → `404` em ambos.

### Passo 6 — A liberação de A não foi alterada
(banco descartável) `SELECT revoked_at IS NULL FROM access_exceptions WHERE id='<EXC_A>';` → `t`.

### Passo 7 — O toggle e o horário são por tenant
Admin B: `GET /v1/tenant-settings/business-hours-restriction` → `{"enabled":false}` (A está ligado). Vendedor B: `GET /v1/leads` → `200` (B não está restringido).
Admin B aplica `$HORARIO_FORA` e liga a restrição (`200` e `200`).

### Passo 8 — A liberação de A não vaza para B
Vendedor B: `GET /v1/leads` → **`403 OUTSIDE_BUSINESS_HOURS`** (a liberação `all` de A não vale em B). Vendedor A: `GET /v1/leads` → `200` (liberação de A segue valendo em A).

### Passo 9 — Liberação própria de B só vale em B
Gerente B concede `leads` a `$UID_VENDEDOR_B` → `201`. Vendedor B `GET /v1/leads` → `200`.
(banco descartável) `SELECT tenant_id, count(*) FROM access_exceptions GROUP BY 1;` → uma contagem por tenant, sem mistura.

### Passo 10 — Limpeza
Gerente A revoga `EXC_A` → `200`.

## 7. Resultado que NÃO deve acontecer

- ✗ `200`/`201`/`204` em qualquer tentativa cross-tenant (listar, revogar, conceder).
- ✗ `403` em vez de `404` para recurso de outro tenant (vaza existência).
- ✗ Liberação de A fazer o Vendedor B acessar fora do horário (ou o inverso).
- ✗ O toggle ou o horário de um tenant alterar o comportamento do outro.
- ✗ Qualquer campo de A em resposta para B; qualquer alteração em `access_exceptions` de A após as tentativas de B; `500`.

---

## 8. Resultado da IA — Execução anterior

> Evidência histórica de execução pela IA. **Não é validação manual do responsável.**

| Campo | Valor |
|---|---|
| Executor | Claude (Sonnet 5.5) |
| Data | 2026-10-19 (≈ 15:51 UTC) |
| Ambiente | Backend do `main` pós-merge (crm-backend `20ec912`), banco descartável `crm_mat_f47`, tenant B criado por SQL |
| Método | Requisições HTTP reais por script + SQL; 16 passos |
| Resultado | **PASSOU** (16 de 16 conforme o esperado) |

**Evidências:**
```
B GET /access-exceptions            -> 200 {"data":[],"page":1,"limit":20,"total":0}
B DELETE /access-exceptions/{EXC_A} -> 404 {"error":{"code":"NOT_FOUND","message":"Not Found","details":[]}}
B POST  /access-exceptions (usuario de A) -> 404 NOT_FOUND
B GET /leads/{LEAD_A} -> 404 · B GET /conversations/{CONV_A} -> 404
SQL: revoked_at IS NULL (excecao de A) -> t
B toggle -> {"enabled": false}; vendedor B /leads 200 (A ligado)
B horario fora + ligar -> 200/200; vendedor B /leads -> 403 OUTSIDE_BUSINESS_HOURS
vendedor A /leads -> 200 (liberacao de A)
B concede leads ao vendedor B -> 201; vendedor B /leads -> 200
SQL: excecoes por tenant -> tenant A: 5 · tenant B: 1
```
**Observações**: a contagem 5 do tenant A inclui as liberações dos MATs anteriores (todas revogadas/expiradas); o ponto é a **separação** por tenant. Usuários de B foram criados via API; o tenant B e seu admin, por SQL (D-059).

## 9. Validação Manual do Responsável

> **Não preencher automaticamente.** Responsabilidade do responsável pelo projeto, após executar de verdade os passos da seção 6. A execução técnica assistida por IA (2026-10-19) está registrada no [relatório consolidado](../execucao-assistida-f4-7.md), na seção 8 e no Histórico, e **não substitui** esta validação.

- **Executor**: _______________________________
- **Data**: _______________________________
- **Ambiente**: _______________________________
- **Resultado**: [ ] PASSOU  [ ] FALHOU  [ ] BLOQUEADO

**Passos executados:**
- [ ] 1 Criar em A · [ ] 2 B não lista · [ ] 3 B não revoga · [ ] 4 B não concede a A · [ ] 5 Lead/Conversa de A · [ ] 6 A intacta · [ ] 7 Toggle/horário por tenant · [ ] 8 Sem vazamento · [ ] 9 Liberação de B · [ ] 10 Limpeza

**Observações:**

_______________________________

**Evidências** (log / saída dos comandos / screenshots):

_______________________________

## 10. Critério de Aceite

- 🟢 **PASSOU** — comportamento manual igual ao esperado em cada passo, sem nenhuma ocorrência da seção 7.
- 🔴 **FALHOU** — qualquer resultado da seção 7 ocorreu.
- 🟡 **BLOQUEADO** — não foi possível executar por ambiente, dependência ou fixture (ex.: tenant B não provisionado).

> **Importante**: "Resultado da IA = PASSOU" **não** significa "Validação manual = PASSOU". Este MAT está **executado pela IA, não aceito**.

## 11. Histórico

| Data | Executor | Tipo | Resultado |
|---|---|---|---|
| 2026-10-19 | Claude (Sonnet 5.5) | IA | PASSOU |
| 2026-10-19 | Claude (Sonnet 5.5) | IA (reexecução técnica assistida em banco novo; ver [relatório](../execucao-assistida-f4-7.md)) | PASSOU |
| _(a preencher)_ | _(responsável pelo projeto)_ | Manual | PENDENTE |
