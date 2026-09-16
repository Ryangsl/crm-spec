# MAT-006 — RBAC: permissão concedida vs. negada

## 1. Identificação

| Campo | Valor |
|---|---|
| ID | MAT-006 |
| Fase | 2 |
| Prioridade | CRÍTICA |
| Tipo | Segurança (Autorização) |
| Requisitos relacionados | — (RBAC não tem RF numerado próprio; coberto por BR-25/BR-26) |
| ADRs relacionados | — |
| Decisions relacionadas | [D-058](../../00-governance/decision-register.md#d-058--escopo-de-rbac-na-fase-2-e-na-fase-3-apenas-tenant) |

Referências adicionais: [personas.md](../../01-product/personas.md) §1/§3, [BR-25/BR-26](../../02-business/business-rules.md).

## 2. Objetivo

Validar que um usuário sem a permissão atômica exigida recebe `403` de forma consistente
(nunca execução parcial, nunca `500`), e que uma rota sem `@RequirePermissions` (própria do
usuário, como `/me`) continua acessível mesmo sem nenhuma permissão de módulo.

## 3. Escopo

**Cobre**: RBAC no **escopo de tenant** (D-058) — permissão concedida vs. negada dentro do
próprio tenant do usuário.

**Não cobre**: escopo por equipe/filial (`Team`/`Branch`) — explicitamente adiado para a Fase
3+, sem enforcement ativo hoje. Nem isolamento entre tenants — isso é o
[MAT-007](MAT-007-tenant-isolation.md).

## 4. Pré-requisitos

```bash
cd crm-workspace
docker compose up -d

cd ../crm-backend
npm run db:setup
npm run dev
```

Um tenant adicional ("MAT Tenant B") com um usuário cujo único papel **não concede nenhuma
permissão** (nem `users:read`, nem `users:create`) — ver seção 5.

> ⚠️ **Lacuna conhecida**: este fixture **não faz parte** do seed padrão versionado
> (`crm-backend/prisma/seed.ts`) — foi provisionado manualmente durante a execução de
> 2026-09-09 (não há API de criação de tenant nesta fase, D-059). Para reexecutar este MAT do
> zero, é necessário recriar o tenant e o usuário primeiro, replicando a estrutura do tenant
> "Empresa Exemplo" já presente em `prisma/seed.ts` (mesmos campos, outro `id`/`name`, e um
> papel sem nenhuma `permission` associada). Isto não é um comando a inventar aqui — é uma
> lacuna registrada para decisão futura (ex.: promover este fixture para o seed oficial).

## 5. Dados de teste

Tenant "MAT Tenant B" com o usuário `sempermissao@mat-tenant-b.test`, cujo papel não concede
`users:read` nem `users:create` (nenhuma permissão de módulo).

## 6. Tutorial de execução manual

### Passo 1 — Login com o usuário sem permissão

**Ação**: autenticar com `sempermissao@mat-tenant-b.test`.

**Comando**:
```bash
curl -i -X POST http://localhost:3000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"sempermissao@mat-tenant-b.test","password":"<senha do fixture>"}'
```

**Resultado esperado**: `HTTP 201` — guardar o `access_token`.

### Passo 2 — Tentar listar usuários

**Ação**: chamar `GET /v1/users` com o token desse usuário.

**Comando**:
```bash
curl -i http://localhost:3000/v1/users \
  -H "Authorization: Bearer <access_token>"
```

**Resultado esperado**: `HTTP 403`, `error.code = "FORBIDDEN"`.

### Passo 3 — Tentar criar um usuário

**Ação**: chamar `POST /v1/users` com o mesmo token.

**Comando**:
```bash
curl -i -X POST http://localhost:3000/v1/users \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Teste","email":"teste@mat-tenant-b.test","password":"Teste123!"}'
```

**Resultado esperado**: `HTTP 403`, mesmo `error.code`.

### Passo 4 — Confirmar que `/me` continua acessível

**Ação**: chamar `GET /v1/users/me` com o mesmo token.

**Comando**:
```bash
curl -i http://localhost:3000/v1/users/me \
  -H "Authorization: Bearer <access_token>"
```

**Resultado esperado**: `HTTP 200`.

**O que observar**: essa rota não passa por `@RequirePermissions` — precisa funcionar mesmo sem
nenhuma permissão de módulo, porque é o próprio usuário consultando a si mesmo.

## 7. Resultado que NÃO deve acontecer

- ✗ Qualquer execução parcial (ex.: listar mas com dados incompletos) em vez de bloqueio total.
- ✗ `500` em vez de `403`.
- ✗ `401` em vez de `403` (o usuário está autenticado — o problema é permissão, não identidade; confundir os dois códigos dificulta o cliente diferenciar "faça login de novo" de "peça acesso ao seu admin").
- ✗ Passo 4 falhando por falta de permissão de módulo (RBAC mal implementado bloquearia até o próprio usuário se ver).

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

Listar sem `users:read`:
```json
HTTP 403
{"error":{"code":"FORBIDDEN","message":"Forbidden","details":[]}}
```

Criar sem `users:create`:
```json
HTTP 403
{"error":{"code":"FORBIDDEN","message":"Forbidden","details":[]}}
```

`/me` mesmo sem nenhuma permissão de módulo:
```json
HTTP 200
{"id":"01a08779-f5d9...redacted","name":"sempermissao@mat-tenant-b.test","email":"sempermissao@mat-tenant-b.test","status":"active","created_at":"2026-09-09T18:41:52.089Z"}
```

**Observações**: este MAT valida RBAC no escopo de tenant apenas (D-058) — não existe hoje
nenhum cenário de "permissão concedida mas escopo de equipe/filial nega o registro
específico", porque esse enforcement é explicitamente Fase 3+. Quando `Team`/`Branch` ganharem
regra ativa, este MAT precisa de uma seção nova para esse caso.

## 9. Validação Manual do Responsável

> **Não preencher automaticamente.** Esta seção é responsabilidade do responsável pelo projeto,
> preenchida após executar de verdade os passos da seção 6.

- **Executor**: _______________________________
- **Data**: _______________________________
- **Ambiente**: _______________________________
- **Resultado**: [ ] PASSOU  [ ] FALHOU  [ ] BLOQUEADO

**Passos executados:**
- [ ] Passo 1 — Login com o usuário sem permissão
- [ ] Passo 2 — Tentar listar usuários
- [ ] Passo 3 — Tentar criar um usuário
- [ ] Passo 4 — Confirmar que `/me` continua acessível

**Observações:**

_______________________________

**Evidências** (screenshot / vídeo / log / outro):

_______________________________

## 10. Critério de Aceite

- 🟢 **PASSOU** — o comportamento observado manualmente corresponde integralmente ao esperado em cada passo da seção 6, sem nenhuma ocorrência da seção 7.
- 🔴 **FALHOU** — qualquer resultado da seção 7 ocorreu.
- 🟡 **BLOQUEADO** — o teste não pôde ser executado por problema de ambiente, dependência ou pré-requisito (ex.: fixture do Tenant B/usuário sem permissão ainda não existe no seed).

> **Importante**: "Resultado da IA = PASSOU" (seção 8) **não** significa automaticamente
> "Validação manual = PASSOU" (seção 9).

## 11. Histórico

| Data | Executor | Tipo | Resultado |
|---|---|---|---|
| 2026-09-09 | Claude (Sonnet 5) | IA | PASSOU |
| _(a preencher)_ | _(responsável pelo projeto)_ | Manual | PENDENTE |
