# MAT-011 — Restrição por horário: precedência das isenções e múltiplos papéis

## 1. Identificação

| Campo | Valor |
|---|---|
| ID | MAT-011 |
| Fase / incremento | 4 / F4.7 |
| Prioridade | CRÍTICA |
| Tipo | Funcional + Segurança (Autorização) |
| Requisitos relacionados | BR-27 |
| Decisions relacionadas | [D-082](../../00-governance/decision-register.md#d-082--restrição-por-horário-comercial-e-liberação-excepcional-vn-07-vn-08) (PN-1), [D-083](../../00-governance/decision-register.md#d-083--exceções-de-acesso-modelo-técnico-e-critério-de-identificação-td-05-td-14) (TD-14) |
| Ambiente | Ambiente de testes (API, banco descartável), relógio real |

## 2. Objetivo

Validar que **a isenção prevalece**: quem tem o marcador de isenção (`business_hours:exempt`) nunca é restringido, mesmo que também tenha o de restrição — inclusive o usuário com **dois papéis** (Vendedor + Gerente) — e que papéis sem nenhum marcador não são restringidos por padrão.

## 3. Escopo

**Cobre**: Admin (que recebe todos os marcadores do seed), Gerente, Supervisor, usuário `multi` (Vendedor + Gerente), Operador (sem marcador) e o contraste com o Vendedor puro; a recusa de conceder liberação a quem não é sujeito.

**Não cobre**: Diretor (isento no seed; sem usuário nos fixtures — mesmo mecanismo do Supervisor); papéis personalizados (precisam de marcador explícito); tenants existentes ([runbook](../../08-devops/runbook-f4-7-tenant-roles.md)).

## 4. Pré-requisitos

[F4-7-preparacao-do-ambiente.md](F4-7-preparacao-do-ambiente.md) (seções 1 a 3). **Estado**: horário `$HORARIO_FORA` aplicado e restrição **ligada** no tenant A (feito pelo Admin como no [MAT-010](MAT-010-restricao-acesso-dentro-fora-horario.md), passos 3 e 8).

## 5. Dados de teste

`admin@exemplo.crm.local`, `gerente@a.mat.test`, `supervisor@a.mat.test`, `multi@a.mat.test` (papéis `vendedor` e `gerente`), `operador@a.mat.test`, `vendedor@a.mat.test`.

## 6. Tutorial de execução manual

### Passo 1 — Confirmar os papéis e marcadores do usuário com dois papéis
**Perfil**: `multi`. **Comando**: `curl -s $API/v1/users/me -H "Authorization: Bearer $TK_MULTI"`.
**Esperado**: `roles` = `["gerente","vendedor"]` e `permissions` contém `business_hours:restricted` **e** `business_hours:exempt` (além de `access_exceptions:manage`). **Evidência**: campos `roles` e `permissions` (recortados).

### Passo 2 — Isentos acessam fora do horário
**Perfis**: Admin, Gerente, Supervisor e `multi`. **Comandos** (um por token): `GET $API/v1/leads`, `GET $API/v1/conversations`, `GET $API/v1/access-status`.
**Esperado**: `200` em todos os acessos. No status: `applies_to_me = false`, `within_business_hours = false`, `access = {"leads":true,"conversations":true}`. **Evidência**: status + corpo do `access-status` de cada perfil.

### Passo 3 — Papel sem marcador não é restringido
**Perfil**: Operador. `GET $API/v1/leads` → `200`; `GET $API/v1/access-status` → `applies_to_me = false`.

### Passo 4 — O Vendedor puro continua restringido (contraste)
**Perfil**: Vendedor. `GET $API/v1/leads` → **`403 OUTSIDE_BUSINESS_HOURS`**.

### Passo 5 — Conceder liberação a quem não é sujeito é rejeitado
**Perfil**: Gerente. **Comando**:
```bash
curl -i -X POST $API/v1/access-exceptions -H "Authorization: Bearer $TK_GERENTE" -H "Content-Type: application/json" \
  -d "{\"user_id\":\"$UID_MULTI\",\"scope\":\"leads\",\"reason\":\"teste\",\"expires_at\":\"<agora+1h em UTC, ex.: 2030-01-01T10:00:00Z>\"}"
```
(use um instante futuro real, com `Z`). **Esperado**: `422`, `error.code = "ACCESS_EXCEPTION_TARGET_NOT_RESTRICTED"` (a liberação não teria efeito). Repita com `UID_OPERADOR` e `UID_GERENTE`: mesmo resultado.

### Passo 6 — Um papel não-isento é o que decide
**Perfil**: Admin. Com `PATCH $API/v1/users/$UID_MULTI -d '{"role_ids":["<id vendedor>"]}'`, deixe `multi` apenas com o papel `vendedor` e repita `GET /v1/leads` com o token de `multi`: **`403 OUTSIDE_BUSINESS_HOURS`** (e `access-status` com `applies_to_me = true`). Restaure com `{"role_ids":["<id vendedor>","<id gerente>"]}` e confirme `200` de novo. As permissões são lidas a cada requisição: o login pode ser refeito, mas não é obrigatório.

## 7. Resultado que NÃO deve acontecer

- ✗ Admin, Gerente, Supervisor ou `multi` receberem `403 OUTSIDE_BUSINESS_HOURS` com a restrição ligada.
- ✗ O usuário com os dois marcadores ser tratado como sujeito (a isenção deve prevalecer).
- ✗ Operador (sem marcador) ser restringido por padrão.
- ✗ O Vendedor puro acessar fora do horário sem liberação.
- ✗ Aceitar a concessão de liberação a quem não é sujeito (`201`).
- ✗ `500` ou `403` de permissão em rotas que o perfil tem direito.

---

## 8. Resultado da IA — Execução anterior

> Evidência histórica de execução pela IA. **Não é validação manual do responsável.**

| Campo | Valor |
|---|---|
| Executor | Claude (Sonnet 5.5) |
| Data | 2026-10-19 (≈ 15:50 UTC) |
| Ambiente | Backend do `main` pós-merge (crm-backend `20ec912`), banco descartável `crm_mat_f47` |
| Método | Requisições HTTP reais por script; 15 passos (Passos 1 a 5) e, em execução complementar no mesmo ambiente, o Passo 6 |
| Resultado | **PASSOU** (15 de 15 nos Passos 1 a 5; Passo 6 conforme o esperado) |

**Evidências:**
```
multi: roles ["gerente","vendedor"] · marcadores ["access_exceptions:manage","business_hours:exempt","business_hours:restricted"]
admin/gerente/supervisor/multi (fora do horario): GET /leads 200 · GET /conversations 200
  access-status -> {"restriction_enabled":true,"applies_to_me":false,"within_business_hours":false,"access":{"leads":true,"conversations":true}}
operador GET /leads -> 200
vendedor GET /leads -> 403 OUTSIDE_BUSINESS_HOURS
gerente POST /access-exceptions (alvo multi) -> 422 ACCESS_EXCEPTION_TARGET_NOT_RESTRICTED
  {"error":{"code":"ACCESS_EXCEPTION_TARGET_NOT_RESTRICTED","message":"O usuario nao esta sujeito a restricao por horario; a liberacao nao teria efeito.","details":[]}}
Passo 6: multi com [vendedor] apenas -> GET /v1/leads 403 OUTSIDE_BUSINESS_HOURS · access-status applies_to_me=true
         PATCH users role_ids=[vendedor] 200 · restaurado [vendedor,gerente] 200 -> GET /v1/leads 200
```
**Observações**: o alvo `operador`/`gerente`/`admin` da concessão foi verificado no [MAT-012](MAT-012-restricao-liberacao-excepcional.md) (passo 23). Diretor não tem usuário nos fixtures.

## 9. Validação Manual do Responsável

> **Não preencher automaticamente.** Responsabilidade do responsável pelo projeto, após executar de verdade os passos da seção 6. A execução técnica assistida por IA (2026-10-19) está registrada no [relatório consolidado](../execucao-assistida-f4-7.md), na seção 8 e no Histórico, e **não substitui** esta validação.

- **Executor**: _______________________________
- **Data**: _______________________________
- **Ambiente**: _______________________________
- **Resultado**: [ ] PASSOU  [ ] FALHOU  [ ] BLOQUEADO

**Passos executados:**
- [ ] 1 Papéis/marcadores do `multi` · [ ] 2 Isentos acessam · [ ] 3 Papel sem marcador · [ ] 4 Vendedor puro · [ ] 5 Concessão a não sujeito · [ ] 6 Troca de papéis

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
