# F4.7 — Preparação do ambiente e dos dados dos MATs (MAT-009 a MAT-016)

Preparação **compartilhada** pelos MATs da restrição de acesso por horário comercial e da liberação excepcional ([D-082](../../00-governance/decision-register.md#d-082--restrição-por-horário-comercial-e-liberação-excepcional-vn-07-vn-08)/[D-083](../../00-governance/decision-register.md#d-083--exceções-de-acesso-modelo-técnico-e-critério-de-identificação-td-05-td-14), BR-27). Os MATs apontam para este arquivo na seção 4.

> ⚠️ **Nunca execute estes roteiros contra um banco real.** Eles ligam a restrição de acesso, criam usuários e um segundo tenant e mexem em horário comercial. Use sempre um banco descartável (abaixo). Isto **não** é o runbook de tenants existentes (`../../08-devops/runbook-f4-7-tenant-roles.md`), que tem procedimento próprio, autorização e backup.

## 1. Ambiente

```bash
cd crm-workspace
docker compose up -d                 # Postgres e Redis locais

# banco DESCARTÁVEL (não use "crm" nem "crm_test")
docker exec <container-postgres> psql -U crm -d postgres -c 'CREATE DATABASE crm_mat_f47'

cd ../crm-backend
export DATABASE_URL="postgresql://<usuario>:<senha>@localhost:5432/crm_mat_f47"   # use o usuário/senha do seu .env
npx prisma migrate deploy            # aplica as migrations, inclusive 20261014120000_f4_7_access_exceptions
npm run db:seed                      # tenant "Empresa Exemplo": papéis de fábrica com os marcadores do F4.7
npm run build && PORT=3101 node dist/main.js    # backend de teste em http://localhost:3101
```

O `DATABASE_URL` exportado sobrepõe o do `.env`, então o backend e o seed usam só o banco descartável. Confirme com `curl http://localhost:3101/health` (`200`).

Para os MATs de interface (MAT-014), suba também o frontend apontando para esse backend: `cd crm-frontend && VITE_API_URL=http://localhost:3101 npm run dev` e abra a URL que o Vite imprimir (a CORS do backend aceita `http://localhost:5173` por padrão; se o Vite usar outra porta, inclua-a em `CORS_ORIGINS` ao subir o backend).

## 2. Convenções dos roteiros

```bash
API=http://localhost:3101
login() { curl -s -X POST $API/v1/auth/login -H 'Content-Type: application/json' \
  -d "{\"email\":\"$1\",\"password\":\"$2\"}" | sed -E 's/.*"access_token":"([^"]+)".*/\1/'; }
```

- O token de acesso dura **15 minutos** (`JWT_ACCESS_TTL=900`): se um passo devolver `401`, faça o `login` de novo.
- Senhas dos usuários criados pelos roteiros: `Mat12345!` (fixture de teste). O admin do seed é `admin@exemplo.crm.local` / `Admin123!`.
- **Relógio real.** O backend decide "dentro/fora do horário" pelo relógio da máquina. Os roteiros montam o horário **a partir de agora**: "dentro" = todos os dias 00:00–23:59 UTC; "fora" = todos os dias **menos o de hoje** (UTC). Não execute os roteiros no minuto antes ou depois da meia-noite UTC (23:59–00:01), quando "agora" muda de dia ou fica fora de 00:00–23:59:
  ```bash
  HOJE=$(date -u +%u)                                  # 1=segunda ... 7=domingo
  SEM_HOJE=$(for d in 1 2 3 4 5 6 7; do [ $d -ne $HOJE ] && printf "%s," $d; done | sed 's/,$//')
  HORARIO_DENTRO='{"schema_version":1,"timezone":"UTC","weekly":[{"days":[1,2,3,4,5,6,7],"start":"00:00","end":"23:59"}]}'
  HORARIO_FORA="{\"schema_version\":1,\"timezone\":\"UTC\",\"weekly\":[{\"days\":[$SEM_HOJE],\"start\":\"00:00\",\"end\":\"23:59\"}]}"
  ```
  Aplicar o horário: `curl -s -X PUT $API/v1/tenant-settings/business-hours -H "Authorization: Bearer $TK_ADMIN" -H 'Content-Type: application/json' -d "$HORARIO_FORA"`.
- Os testes automatizados (e2e) cobrem os mesmos cenários com **relógio fixo** (`FixedClock`); o MAT valida o comportamento real, com o relógio real.

## 3. Dados de teste (usuários do tenant de exemplo — "Tenant A")

Com o admin do seed autenticado (`TK_ADMIN=$(login admin@exemplo.crm.local 'Admin123!')`), liste os papéis (`GET /v1/roles`) e anote os ids (UUID v7) de `gerente`, `supervisor`, `vendedor` e `operador`. Crie os usuários com `POST /v1/users` (`name`, `email`, `password`, `role_ids`):

| E-mail | Papéis (`role_ids`) | Perfil nos MATs |
|---|---|---|
| `gerente@a.mat.test` | `gerente` | Gerente (isento; gere liberações; **não** controla o toggle) |
| `supervisor@a.mat.test` | `supervisor` | Supervisor (isento) |
| `vendedor@a.mat.test` | `vendedor` | Vendedor (**sujeito** à restrição) |
| `multi@a.mat.test` | `vendedor` + `gerente` | Múltiplos papéis (a isenção prevalece) |
| `operador@a.mat.test` | `operador` | Operador (sem marcador: não é restringido) |

Faça o login de cada um e guarde `TK_ADMIN`, `TK_GERENTE`, `TK_SUPERVISOR`, `TK_VENDEDOR`, `TK_MULTI`, `TK_OPERADOR`. Anote também `GET /v1/users/me` de cada usuário (campo `id`) como `UID_VENDEDOR`, `UID_MULTI`, `UID_OPERADOR`, `UID_GERENTE`, `UID_ADMIN`.

Dados de CRM (como `gerente`, que é isento):

```bash
SRC_ID=$(curl -s $API/v1/lead-sources -H "Authorization: Bearer $TK_ADMIN" | sed -E 's/.*"data":\[\{"id":"([^"]+)".*/\1/')
LEAD_ID=$(curl -s -X POST $API/v1/leads -H "Authorization: Bearer $TK_GERENTE" -H 'Content-Type: application/json' \
  -d "{\"source_id\":\"$SRC_ID\",\"name\":\"MAT Lead A1\",\"owner_id\":\"$UID_VENDEDOR\"}" | sed -E 's/.*"id":"([^"]+)".*/\1/')
CONV_ID=$(curl -s -X POST $API/v1/conversations -H "Authorization: Bearer $TK_GERENTE" -H 'Content-Type: application/json' \
  -d "{\"lead_id\":\"$LEAD_ID\"}" | sed -E 's/.*"id":"([^"]+)".*/\1/')
```

### Tenant B (isolamento — MAT-013)

> ⚠️ **Lacuna conhecida (D-059)**: não há API de criação de tenant, então o "MAT Tenant B" é criado por SQL no banco descartável (clona os papéis de sistema do tenant A, com UUID v7, e cria `admin@b.mat.test` com a senha do admin de exemplo). O SQL abaixo foi validado em banco descartável em 2026-10-19.

```sql
CREATE FUNCTION pg_temp.uuid_v7() RETURNS text LANGUAGE sql VOLATILE AS $$
  SELECT encode(
    set_bit(set_bit(
      overlay(uuid_send(gen_random_uuid())
              PLACING substring(int8send((extract(epoch FROM clock_timestamp()) * 1000)::bigint) FROM 3)
              FROM 1 FOR 6),
      52, 1), 53, 1),
    'hex')::uuid::text
$$;

BEGIN;
CREATE TEMP TABLE _b AS SELECT pg_temp.uuid_v7() AS tenant_id;

INSERT INTO tenants (id, name, document, plan_id, status, created_at, updated_at)
SELECT b.tenant_id, 'MAT Tenant B', '00000000000999', t.plan_id, t.status, now(), now()
FROM tenants t, _b b WHERE t.document = '00000000000100';

CREATE TEMP TABLE _roles AS
SELECT r.id AS old_id, pg_temp.uuid_v7() AS new_id, r.name, r.is_system
FROM roles r JOIN tenants t ON t.id = r.tenant_id
WHERE t.document = '00000000000100' AND r.deleted_at IS NULL AND r.is_system;

INSERT INTO roles (id, tenant_id, name, is_system, created_at, updated_at)
SELECT m.new_id, b.tenant_id, m.name, m.is_system, now(), now() FROM _roles m, _b b;

INSERT INTO role_permissions (role_id, permission_id)
SELECT m.new_id, rp.permission_id FROM role_permissions rp JOIN _roles m ON m.old_id = rp.role_id;

INSERT INTO users (id, tenant_id, name, email, password_hash, status, created_at, updated_at)
SELECT pg_temp.uuid_v7(), b.tenant_id, 'MAT admin B', 'admin@b.mat.test', u.password_hash, 'active', now(), now()
FROM users u, _b b WHERE u.email = 'admin@exemplo.crm.local';

INSERT INTO user_roles (user_id, role_id)
SELECT u.id, m.new_id FROM users u, _roles m WHERE u.email = 'admin@b.mat.test' AND m.name = 'admin';
COMMIT;
```

Execute com `psql -v ON_ERROR_STOP=1 -d crm_mat_f47 -f <arquivo>.sql`. Depois, como `admin@b.mat.test` / `Admin123!`, crie `gerente@b.mat.test` e `vendedor@b.mat.test` (senha `Mat12345!`) com `POST /v1/users` (ids dos papéis de `GET /v1/roles` **do tenant B**) e guarde `TK_ADMIN_B`, `TK_GERENTE_B`, `TK_VENDEDOR_B` e `UID_VENDEDOR_B`. O tenant B não tem fontes de lead (`GET /v1/lead-sources` vazio).

## 4. Classificação dos MATs do F4.7

| MAT | Tema | Onde pode ser validado | Observação |
|---|---|---|---|
| [MAT-009](MAT-009-restricao-toggle-global.md) | Toggle global (Admin) | Ambiente de testes (API) | Sem UI |
| [MAT-010](MAT-010-restricao-acesso-dentro-fora-horario.md) | Acesso dentro/fora do horário | Ambiente de testes (API) | Relógio real |
| [MAT-011](MAT-011-restricao-isencoes-multiplos-papeis.md) | Isenções e múltiplos papéis | Ambiente de testes (API) | — |
| [MAT-012](MAT-012-restricao-liberacao-excepcional.md) | Liberações excepcionais | Ambiente de testes (API) | Inclui espera de ~20 s |
| [MAT-013](MAT-013-restricao-isolamento-tenant.md) | Isolamento por tenant | Ambiente de testes (API) + fixture do tenant B | Segue o padrão MAT-SEC-TENANT-001 |
| [MAT-014](MAT-014-restricao-interface.md) | Banner e `403` na interface | **Ambiente integrado** (backend + frontend + navegador) | Exige screenshot |
| [MAT-015](MAT-015-restricao-rotas-excluidas.md) | Rotas excluídas (D-082) | Ambiente de testes (API) | Documenta as lacunas PN-3 |
| [MAT-016](MAT-016-restricao-disponibilidade-distribuicao.md) | Disponibilidade e distribuição inalteradas | Ambiente de testes (API) | — |

Nenhum destes MATs deve ser executado em tenant real. A validação em ambiente real (migration, runbook dos tenants existentes e ativação do toggle) é uma etapa operacional **separada**, com autorização e backup.
