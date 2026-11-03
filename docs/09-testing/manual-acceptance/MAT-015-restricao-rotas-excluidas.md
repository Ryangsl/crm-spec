# MAT-015 — Restrição por horário: rotas explicitamente excluídas (D-082)

## 1. Identificação

| Campo | Valor |
|---|---|
| ID | MAT-015 |
| Fase / incremento | 4 / F4.7 |
| Prioridade | MÉDIA |
| Tipo | Funcional (documenta o escopo e as lacunas conhecidas) |
| Requisitos relacionados | BR-27 |
| Decisions relacionadas | [D-082](../../00-governance/decision-register.md#d-082--restrição-por-horário-comercial-e-liberação-excepcional-vn-07-vn-08) (PN-2, PN-3), [D-083](../../00-governance/decision-register.md#d-083--exceções-de-acesso-modelo-técnico-e-critério-de-identificação-td-05-td-14) |
| Ambiente | Ambiente de testes (API, banco descartável), relógio real |

## 2. Objetivo

Confirmar que o guard **por rota** não afeta as rotas **explicitamente excluídas** da cobertura inicial — importação e conversão de Leads, `lead-sources` e as rotas de settings/auth/perfil/disponibilidade/notificações — e **registrar com evidência as lacunas conhecidas (PN-3)**: módulos como Clientes, Oportunidades e Tarefas **não** são protegidos pela restrição. Este MAT **não afirma proteção** onde ela não existe.

## 3. Escopo

**Cobre**: `POST /v1/leads/import`, `POST /v1/leads/{id}/convert`, `GET /v1/lead-sources`, `GET /v1/users/me`, `GET /v1/access-status`, disponibilidade e notificações; contraste com uma rota coberta.

**Não cobre**: a decisão de ampliar a cobertura (futura, fora do F4.7); as rotas cobertas ([MAT-010](MAT-010-restricao-acesso-dentro-fora-horario.md)).

## 4. Pré-requisitos

[F4-7-preparacao-do-ambiente.md](F4-7-preparacao-do-ambiente.md). **Estado**: horário `$HORARIO_FORA`, restrição **ligada**, **nenhuma liberação vigente** (revogue as do [MAT-012](MAT-012-restricao-liberacao-excepcional.md)). Um segundo lead para converter (o `LEAD_ID` do preparo serve; a conversão altera seu status para `converted`).

## 5. Dados de teste

Vendedor (sujeito à restrição). Para `lead-sources`, o Vendedor de fábrica **não** tem `lead_sources:read`: crie um papel personalizado `mat-restrito-fontes` (`leads:read`, `lead_sources:read`, `business_hours:restricted`) por `POST /v1/roles` (Admin) e um usuário `fontes@a.mat.test` com ele — esse usuário também é sujeito à restrição.

## 6. Tutorial de execução manual

`AUTH_V="Authorization: Bearer $TK_VENDEDOR"`; `AUTH_F` com o token do usuário `fontes@a.mat.test`.

### Passo 1 — Importação de Leads continua permitida
**Perfil**: Vendedor. `printf 'name,email\nMaria MAT,maria@mat.test\n' > mat_leads.csv` e
`curl -i -X POST $API/v1/leads/import -H "$AUTH_V" -F "source_id=$SRC_ID" -F "file=@mat_leads.csv;type=text/csv"`.
**Esperado**: **`201`**, `{"total":1,"created":1,"skipped":0,"errors":[]}` (não `403 OUTSIDE_BUSINESS_HOURS`).

### Passo 2 — Conversão de Lead continua permitida
**Perfil**: Vendedor. `curl -i -X POST $API/v1/leads/$LEAD_ID/convert -H "$AUTH_V" -H "Content-Type: application/json" -d '{"customer":{"name":"Cliente MAT"}}'`.
**Esperado**: `201`, lead com `status = "converted"` e `customer_id` (não `403` de horário).

### Passo 3 — `lead-sources`
**Perfil**: `fontes@a.mat.test`. `GET $API/v1/lead-sources` → **`200`**; no mesmo usuário `GET /v1/leads` → **`403 OUTSIDE_BUSINESS_HOURS`** (contraste: o mesmo usuário sujeito).
**Nota**: com o Vendedor de fábrica, `GET /v1/lead-sources` dá `403 FORBIDDEN` por **falta de permissão**, não por horário.

### Passo 4 — Rotas de perfil, status, disponibilidade e notificações
**Perfil**: Vendedor. `GET /v1/users/me`, `GET /v1/access-status`, `GET /v1/availability/me`, `GET /v1/notifications/unread-count` → **`200`** em todas.

### Passo 5 — Lacunas conhecidas (PN-3): módulos não protegidos
**Perfil**: Vendedor (fora do horário, sem liberação). `GET /v1/customers`, `GET /v1/opportunities`, `GET /v1/tasks`.
**Esperado (estado atual, lacuna documentada)**: **`200`** — esses módulos **não** estão cobertos pela restrição inicial (também notas, compromissos, interações, timeline). Registre o resultado como **observação**, não como falha: é a cobertura aprovada em D-082.

### Passo 6 — Contraste com a rota coberta
**Perfil**: Vendedor. `GET /v1/leads` → `403 OUTSIDE_BUSINESS_HOURS`.

## 7. Resultado que NÃO deve acontecer

- ✗ `403 OUTSIDE_BUSINESS_HOURS` em importação, conversão, `lead-sources`, `users/me`, `access-status`, disponibilidade ou notificações.
- ✗ A documentação ou a interface afirmarem que Clientes, Oportunidades, Tarefas, notas, interações ou timeline são protegidos pela restrição.
- ✗ `500` em qualquer passo.
- ✗ A rota coberta (`/v1/leads`) deixar de bloquear no Passo 6.

---

## 8. Resultado da IA — Execução anterior

> Evidência histórica de execução pela IA. **Não é validação manual do responsável.**

| Campo | Valor |
|---|---|
| Executor | Claude (Sonnet 5.5) |
| Data | 2026-10-19 (≈ 15:51 UTC) |
| Ambiente | Backend do `main` pós-merge (crm-backend `20ec912`), banco descartável `crm_mat_f47` |
| Método | Requisições HTTP reais por script + execução complementar com papel personalizado; 11 passos |
| Resultado | **PASSOU** (após correção do roteiro: ver observação sobre `lead-sources`) |

**Evidências:**
```
vendedor POST /leads/import           -> 201 {"total":1,"created":1,"skipped":0,"errors":[]}
vendedor POST /leads/{id}/convert     -> 201 {"status":"converted","customer_id":"01a154db-efd0-...",...}
vendedor GET /users/me · /access-status · /availability/me · /notifications/unread-count -> 200
vendedor GET /customers · /opportunities · /tasks  -> 200  (lacuna PN-3: nao protegidos)
vendedor GET /leads                   -> 403 OUTSIDE_BUSINESS_HOURS
vendedor (fabrica) GET /lead-sources  -> 403 FORBIDDEN  (permissao, nao horario)
fontes@a.mat.test (papel personalizado, sujeito): access-status {"applies_to_me":true,"access":{"leads":false,"conversations":false}}
  GET /leads -> 403 OUTSIDE_BUSINESS_HOURS · GET /lead-sources -> 200 · GET /users/me -> 200 · GET /access-status -> 200
```
**Observações**: a primeira versão do roteiro esperava `200` em `lead-sources` com o Vendedor de fábrica; a execução mostrou `403 FORBIDDEN` por falta de `lead_sources:read`, e o roteiro foi corrigido para usar o papel personalizado (a execução complementar está acima). Não foram exercitadas notas, compromissos, interações e timeline (mesma lacuna PN-3, sem evidência própria neste MAT).

## 9. Validação Manual do Responsável

> **Não preencher automaticamente.** Responsabilidade do responsável pelo projeto, após executar de verdade os passos da seção 6. A execução técnica assistida por IA (2026-10-19) está registrada no [relatório consolidado](../execucao-assistida-f4-7.md), na seção 8 e no Histórico, e **não substitui** esta validação.

- **Executor**: _______________________________
- **Data**: _______________________________
- **Ambiente**: _______________________________
- **Resultado**: [ ] PASSOU  [ ] FALHOU  [ ] BLOQUEADO

**Passos executados:**
- [ ] 1 Importação · [ ] 2 Conversão · [ ] 3 `lead-sources` (com papel personalizado) · [ ] 4 Perfil/status/disponibilidade/notificações · [ ] 5 Lacunas PN-3 · [ ] 6 Contraste

**Observações:**

_______________________________

**Evidências** (log / saída dos comandos / screenshots):

_______________________________

## 10. Critério de Aceite

- 🟢 **PASSOU** — comportamento manual igual ao esperado em cada passo, sem nenhuma ocorrência da seção 7. O Passo 5 é registro da lacuna conhecida, não critério de falha.
- 🔴 **FALHOU** — qualquer resultado da seção 7 ocorreu.
- 🟡 **BLOQUEADO** — não foi possível executar por ambiente, dependência ou fixture.

> **Importante**: "Resultado da IA = PASSOU" **não** significa "Validação manual = PASSOU". Este MAT está **executado pela IA, não aceito**.

## 11. Histórico

| Data | Executor | Tipo | Resultado |
|---|---|---|---|
| 2026-10-19 | Claude (Sonnet 5.5) | IA | PASSOU |
| 2026-10-19 | Claude (Sonnet 5.5) | IA (reexecução técnica assistida em banco novo; ver [relatório](../execucao-assistida-f4-7.md)) | PASSOU |
| _(a preencher)_ | _(responsável pelo projeto)_ | Manual | PENDENTE |
