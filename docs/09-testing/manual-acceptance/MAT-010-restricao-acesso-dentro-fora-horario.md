# MAT-010 — Restrição por horário: acesso dentro e fora do horário (usuário sujeito)

## 1. Identificação

| Campo | Valor |
|---|---|
| ID | MAT-010 |
| Fase / incremento | 4 / F4.7 |
| Prioridade | CRÍTICA |
| Tipo | Funcional + Segurança (Autorização) |
| Requisitos relacionados | BR-27 |
| Decisions relacionadas | [D-082](../../00-governance/decision-register.md#d-082--restrição-por-horário-comercial-e-liberação-excepcional-vn-07-vn-08), [D-083](../../00-governance/decision-register.md#d-083--exceções-de-acesso-modelo-técnico-e-critério-de-identificação-td-05-td-14) |
| Ambiente | Ambiente de testes (API, banco descartável), **relógio real** |

## 2. Objetivo

Validar que o usuário **sujeito à restrição** (Vendedor: marcador de restrição e sem o de isenção) acessa Leads e Conversas dentro do horário comercial e recebe `403 OUTSIDE_BUSINESS_HOURS` — em **leitura e escrita**, sem efeito colateral — fora dele, e que o endpoint de status e o toggle refletem o estado.

## 3. Escopo

**Cobre**: as 8 rotas de Leads cobertas (`GET/POST /leads`, `GET/PATCH/DELETE /leads/{id}`, `qualify`, `disqualify`, `reopen`) e as 8 de Conversas (`POST/GET /conversations`, `GET /conversations/{id}`, `assign`, `close`, `reopen`, `GET/POST …/messages`); `GET /v1/access-status`; a ordem autenticação → permissão → horário.

**Não cobre**: isenções ([MAT-011](MAT-011-restricao-isencoes-multiplos-papeis.md)); liberações ([MAT-012](MAT-012-restricao-liberacao-excepcional.md)); rotas fora da cobertura ([MAT-015](MAT-015-restricao-rotas-excluidas.md)); a interface ([MAT-014](MAT-014-restricao-interface.md)).

## 4. Pré-requisitos

[F4-7-preparacao-do-ambiente.md](F4-7-preparacao-do-ambiente.md) (seções 1 a 3), com `LEAD_ID`, `CONV_ID`, `SRC_ID` criados. Restrição desligada no início. Não executar perto da meia-noite UTC.

## 5. Dados de teste

Vendedor `vendedor@a.mat.test` (sujeito); Operador `operador@a.mat.test` (sem marcador); Admin do seed. Lead `MAT Lead A1` (dono: o vendedor) e uma conversa ligada a ele.

## 6. Tutorial de execução manual

Convenção: `AUTH_V="Authorization: Bearer $TK_VENDEDOR"`, `H="Content-Type: application/json"`.

### Passo 1 — Dentro do horário
**Perfil**: Admin. Aplique `$HORARIO_DENTRO` (`PUT /v1/tenant-settings/business-hours`) e ligue: `PUT /v1/tenant-settings/business-hours-restriction -d '{"enabled":true}'`. **Esperado**: ambos `200`.

### Passo 2 — Vendedor acessa normalmente
**Perfil**: Vendedor. `GET $API/v1/access-status`, `GET $API/v1/leads`, `GET $API/v1/conversations`.
**Esperado**: `200` nos três. O status vem `{"restriction_enabled":true,"applies_to_me":true,"within_business_hours":true,"access":{"leads":true,"conversations":true}}`. **Evidência**: corpo do status + códigos.

### Passo 3 — Fora do horário
**Perfil**: Admin. Aplique `$HORARIO_FORA`. **Esperado**: `200`.

### Passo 4 — Status fora do horário
**Perfil**: Vendedor. `GET $API/v1/access-status`.
**Esperado**: `200`, `{"restriction_enabled":true,"applies_to_me":true,"within_business_hours":false,"access":{"leads":false,"conversations":false}}`.

### Passo 5 — Todas as rotas cobertas bloqueiam (leitura e escrita)
**Perfil**: Vendedor. Execute cada chamada e registre o status:
```bash
curl -i $API/v1/leads                                   -H "$AUTH_V"
curl -i $API/v1/leads/$LEAD_ID                          -H "$AUTH_V"
curl -i -X POST  $API/v1/leads  -H "$AUTH_V" -H "$H" -d "{\"source_id\":\"$SRC_ID\",\"name\":\"NAO DEVE CRIAR\"}"
curl -i -X PATCH $API/v1/leads/$LEAD_ID -H "$AUTH_V" -H "$H" -d '{"name":"NAO DEVE ALTERAR"}'
curl -i -X POST  $API/v1/leads/$LEAD_ID/qualify         -H "$AUTH_V"
curl -i $API/v1/conversations                           -H "$AUTH_V"
curl -i $API/v1/conversations/$CONV_ID                  -H "$AUTH_V"
curl -i $API/v1/conversations/$CONV_ID/messages         -H "$AUTH_V"
curl -i -X POST  $API/v1/conversations/$CONV_ID/messages -H "$AUTH_V" -H "$H" -d '{"content":"NAO DEVE GRAVAR"}'
curl -i -X POST  $API/v1/conversations/$CONV_ID/close   -H "$AUTH_V"
```
**Esperado**: **`403`** com `error.code = "OUTSIDE_BUSINESS_HOURS"` em todas. **Evidência**: status + corpo de cada uma.

### Passo 6 — Nenhuma escrita bloqueada teve efeito
**Comandos** (banco descartável): `SELECT count(*) FROM leads WHERE deleted_at IS NULL;` (igual ao de antes do Passo 5), `SELECT name FROM leads WHERE id='<LEAD_ID>';` (`MAT Lead A1`), `SELECT count(*) FROM messages;` (`0`).

### Passo 7 — Quem não é sujeito não é afetado; a permissão vem antes do horário
**Perfil**: Operador (sem marcador): `GET $API/v1/leads` → `200` mesmo fora do horário. Vendedor: `GET $API/v1/users/me` → `200` (rota fora da restrição). Operador: `POST $API/v1/conversations/$CONV_ID/assign -d '{"user_id":null}'` → **`403 FORBIDDEN`** (falta `conversations:assign`; o erro é de permissão, **não** de horário).

### Passo 8 — Desligar libera e religar volta a bloquear
**Perfil**: Admin `PUT {"enabled":false}` → Vendedor `GET /v1/leads` `200`. Admin `PUT {"enabled":true}` → Vendedor `GET /v1/leads` `403 OUTSIDE_BUSINESS_HOURS`.

## 7. Resultado que NÃO deve acontecer

- ✗ Vendedor (sujeito) acessar qualquer rota coberta fora do horário (`200`/`201`/`204`) com a restrição ligada.
- ✗ Bloqueio dentro do horário ou com o toggle desligado.
- ✗ Qualquer escrita bloqueada alterar dados (lead criado/alterado, mensagem gravada).
- ✗ `500`; `401` no lugar de `403`; ou `403` de horário em vez do `403 FORBIDDEN` de permissão (a permissão é checada antes).
- ✗ `access-status` divergir do comportamento real das rotas.

---

## 8. Resultado da IA — Execução anterior

> Evidência histórica de execução pela IA. **Não é validação manual do responsável.**

| Campo | Valor |
|---|---|
| Executor | Claude (Sonnet 5.5) |
| Data | 2026-10-19 (≈ 15:50 UTC, relógio real; horário "fora" = todos os dias exceto segunda, hoje) |
| Ambiente | Backend do `main` pós-merge (crm-backend `20ec912`) em `http://localhost:3101`, banco descartável `crm_mat_f47` |
| Método | Requisições HTTP reais por script + consultas SQL; 24 passos |
| Resultado | **PASSOU** (24 de 24 conforme o esperado) |

**Evidências:**
```
dentro:  access-status -> 200 {"restriction_enabled":true,"applies_to_me":true,"within_business_hours":true,"access":{"leads":true,"conversations":true}}
         GET /v1/leads 200 · GET /v1/conversations 200
fora:    access-status -> 200 {"restriction_enabled":true,"applies_to_me":true,"within_business_hours":false,"access":{"leads":false,"conversations":false}}
vendedor, fora do horario (todas -> HTTP 403 OUTSIDE_BUSINESS_HOURS):
  GET /v1/leads · GET /v1/leads/{id} · POST /v1/leads · PATCH /v1/leads/{id} · POST /v1/leads/{id}/qualify
  GET /v1/conversations · GET /v1/conversations/{id} · GET …/messages · POST …/messages · POST …/close
SQL: leads antes/depois = 1|1 · nome do lead = "MAT Lead A1" · mensagens gravadas = 0
operador GET /v1/leads -> 200 · vendedor GET /v1/users/me -> 200
operador POST /conversations/{id}/assign -> 403 FORBIDDEN (permissao antes do horario)
toggle off -> vendedor 200; toggle on -> vendedor 403 OUTSIDE_BUSINESS_HOURS
```
**Observações**: os passos `DELETE /leads/{id}`, `disqualify`, `reopen` de Leads, `assign` e `reopen` de Conversas **não** foram chamados manualmente neste roteiro (a cobertura de rota por rota está nos testes e2e, com relógio fixo); `DELETE /leads/{id}` segue sem teste de horário dedicado (observação menor registrada).

## 9. Validação Manual do Responsável

> **Não preencher automaticamente.** Responsabilidade do responsável pelo projeto, após executar de verdade os passos da seção 6. A execução técnica assistida por IA (2026-10-19) está registrada no [relatório consolidado](../execucao-assistida-f4-7.md), na seção 8 e no Histórico, e **não substitui** esta validação.

- **Executor**: _______________________________
- **Data**: _______________________________
- **Ambiente**: _______________________________
- **Resultado**: [ ] PASSOU  [ ] FALHOU  [ ] BLOQUEADO

**Passos executados:**
- [ ] 1 Dentro do horário · [ ] 2 Vendedor acessa · [ ] 3 Fora do horário · [ ] 4 Status fora · [ ] 5 Rotas bloqueadas (10 chamadas) · [ ] 6 Sem efeito colateral · [ ] 7 Não sujeito / permissão antes · [ ] 8 Desligar e religar

**Observações:**

_______________________________

**Evidências** (log / saída dos comandos / screenshots):

_______________________________

## 10. Critério de Aceite

- 🟢 **PASSOU** — comportamento manual igual ao esperado em cada passo da seção 6, sem nenhuma ocorrência da seção 7.
- 🔴 **FALHOU** — qualquer resultado da seção 7 ocorreu.
- 🟡 **BLOQUEADO** — não foi possível executar por ambiente, dependência ou fixture.

> **Importante**: "Resultado da IA = PASSOU" **não** significa "Validação manual = PASSOU". Este MAT está **executado pela IA, não aceito**.

## 11. Histórico

| Data | Executor | Tipo | Resultado |
|---|---|---|---|
| 2026-10-19 | Claude (Sonnet 5.5) | IA | PASSOU |
| 2026-10-19 | Claude (Sonnet 5.5) | IA (reexecução técnica assistida em banco novo; ver [relatório](../execucao-assistida-f4-7.md)) | PASSOU |
| _(a preencher)_ | _(responsável pelo projeto)_ | Manual | PENDENTE |
