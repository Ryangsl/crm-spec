# MAT-016 — Restrição por horário: disponibilidade e distribuição de Leads não são alteradas

## 1. Identificação

| Campo | Valor |
|---|---|
| ID | MAT-016 |
| Fase / incremento | 4 / F4.7 (regressão de F4.2, F4.3 e F4.5) |
| Prioridade | ALTA |
| Tipo | Regressão funcional |
| Requisitos relacionados | BR-05, BR-14, BR-27, BR-31 |
| Decisions relacionadas | [D-071](../../00-governance/decision-register.md#d-071--disponibilidade-de-consultoratendente-para-distribuição-automática), [D-078](../../00-governance/decision-register.md#d-078--distribuição-automática-de-leads-com-disponibilidade-td-11), [D-082](../../00-governance/decision-register.md#d-082--restrição-por-horário-comercial-e-liberação-excepcional-vn-07-vn-08) |
| Ambiente | Ambiente de testes (API, banco descartável), relógio real |

## 2. Objetivo

Confirmar que a restrição por horário **não altera** a disponibilidade (D-071) nem a distribuição automática de Leads (D-078): o consultor `Disponível` fora do horário continua elegível e recebe o Lead; o estado e o histórico de disponibilidade não mudam por causa do horário nem do toggle; a notificação `lead.assigned` continua sendo gerada. Registra também a **consequência conhecida**: o consultor recebe um Lead que não consegue abrir fora do horário.

## 3. Escopo

**Cobre**: `PUT /v1/tenant-settings/availability`, `PUT/GET /v1/availability/me`, criação de Lead sem dono (round-robin), notificações, e o efeito do toggle sobre o estado.

**Não cobre**: a lógica completa de elegibilidade e a matriz de estados (testes de F4.2/F4.3); entrega de notificações em tempo real (polling de 30 s no frontend).

## 4. Pré-requisitos

[F4-7-preparacao-do-ambiente.md](F4-7-preparacao-do-ambiente.md). **Estado**: horário `$HORARIO_FORA`, restrição **ligada**, **nenhuma liberação vigente**. O Vendedor de fábrica tem `availability:update`; o Gerente cria o Lead (isento).

## 5. Dados de teste

Vendedor `vendedor@a.mat.test` (único `Disponível`), Gerente, Admin. Para o resultado ser determinístico, mantenha **apenas o Vendedor `Disponível`** entre os elegíveis (quem tem `leads:update`): os demais usuários do tenant devem estar sem registro de disponibilidade (= `Indisponível`).

## 6. Tutorial de execução manual

### Passo 1 — Ligar a disponibilidade no tenant e colocar o Vendedor `Disponível`
**Perfil**: Admin: `PUT $API/v1/tenant-settings/availability -d '{"enabled":true}'` → `200`. **Perfil**: Vendedor: `PUT $API/v1/availability/me -d '{"status":"available"}'` → `200` (rota própria, **não** restrita pelo horário).
(banco descartável) registre o estado e o histórico antes: `SELECT (SELECT status FROM user_availability WHERE user_id='<UID_VENDEDOR>'), (SELECT count(*) FROM availability_log);` → `available | 1`.

### Passo 2 — Distribuição fora do horário
**Perfil**: Gerente: `curl -X POST $API/v1/leads -H "Authorization: Bearer $TK_GERENTE" -H "Content-Type: application/json" -d "{\"source_id\":\"$SRC_ID\",\"name\":\"MAT Lead distribuido\"}"` (**sem** `owner_id`).
**Esperado**: `201`; `owner_id` = id do Vendedor (round-robin entre os elegíveis `Disponíveis`), **mesmo fora do horário** e com a restrição ligada. **Evidência**: corpo do lead.

### Passo 3 — Notificação `lead.assigned` continua sendo gerada
**Perfil**: Vendedor: `GET $API/v1/notifications/unread-count` → `200` com `count` incrementado em 1 em relação a antes do Passo 2.

### Passo 4 — Consequência conhecida: o Lead atribuído não abre fora do horário
**Perfil**: Vendedor: `GET $API/v1/leads/<id do lead do Passo 2>` → `403 OUTSIDE_BUSINESS_HOURS`. **Registre** como comportamento conhecido (D-082: a distribuição não foi alterada; o Vendedor pode pedir uma liberação). **Não é falha.**

### Passo 5 — Disponibilidade intacta
**Perfil**: Vendedor: `GET $API/v1/availability/me` → `{"enabled":true,"status":"available",...}` com o **mesmo** `since` do Passo 1. (banco descartável) a consulta do Passo 1 devolve o **mesmo** `available | 1` (sem novas linhas de histórico).

### Passo 6 — Ligar/desligar a restrição não mexe na disponibilidade
**Perfil**: Admin: `PUT …/business-hours-restriction {"enabled":false}` e depois `{"enabled":true}` → `200` em ambos. A consulta do Passo 1 continua devolvendo `available | 1`.

## 7. Resultado que NÃO deve acontecer

- ✗ O consultor `Disponível` deixar de receber Lead fora do horário (o horário **não** filtra a distribuição).
- ✗ Qualquer mudança automática no estado de disponibilidade ou novas linhas em `availability_log` causadas pelo horário ou pelo toggle.
- ✗ A notificação `lead.assigned` deixar de ser gerada.
- ✗ A restrição bloquear `PUT /v1/availability/me`, `GET /v1/availability/me` ou as notificações.
- ✗ `500` em qualquer passo.

---

## 8. Resultado da IA — Execução anterior

> Evidência histórica de execução pela IA. **Não é validação manual do responsável.**

| Campo | Valor |
|---|---|
| Executor | Claude (Sonnet 5.5) |
| Data | 2026-10-19 (≈ 15:51 UTC) |
| Ambiente | Backend do `main` pós-merge (crm-backend `20ec912`), banco descartável `crm_mat_f47` |
| Método | Requisições HTTP reais por script + SQL; 9 passos |
| Resultado | **PASSOU** (9 de 9 conforme o esperado) |

**Evidências:**
```
admin PUT /tenant-settings/availability {"enabled":true}   -> 200 {"enabled": true}
vendedor PUT /availability/me {"status":"available"}       -> 200 {"enabled":true,"status":"available","since":"2026-10-19T15:51:02.527Z"}
SQL antes:  available|1
gerente POST /leads (sem owner, fora do horario, restricao ligada) -> 201 ; owner_id == id do vendedor: True
vendedor GET /notifications/unread-count                   -> 200 {"count": 2}   (1 do lead da fixture + 1 do distribuido)
vendedor GET /leads/{id do lead distribuido}               -> 403 OUTSIDE_BUSINESS_HOURS   (consequencia conhecida)
vendedor GET /availability/me                              -> 200 {"status":"available","since":"2026-10-19T15:51:02.527Z"}   (mesmo "since")
SQL depois: available|1 · apos desligar/religar a restricao: available|1
```
**Observações**: o `count: 2` inclui a notificação do lead da fixture (criado com `owner_id` = vendedor); o ponto é o incremento causado pela distribuição. A matriz completa de elegibilidade (estados, flag, múltiplos elegíveis) está nos testes e2e de distribuição, não neste roteiro.

## 9. Validação Manual do Responsável

> **Não preencher automaticamente.** Responsabilidade do responsável pelo projeto, após executar de verdade os passos da seção 6. A execução técnica assistida por IA (2026-10-19) está registrada no [relatório consolidado](../execucao-assistida-f4-7.md), na seção 8 e no Histórico, e **não substitui** esta validação.

- **Executor**: _______________________________
- **Data**: _______________________________
- **Ambiente**: _______________________________
- **Resultado**: [ ] PASSOU  [ ] FALHOU  [ ] BLOQUEADO

**Passos executados:**
- [ ] 1 Disponibilidade e estado inicial · [ ] 2 Distribuição fora do horário · [ ] 3 Notificação · [ ] 4 Consequência conhecida · [ ] 5 Disponibilidade intacta · [ ] 6 Toggle não mexe na disponibilidade

**Observações:**

_______________________________

**Evidências** (log / saída dos comandos / screenshots):

_______________________________

## 10. Critério de Aceite

- 🟢 **PASSOU** — comportamento manual igual ao esperado em cada passo, sem nenhuma ocorrência da seção 7. O Passo 4 é o registro de uma consequência conhecida, não critério de falha.
- 🔴 **FALHOU** — qualquer resultado da seção 7 ocorreu.
- 🟡 **BLOQUEADO** — não foi possível executar por ambiente, dependência ou fixture.

> **Importante**: "Resultado da IA = PASSOU" **não** significa "Validação manual = PASSOU". Este MAT está **executado pela IA, não aceito**.

## 11. Histórico

| Data | Executor | Tipo | Resultado |
|---|---|---|---|
| 2026-10-19 | Claude (Sonnet 5.5) | IA | PASSOU |
| 2026-10-19 | Claude (Sonnet 5.5) | IA (reexecução técnica assistida em banco novo; ver [relatório](../execucao-assistida-f4-7.md)) | PASSOU |
| _(a preencher)_ | _(responsável pelo projeto)_ | Manual | PENDENTE |
