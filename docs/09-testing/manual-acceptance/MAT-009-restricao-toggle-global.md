# MAT-009 — Restrição por horário: toggle global (somente Admin)

## 1. Identificação

| Campo | Valor |
|---|---|
| ID | MAT-009 |
| Fase / incremento | 4 / F4.7 |
| Prioridade | ALTA |
| Tipo | Funcional + Segurança (Autorização) |
| Requisitos relacionados | BR-27 |
| Decisions relacionadas | [D-082](../../00-governance/decision-register.md#d-082--restrição-por-horário-comercial-e-liberação-excepcional-vn-07-vn-08), [D-083](../../00-governance/decision-register.md#d-083--exceções-de-acesso-modelo-técnico-e-critério-de-identificação-td-05-td-14) |
| Ambiente | Ambiente de testes (API, banco descartável) |

## 2. Objetivo

Validar que a restrição de acesso por horário é **desligada por padrão**, que **somente o Admin** a liga e desliga, que ligar exige um horário comercial válido (`422 BUSINESS_HOURS_REQUIRED`) e que Gerente e demais perfis não leem nem alteram o toggle.

## 3. Escopo

**Cobre**: `GET/PUT /v1/tenant-settings/business-hours-restriction`; recusa de ativação sem horário válido; idempotência; auditoria; permissões.

**Não cobre**: o efeito do toggle sobre o acesso a Leads e Conversas ([MAT-010](MAT-010-restricao-acesso-dentro-fora-horario.md)); isenções ([MAT-011](MAT-011-restricao-isencoes-multiplos-papeis.md)); a tela do toggle ([MAT-014](MAT-014-restricao-interface.md)); isolamento entre tenants ([MAT-013](MAT-013-restricao-isolamento-tenant.md)).

## 4. Pré-requisitos

Ambiente, convenções e usuários: [F4-7-preparacao-do-ambiente.md](F4-7-preparacao-do-ambiente.md) (seções 1 a 3). Tenant A **sem** horário comercial configurado e com a restrição **ausente** (estado inicial do seed).

## 5. Dados de teste

Perfis: `admin@exemplo.crm.local` (Admin), `gerente@a.mat.test`, `vendedor@a.mat.test`, `supervisor@a.mat.test`, `operador@a.mat.test`, `multi@a.mat.test`. Tokens `TK_*` conforme a preparação.

## 6. Tutorial de execução manual

Em todos os passos: `H="Content-Type: application/json"`; `URL=$API/v1/tenant-settings/business-hours-restriction`.

### Passo 1 — Estado inicial (desligado)
**Perfil**: Admin. **Comando**: `curl -i $URL -H "Authorization: Bearer $TK_ADMIN"`.
**Esperado**: `200`, `{"enabled":false}`. **Evidência**: status + corpo.

### Passo 2 — Ativar sem horário comercial válido
**Perfil**: Admin. **Comando**: `curl -i -X PUT $URL -H "Authorization: Bearer $TK_ADMIN" -H "$H" -d '{"enabled":true}'`.
**Esperado**: `422`, `error.code = "BUSINESS_HOURS_REQUIRED"`. **Evidência**: status + corpo; depois repita o Passo 1: continua `false`.

### Passo 3 — Desligar sem horário é aceito
**Perfil**: Admin. **Comando**: o mesmo `PUT` com `{"enabled":false}`. **Esperado**: `200`, `{"enabled":false}`.

### Passo 4 — Horário comercial inválido é recusado pela API
**Perfil**: Admin. **Comando**:
```bash
curl -i -X PUT $API/v1/tenant-settings/business-hours -H "Authorization: Bearer $TK_ADMIN" -H "$H" \
  -d '{"schema_version":1,"timezone":"UTC","weekly":[{"days":[1],"start":"18:00","end":"09:00"}]}'
```
**Esperado**: `422`, `error.code = "BUSINESS_HOURS_INVALID"` (início deve ser anterior ao fim; janelas que cruzam a meia-noite não são suportadas na v1). O Passo 2 continua valendo (a ativação segue recusada).

### Passo 5 — Ativar com horário válido
**Perfil**: Admin. **Comandos**: aplique `$HORARIO_DENTRO` (preparação, seção 2) em `PUT /v1/tenant-settings/business-hours` e repita o `PUT` do toggle com `{"enabled":true}`.
**Esperado**: horário `200`; toggle `200`, `{"enabled":true}`. **Evidência**: ambos os corpos.

### Passo 6 — Idempotência e formato
**Perfil**: Admin. Repita o `PUT {"enabled":true}` → `200` (sem erro). Envie `{"enabled":"true"}` (texto) → `400 VALIDATION_ERROR` (`enabled must be a boolean value`).

### Passo 7 — Auditoria
**Comando** (no banco descartável): `SELECT count(*) FROM audit_log WHERE entity_type='tenant_settings' AND payload->>'key'='crm.business_hours.restriction.enabled';`
**Esperado**: uma linha por **mudança de valor** (o `PUT true` repetido não audita de novo). Após os Passos 3 e 5: `2`.

### Passo 8 — Perfis sem permissão
**Perfis**: Gerente, Vendedor, Supervisor, Operador e o usuário `multi` (vendedor + gerente). **Comandos**: `GET $URL` e `PUT $URL -d '{"enabled":false}'` com o token de cada um.
**Esperado**: **`403`**, `error.code = "FORBIDDEN"`, em todos os casos (o Gerente **não** controla o toggle global). Sem token: `401`. **Evidência**: status + corpo de cada tentativa.

### Passo 9 — O toggle não foi alterado pelas tentativas
**Perfil**: Admin. `GET $URL` → `{"enabled":true}` (os `PUT false` do Passo 8 foram recusados).

### Passo 10 — Desligar
**Perfil**: Admin. `PUT {"enabled":false}` → `200`; `GET` → `{"enabled":false}`.

## 7. Resultado que NÃO deve acontecer

- ✗ O toggle ligar sem `crm.business_hours` válido.
- ✗ Gerente (ou qualquer perfil que não seja Admin) ler ou alterar o toggle (`200`/`201` em vez de `403`).
- ✗ `500` em qualquer passo; `401` no lugar de `403` para usuário autenticado.
- ✗ A restrição já vir **ligada** em um tenant novo.
- ✗ Mudança de valor sem registro em `audit_log`, ou registro duplicado para um `PUT` idempotente.

---

## 8. Resultado da IA — Execução anterior

> Evidência histórica de execução pela IA. **Não é validação manual do responsável** — ver seção 9.

| Campo | Valor |
|---|---|
| Executor | Claude (Sonnet 5.5) |
| Data | 2026-10-19 |
| Ambiente | Backend do `main` pós-merge (crm-backend `20ec912`, `nest build` local) em `http://localhost:3101`, banco descartável `crm_mat_f47` (Postgres 16) e Redis locais; **não** é ambiente real |
| Método | Requisições HTTP reais por script (Python/`urllib`) + consultas SQL; 23 passos |
| Resultado | **PASSOU** (23 de 23 conforme o esperado) |

**Evidências:**
```
GET toggle (inicial)            HTTP 200 {"enabled": false}
PUT true sem horario            HTTP 422 BUSINESS_HOURS_REQUIRED {"error":{"code":"BUSINESS_HOURS_REQUIRED","message":"Configure um horario de funcionamento valido antes de ativar a restricao por horario.","details":[]}}
PUT horario 18:00-09:00         HTTP 422 BUSINESS_HOURS_INVALID  (weekly[0]: start deve ser anterior a end ...)
PUT true (horario valido)       HTTP 200 {"enabled": true}      PUT true (repetido) HTTP 200
PUT "true" (texto)              HTTP 400 VALIDATION_ERROR (enabled must be a boolean value)
auditoria (SQL)                 2
gerente/vendedor/supervisor/operador/multi: GET e PUT -> HTTP 403 FORBIDDEN  {"error":{"code":"FORBIDDEN","message":"Forbidden","details":[]}}
sem token                       HTTP 401 UNAUTHORIZED
GET apos as tentativas          HTTP 200 {"enabled": true}
PUT false / GET                 HTTP 200 {"enabled": false}
```
**Observações**: o Admin do seed é o único papel de fábrica com `tenant_settings:update` (hoje a regra "só o Admin" vem dessa permissão). Interface do toggle: [MAT-014](MAT-014-restricao-interface.md) (não executado pela IA).

## 9. Validação Manual do Responsável

> **Não preencher automaticamente.** Responsabilidade do responsável pelo projeto, após executar de verdade os passos da seção 6. A execução técnica assistida por IA (2026-10-19) está registrada no [relatório consolidado](../execucao-assistida-f4-7.md), na seção 8 e no Histórico, e **não substitui** esta validação.

- **Executor**: _______________________________
- **Data**: _______________________________
- **Ambiente**: _______________________________
- **Resultado**: [ ] PASSOU  [ ] FALHOU  [ ] BLOQUEADO

**Passos executados:**
- [ ] 1 Estado inicial · [ ] 2 Ativar sem horário · [ ] 3 Desligar sem horário · [ ] 4 Horário inválido · [ ] 5 Ativar com horário · [ ] 6 Idempotência/formato · [ ] 7 Auditoria · [ ] 8 Perfis sem permissão · [ ] 9 Toggle intacto · [ ] 10 Desligar

**Observações:**

_______________________________

**Evidências** (log / saída dos comandos / screenshots):

_______________________________

## 10. Critério de Aceite

- 🟢 **PASSOU** — o comportamento observado manualmente corresponde ao esperado em cada passo da seção 6, sem nenhuma ocorrência da seção 7.
- 🔴 **FALHOU** — qualquer resultado da seção 7 ocorreu.
- 🟡 **BLOQUEADO** — o teste não pôde ser executado por problema de ambiente, dependência ou fixture.

> **Importante**: "Resultado da IA = PASSOU" (seção 8) **não** significa "Validação manual = PASSOU" (seção 9). Este MAT está **executado pela IA, não aceito**.

## 11. Histórico

| Data | Executor | Tipo | Resultado |
|---|---|---|---|
| 2026-10-19 | Claude (Sonnet 5.5) | IA | PASSOU |
| 2026-10-19 | Claude (Sonnet 5.5) | IA (reexecução técnica assistida em banco novo; ver [relatório](../execucao-assistida-f4-7.md)) | PASSOU |
| _(a preencher)_ | _(responsável pelo projeto)_ | Manual | PENDENTE |
