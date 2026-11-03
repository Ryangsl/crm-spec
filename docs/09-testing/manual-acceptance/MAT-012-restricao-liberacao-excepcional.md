# MAT-012 — Restrição por horário: liberação excepcional de acesso

## 1. Identificação

| Campo | Valor |
|---|---|
| ID | MAT-012 |
| Fase / incremento | 4 / F4.7 |
| Prioridade | CRÍTICA |
| Tipo | Funcional + Segurança (Autorização) |
| Requisitos relacionados | BR-27, UC-15 |
| Decisions relacionadas | [D-082](../../00-governance/decision-register.md#d-082--restrição-por-horário-comercial-e-liberação-excepcional-vn-07-vn-08) (A4–A8), [D-083](../../00-governance/decision-register.md#d-083--exceções-de-acesso-modelo-técnico-e-critério-de-identificação-td-05-td-14) (TD-05) |
| Ambiente | Ambiente de testes (API, banco descartável), relógio real |

## 2. Objetivo

Validar a concessão, a listagem e a revogação de liberações excepcionais por **Admin e Gerente**: motivo obrigatório, expiração futura obrigatória (instante RFC 3339 com fuso), escopo (`leads`, `conversations`, `all`), validade por data (início inclusivo, fim exclusivo), **liberações simultâneas em união**, revogação sem afetar as demais e auditoria.

## 3. Escopo

**Cobre**: `POST/GET /v1/access-exceptions`, `DELETE /v1/access-exceptions/{id}`; efeito no acesso do Vendedor; validações do corpo; permissão `access_exceptions:manage`.

**Não cobre**: isolamento entre tenants ([MAT-013](MAT-013-restricao-isolamento-tenant.md)); a tela de liberações ([MAT-014](MAT-014-restricao-interface.md)).

## 4. Pré-requisitos

[F4-7-preparacao-do-ambiente.md](F4-7-preparacao-do-ambiente.md). **Estado**: horário `$HORARIO_FORA` e restrição **ligada**; nenhuma liberação vigente. Defina um utilitário para instantes futuros:
```bash
daqui() { date -u -d "+$1" +%Y-%m-%dT%H:%M:%SZ; }      # ex.: daqui "1 hour"   (GNU date; no macOS: date -u -v+1H ...)
grant() { curl -s -w '\nHTTP %{http_code}\n' -X POST $API/v1/access-exceptions -H "Authorization: Bearer $1" -H "Content-Type: application/json" \
  -d "{\"user_id\":\"$UID_VENDEDOR\",\"scope\":\"$2\",\"reason\":\"${3:-Plantao de fim de semana}\",\"expires_at\":\"${4:-$(daqui '1 hour')}\"}"; }
```

## 5. Dados de teste

Vendedor (sujeito), Gerente e Admin (concedentes), Supervisor/Operador/Vendedor (sem permissão de gestão), alvos não sujeitos (`UID_OPERADOR`, `UID_GERENTE`, `UID_ADMIN`).

## 6. Tutorial de execução manual

### Passo 1 — Vendedor bloqueado antes de qualquer liberação
`GET $API/v1/leads` (Vendedor) → `403 OUTSIDE_BUSINESS_HOURS`.

### Passo 2 — Gerente concede escopo `leads`
`grant $TK_GERENTE leads` → **`201`**; corpo com `scope = "leads"`, `granted_by` = id do Gerente, `starts_at` ≈ agora (início imediato), `expires_at` = o informado, `revoked_at = null`. Guarde `EXC1` (id).
Depois: Vendedor `GET /v1/leads` → `200`; Vendedor `GET /v1/conversations` → **`403 OUTSIDE_BUSINESS_HOURS`** (o escopo não cobre Conversas).

### Passo 3 — Admin concede escopo `conversations` (liberação simultânea)
`grant $TK_ADMIN conversations` → `201` (guarde `EXC2`). Vendedor `GET /v1/conversations` → `200`.

### Passo 4 — Terceira liberação, escopo `all`
`grant $TK_GERENTE all` → `201` (guarde `EXC3`). Há agora 3 liberações vigentes para o mesmo usuário (valem em **união**).

### Passo 5 — Listagem e filtros
Gerente: `GET /v1/access-exceptions` → `200`, `total = 3`, ordem por `starts_at` decrescente. `GET /v1/access-exceptions?active=true` → as 3. `GET /v1/access-exceptions?user_id=$UID_VENDEDOR&limit=1` → 1 item, `total = 3`.

### Passo 6 — Revogar uma liberação não afeta as demais
Gerente: `DELETE /v1/access-exceptions/$EXC3` → `200`, `revoked_at` preenchido. Vendedor `GET /v1/leads` → `200` (EXC1 segue valendo). Repita o `DELETE`: `200` e o **mesmo** `revoked_at` do primeiro (a revogação repetida preserva o primeiro valor).

### Passo 7 — Revogar tudo volta a bloquear
Gerente revoga `EXC1` → Vendedor `GET /v1/leads` → `403 OUTSIDE_BUSINESS_HOURS`; `GET /v1/conversations` ainda `200` (EXC2). Admin revoga `EXC2` → `GET /v1/conversations` → `403 OUTSIDE_BUSINESS_HOURS`.

### Passo 8 — Validações do corpo (nada é gravado)
Gerente, todos com o `grant` ajustado:
| Caso | Esperado |
|---|---|
| motivo vazio (`""`) ou só espaços | `400 VALIDATION_ERROR` |
| motivo com 1.001 caracteres (1.000 é aceito) | `400 VALIDATION_ERROR` |
| `expires_at` no passado (`daqui "-1 minute"`) | `422 ACCESS_EXCEPTION_EXPIRY_INVALID` |
| `expires_at` só com data (`2099-12-31`) | `400 VALIDATION_ERROR` (`expires_at deve ser data e hora com fuso (RFC 3339)…`) |
| `expires_at` sem fuso (`2099-12-31T10:00:00`) | `400 VALIDATION_ERROR` |
| `expires_at` ausente | `400 VALIDATION_ERROR` |
| `scope` inválido (`tudo`) | `400 VALIDATION_ERROR` |
| campo não previsto (`starts_at`, `granted_by`) | `400 VALIDATION_ERROR` |
| alvo não sujeito (Operador, Gerente, Admin) | `422 ACCESS_EXCEPTION_TARGET_NOT_RESTRICTED` |

### Passo 9 — Quem pode gerir
Supervisor, Operador e Vendedor: `POST` e `GET /v1/access-exceptions` → **`403 FORBIDDEN`**. Sem token: `401`.

### Passo 10 — Expiração por data (fim exclusivo)
Gerente: `grant $TK_GERENTE leads "Teste de expiracao" "$(daqui '30 seconds')"` → `201`. Vendedor `GET /v1/leads` imediatamente → `200`; aguarde passar o `expires_at` (+ alguns segundos) e repita → **`403 OUTSIDE_BUSINESS_HOURS`** (sem job: a validade é avaliada na consulta). `GET /v1/access-exceptions?active=false` lista a expirada.

### Passo 11 — Auditoria
(banco descartável) `SELECT action, count(*) FROM audit_log WHERE entity_type='access_exception' GROUP BY 1;` → uma linha `access_exception.granted` por concessão e uma `access_exception.revoked` por **primeira** revogação (a repetida não audita de novo).

## 7. Resultado que NÃO deve acontecer

- ✗ Concessão sem motivo, sem expiração, com expiração no passado ou sem fuso/hora (`201`).
- ✗ Concessão a usuário não sujeito à restrição (`201`).
- ✗ Liberação de escopo `leads` abrir Conversas (ou o inverso); escopo `all` não abrir ambos.
- ✗ Revogar uma liberação invalidar as demais do mesmo usuário; revogação repetida alterar o primeiro `revoked_at`.
- ✗ Liberação expirada ou revogada continuar valendo.
- ✗ Vendedor, Supervisor ou Operador gerir liberações (`2xx`).
- ✗ Concessão/revogação sem registro de auditoria; `500` em qualquer caso.

---

## 8. Resultado da IA — Execução anterior

> Evidência histórica de execução pela IA. **Não é validação manual do responsável.**

| Campo | Valor |
|---|---|
| Executor | Claude (Sonnet 5.5) |
| Data | 2026-10-19 (≈ 15:50 UTC) |
| Ambiente | Backend do `main` pós-merge (crm-backend `20ec912`), banco descartável `crm_mat_f47` |
| Método | Requisições HTTP reais por script + SQL; 38 passos |
| Resultado | **PASSOU** (38 de 38 conforme o esperado) |

**Evidências:**
```
gerente grant leads        -> 201 {"scope":"leads","starts_at":"2026-10-19T15:50:39.556Z","expires_at":"2026-10-19T16:50:39.000Z",...}
vendedor /leads 200 · /conversations 403 OUTSIDE_BUSINESS_HOURS
admin grant conversations  -> 201 · vendedor /conversations 200
gerente grant all          -> 201  (3 liberacoes simultaneas)
GET /access-exceptions 200 · ?active=true 200 · ?user_id=..&limit=1 200
DELETE (all) 200; vendedor /leads 200; DELETE repetido 200 com o mesmo revoked_at = 2026-10-19T15:50:39.817Z
revogar leads -> /leads 403 · /conversations 200 ; revogar conversations -> /conversations 403
motivo "" -> 400 ("reason should not be empty") · "   " -> 400 · 1001 caracteres -> 400
expires_at passado -> 422 ACCESS_EXCEPTION_EXPIRY_INVALID
expires_at "2099-12-31" -> 400 ("expires_at deve ser data e hora com fuso (RFC 3339), ex.: 2026-10-14T23:00:00Z")
expires_at sem fuso -> 400 · scope "tudo" -> 400 · campo starts_at -> 400
alvo operador/gerente/admin -> 422 ACCESS_EXCEPTION_TARGET_NOT_RESTRICTED
vendedor/supervisor/operador: POST e GET /access-exceptions -> 403 FORBIDDEN
expiracao em ~20 s: dentro da validade /leads 200; apos expires_at (15:51:00Z) /leads 403 OUTSIDE_BUSINESS_HOURS
SQL auditoria: access_exception.granted 4 · access_exception.revoked 3 · liberacoes vigentes restantes 0
```
**Observações**: no roteiro da IA a expiração foi de ~20 s (o roteiro manual usa 30 s). A validação de motivo com exatamente 1.000 caracteres (aceito) está nos testes e2e, não neste roteiro.

## 9. Validação Manual do Responsável

> **Não preencher automaticamente.** Responsabilidade do responsável pelo projeto, após executar de verdade os passos da seção 6. A execução técnica assistida por IA (2026-10-19) está registrada no [relatório consolidado](../execucao-assistida-f4-7.md), na seção 8 e no Histórico, e **não substitui** esta validação.

- **Executor**: _______________________________
- **Data**: _______________________________
- **Ambiente**: _______________________________
- **Resultado**: [ ] PASSOU  [ ] FALHOU  [ ] BLOQUEADO

**Passos executados:**
- [ ] 1 Bloqueado antes · [ ] 2 Concede `leads` · [ ] 3 Concede `conversations` · [ ] 4 Concede `all` · [ ] 5 Listagem/filtros · [ ] 6 Revogar uma · [ ] 7 Revogar todas · [ ] 8 Validações do corpo · [ ] 9 Quem pode gerir · [ ] 10 Expiração (30 s) · [ ] 11 Auditoria

**Observações:**

_______________________________

**Evidências** (log / saída dos comandos / screenshots):

_______________________________

## 10. Critério de Aceite

- 🟢 **PASSOU** — comportamento manual igual ao esperado em cada passo, sem nenhuma ocorrência da seção 7.
- 🔴 **FALHOU** — qualquer resultado da seção 7 ocorreu.
- 🟡 **BLOQUEADO** — não foi possível executar por ambiente, dependência ou fixture.

> **Importante**: "Resultado da IA = PASSOU" **não** significa "Validação manual = PASSOU". Este MAT está **executado pela IA, não aceito**.

## 11. Histórico

| Data | Executor | Tipo | Resultado |
|---|---|---|---|
| 2026-10-19 | Claude (Sonnet 5.5) | IA | PASSOU |
| 2026-10-19 | Claude (Sonnet 5.5) | IA (reexecução técnica assistida em banco novo; ver [relatório](../execucao-assistida-f4-7.md)) | PASSOU |
| _(a preencher)_ | _(responsável pelo projeto)_ | Manual | PENDENTE |
