# Runbook — F4.7: papéis e permissões dos tenants existentes

> **Estado**: escrito e **testado só em banco descartável local** (2026-10-19). **Nunca foi executado em ambiente real.** A execução em tenant real exige autorização explícita, backup recente e a revisão de quem opera o banco. Fonte das regras: [D-082](../00-governance/decision-register.md#d-082--restrição-por-horário-comercial-e-liberação-excepcional-vn-07-vn-08) e [D-083](../00-governance/decision-register.md#d-083--exceções-de-acesso-modelo-técnico-e-critério-de-identificação-td-05-td-14); o mapeamento espelha o `prisma/seed.ts` do `crm-backend`.

## 1. Por que este runbook existe

O `seed.ts` aplica os papéis de fábrica (`FACTORY_ROLES`) somente ao tenant de exemplo. Os papéis de sistema são imutáveis pela API e [D-059](../00-governance/decision-register.md#d-059--provisionamento-de-tenant-permanece-manual-fase-2) mantém o provisionamento manual; portanto, em um tenant **já existente** o F4.7 não funciona até os marcadores e `access_exceptions:manage` serem concedidos aos papéis:

- sem `access_exceptions:manage`, ninguém gere liberações (Admin e Gerente recebem `403`);
- sem `business_hours:restricted`, ninguém é restringido;
- sem `business_hours:exempt`, a precedência da isenção (PN-1) não protege quem acumula `vendedor` com outro papel assim que a restrição for ligada.

**Não rode o `seed.ts` inteiro em ambiente real**: ele também cria/atualiza o tenant "Empresa Exemplo" e um usuário admin com senha conhecida. Use os scripts abaixo, que só **inserem** as linhas necessárias.

**Escopo**: este runbook cobre **apenas** `access_exceptions:manage` e os dois marcadores do F4.7. As permissões `availability:*` (F4.2), `interactions:*` (F4.4) e `conversations:*` (F4.6) dos tenants existentes seguem **sem procedimento escrito**, e a mesma regra vale para elas: em ambiente real, passo manual de dados, nunca o `seed.ts` completo. Aplicar as migrations (`prisma migrate deploy`) e ligar a restrição global do tenant são procedimentos distintos, fora deste runbook.

## 2. O que é concedido (mapeamento)

| Papel de sistema | `access_exceptions:manage` | `business_hours:exempt` | `business_hours:restricted` |
|---|:---:|:---:|:---:|
| `admin` | ✅ | ✅ | ✅ (o seed dá ao `admin` todas as permissões do catálogo; a isenção prevalece) |
| `diretor` | | ✅ | |
| `gerente` | ✅ | ✅ | |
| `supervisor` | | ✅ | |
| `vendedor` | | | ✅ |
| `operador`, `backoffice`, `leitura` e papéis personalizados | | | |

- Os três valores são linhas do catálogo **global** `permissions` (`key` única, sem `tenant_id`); a concessão é por tenant, em `role_permissions` (`role_id`, `permission_id`) dos papéis `roles` com `is_system = true` e `deleted_at IS NULL`.
- A permissão do toggle (`tenant_settings:update`, só `admin`) vem do F4.1 — é pré-requisito, não é concedida aqui.
- **O runbook não liga a restrição** (`crm.business_hours.restriction.enabled`), não cria horário comercial e não cria liberações. Ligar a restrição é uma decisão do Admin do tenant, depois da validação (seção 6).

## 3. Garantias dos scripts

Scripts em [`runbooks/f4-7-tenant-roles/`](runbooks/f4-7-tenant-roles/), para `psql` (PostgreSQL ≥ 13, `\if` exige psql ≥ 10):

| Garantia | Como |
|---|---|
| Só adiciona | `20` e `30` contêm apenas `INSERT … ON CONFLICT DO NOTHING`; nenhum `UPDATE`, `DELETE`, `TRUNCATE` ou `DROP` |
| Idempotente | rodar de novo insere 0 linhas (`INSERT 0 0`) |
| Um tenant por vez | todo filtro usa `tenant_id = :'tenant_id'`; sem a variável o psql falha antes de alterar algo; o catálogo global só ganha 3 linhas que, sozinhas, não dão acesso a ninguém |
| Ordem segura | Fase A (isenções) é commitada **antes** da Fase B (restrição); a Fase B **aborta** se alguma isenção da Fase A faltar |
| Só papéis de sistema | papéis personalizados e papéis excluídos nunca são tocados |
| UUID v7 | as 3 linhas novas de `permissions` usam uma função **temporária** (`pg_temp`, some com a sessão) que gera UUID v7 (D-001/ADR-009); o schema não é alterado |

> Mesmo se a Fase B rodasse sozinha, **ninguém seria bloqueado** enquanto o Admin não ligar a restrição (desligada por padrão) e houver `business_hours` válido. A ordem A → B protege o momento em que ela for ligada e evita a janela em que um usuário com `vendedor` + `gerente` teria só o marcador de restrição.

## 4. Procedimento

### 4.1 Preparação (nada é alterado)

1. Autorização explícita para o ambiente e o tenant; **backup recente** do banco e restore já testado (D-028/D-029).
2. **`prisma migrate deploy` já aplicado** com a migration `20261014120000_f4_7_access_exceptions` (as seções 2 e 3 de `10-pre-checks.sql` confirmam). O `migrate deploy` é uma etapa separada do deploy, não faz parte deste runbook.
3. `psql` com um usuário que possa ler e inserir em `permissions` e `role_permissions`. Nunca registre a connection string em arquivos ou na nota do vault.
4. Listar os tenants e escolher, **explicitamente**, os que serão atualizados:
   ```bash
   psql -v ON_ERROR_STOP=1 -f 00-list-tenants.sql
   ```
5. Para cada tenant, rodar as verificações **antes** e guardar a saída (linha de base):
   ```bash
   psql -v ON_ERROR_STOP=1 -v tenant_id=<UUID> -f 10-pre-checks.sql > pre-<tenant>.txt
   ```
   Conferir: papéis `admin`, `diretor`, `gerente`, `supervisor`, `vendedor` presentes e `is_system = true` (seções 3–4); `admin` com `tenant_settings:update` (5); marcadores ainda ausentes (6); **lista de impacto** — quem passará a ser sujeito à restrição (8) — e usuários com `vendedor` + outro papel, a revisar caso a caso (9). Se algum papel personalizado deveria ser isento, **pare**: isso é decisão do produto (concessão manual separada, fora deste runbook).

### 4.2 Execução (altera dados do tenant)

6. **Fase A — isenções e gestão de liberações**:
   ```bash
   psql -v ON_ERROR_STOP=1 -v tenant_id=<UUID> -f 20-phase-a-exempt.sql
   ```
   Esperado na primeira execução: `INSERT 0 3` (catálogo, só na primeira vez em todo o banco) e `INSERT 0 6` (admin ×2, diretor, gerente ×2, supervisor).
7. Verificar a Fase A: `40-post-checks.sql` — a seção 1 deve listar **apenas** `business_hours:restricted` de `admin` e `vendedor` como `faltando`; nenhuma linha `inesperado`.
8. **Fase B — marcador de restrição** (só depois do passo 7):
   ```bash
   psql -v ON_ERROR_STOP=1 -v tenant_id=<UUID> -f 30-phase-b-restrict.sql
   ```
   Esperado: `INSERT 0 2` (admin e vendedor). Se aparecer `ABORTADO: a FASE A … não está completa`, nada foi alterado: rode a Fase A.
9. Repetir 5–8 para cada tenant escolhido (um por vez).

### 4.3 Validação (nada é alterado)

10. Verificações **depois** (cada tenant):
    ```bash
    psql -v ON_ERROR_STOP=1 -v tenant_id=<UUID> -f 40-post-checks.sql > post-<tenant>.txt
    ```
    Esperado: seção 1 e seção 2 **sem linhas**; seção 3 — o tenant alvo cresceu em `6 + 2 = 8` linhas na primeira execução (quando os cinco papéis de sistema existem) e os **demais tenants ficaram idênticos** à linha de base; seção 4 — `permissoes_nao_f4_7` igual ao antes em cada papel; seção 5 — os usuários `sujeito_a_restricao` são exatamente os da lista de impacto (seção 8 do pré-check); seção 6 — restrição **desligada**; seção 7 — nenhuma liberação criada.
11. **Reexecução**: rodar `20` e `30` de novo deve imprimir `INSERT 0 0` em todos os `INSERT` (idempotência).
12. Validação funcional por API (manual, ainda **não executada**), com contas de teste do tenant e a restrição **desligada**:
    - `GET /v1/users/me` do Gerente inclui `access_exceptions:manage` e `business_hours:exempt`; do Vendedor inclui `business_hours:restricted`;
    - `GET /v1/access-status`: Vendedor `applies_to_me = true`; Admin, Gerente e Supervisor `false`; `restriction_enabled = false`;
    - `GET /v1/access-exceptions` com o Gerente responde `200`; com o Vendedor, `403`.
13. **Ligar a restrição** (`PUT /v1/tenant-settings/business-hours-restriction`, só Admin) **não faz parte deste runbook**: exige `business_hours` válido, comunicação aos vendedores e os MATs do F4.7. Lacunas conhecidas (PN-3) e a consequência de a distribuição de Leads continuar atribuindo a vendedor fora do horário estão em [D-082](../00-governance/decision-register.md#d-082--restrição-por-horário-comercial-e-liberação-excepcional-vn-07-vn-08).

## 5. Reversão

A forma preferida de "desfazer" é **manter (ou desligar) a restrição do tenant**: com `crm.business_hours.restriction.enabled = false` ninguém é restringido, e as linhas concedidas ficam inertes. Só se for preciso remover as concessões, com autorização e fora do horário de uso, o conjunto removido é exatamente o inserido (as três chaves não existiam antes):

```sql
-- NÃO faz parte do procedimento normal. Remove apenas as concessões dos 3 marcadores no tenant informado.
BEGIN;
DELETE FROM role_permissions rp
USING roles r, permissions p
WHERE rp.role_id = r.id AND rp.permission_id = p.id
  AND r.tenant_id = :'tenant_id'
  AND p.key IN ('access_exceptions:manage', 'business_hours:restricted', 'business_hours:exempt');
COMMIT;
```

O catálogo global (`permissions`) não precisa ser revertido.

## 6. Como este runbook foi testado (2026-10-19)

- Banco descartável `crm_runbook_scratch` no container Postgres 16 do projeto (**não** `crm` nem `crm_test`; removido ao final): `prisma migrate deploy` + `seed.ts`, depois a remoção dos 3 marcadores para simular um tenant pré-F4.7, mais um segundo tenant (clone) para provar o isolamento e usuários `vendedor` puro, `vendedor` + `gerente`, `vendedor` + papel personalizado, `vendedor` inativo, `operador` e `supervisor`.
- Resultado: Fase B antes da A **aborta** sem alterar; tenant inexistente **aborta**; sem `tenant_id` falha sem alterar; Fase A `INSERT 0 3` + `0 6`; Fase B `INSERT 0 2`; reexecução `INSERT 0 0`; o tenant B ficou com 187 linhas até ser executado por si (depois 195); pós-checks sem divergências; a lista de impacto (2 usuários) coincidiu com os sujeitos pós-execução; UUIDs gerados têm versão 7.
- **Não testado**: execução em ambiente real, em banco com dados reais de tenants, ou com volume grande; validação funcional por API (passo 12); MATs.
