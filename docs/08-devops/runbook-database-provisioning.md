# Runbook — Provisionamento do banco e do usuário da aplicação

O CRM Universal **nunca** cria o próprio usuário nem o próprio banco, e **nunca** se conecta como superusuário. Em todo ambiente, um administrador do PostgreSQL (superusuário ou DBA) cria **manualmente**, uma vez, o usuário de aplicação e o banco **antes** da primeira migration. Depois disso, a aplicação e o `prisma migrate deploy` usam só esse usuário. **Nenhum passo deste runbook foi executado em ambiente real.**

## 1. Por que é manual

- O usuário da aplicação não tem `SUPERUSER`, `CREATEDB` nem `CREATEROLE`; logo, não consegue criar usuário nem banco. É intencional: uma falha ou invasão da aplicação não ganha poder administrativo sobre o servidor.
- Os comandos `npm run db:*` do backend são só de desenvolvimento e recusam banco fora da máquina local (`scripts/check-dev-database.js`). Em produção não existe `db:setup`, seed nem `migrate reset`.
- Migrations em produção são etapa explícita do deploy, antes de subir a versão nova ([deployment.md](deployment.md) §4).

## 2. O que criar

| Item | Desenvolvimento local | Produção |
|---|---|---|
| Usuário de aplicação | `crm_dev` | Nome a definir **[Pendente]** (ex.: `crm_app`) |
| Atributos | `LOGIN`, sem `SUPERUSER`, `CREATEDB`, `CREATEROLE`, `REPLICATION`, `BYPASSRLS` | Os mesmos |
| Banco principal | `crm_dev`, dono = usuário de aplicação | Nome a definir **[Pendente]**, dono = usuário de aplicação |
| Banco de testes | `crm_test` (testes automatizados fazem `TRUNCATE`) | **Não existe.** Testes nunca rodam em produção |
| Quem executa | O desenvolvedor, como `postgres` | DBA/superusuário, com autorização e registro da mudança |
| Senha | Só no `.env` local | Gerada na hora, guardada só no gerenciador de segredos da plataforma de deploy ([D-025](../00-governance/decision-register.md#d-025--secrets-management-em-produção)); nunca em arquivo versionado, chat ou nota |

O dono do banco cria tabelas, tipos e índices no schema `public` (PostgreSQL 15+), o que cobre `prisma migrate deploy`. A única extensão usada é a **`citext`** (e-mail sem distinção de caixa, [D-092](../00-governance/decision-register.md#d-092--e-mail-de-usuário-sem-distinção-de-maiúsculas-e-minúsculas-por-empresa)), extensão confiável no PostgreSQL 13+: o **dono do banco** a cria sem ser superusuário, e a migration faz `CREATE EXTENSION IF NOT EXISTS citext`. Se o usuário que aplica as migrations não for o dono do banco, um superusuário roda antes, no banco da aplicação: `CREATE EXTENSION IF NOT EXISTS citext;`.

## 3. SQL (executar como superusuário, um comando por vez)

`CREATE DATABASE` não roda junto com outros comandos na mesma execução do pgAdmin; no `psql`, cada comando já roda sozinho.

```sql
CREATE ROLE <usuario_app> WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD '<senha>';
CREATE DATABASE <banco> OWNER <usuario_app>;
REVOKE ALL ON DATABASE <banco> FROM PUBLIC;
GRANT CONNECT, TEMPORARY ON DATABASE <banco> TO <usuario_app>;
```

Usuário já existente (troca de senha ou correção de atributos):

```sql
ALTER ROLE <usuario_app> WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD '<senha>';
```

Em desenvolvimento, `<usuario_app>` = `crm_dev` e os bancos são `crm_dev` e `crm_test` (repita `CREATE DATABASE`, `REVOKE` e `GRANT` para o `crm_test`). Ver [local-development.md](local-development.md) §3.1.

## 4. Conferência antes da primeira migration

Conectado como o usuário de aplicação:

```sql
SELECT current_database(), current_user, inet_server_port(),
       (SELECT rolsuper FROM pg_roles WHERE rolname = current_user) AS superusuario,
       (SELECT rolcreatedb FROM pg_roles WHERE rolname = current_user) AS createdb;
```

Esperado: o banco e o usuário certos, `superusuario = false` e `createdb = false`. Depois, `npx prisma migrate status` contra o `DATABASE_URL` do ambiente confirma host, porta e banco antes de `npx prisma migrate deploy`.

**Antes da migration `20261107120000_users_email_case_insensitive` (D-092)** num banco com usuários, confira se há contas com o mesmo e-mail (sem distinção de caixa) na mesma empresa. Com resultado vazio, a migration aplica; com linhas, ela para sem alterar nada e cada caso precisa ser resolvido com o responsável (nunca mesclar contas automaticamente):

```sql
SELECT tenant_id, lower(email) AS email, count(*) FROM users GROUP BY 1, 2 HAVING count(*) > 1;
```

## 5. Produção: pontos ainda sem decisão

- Nomes do usuário e do banco. **[Pendente]**
- Separar o usuário que aplica migrations (dono dos objetos) do usuário que a aplicação usa em tempo de execução (só leitura e escrita de dados). Reduz o dano de uma invasão da aplicação, mas exige `GRANT`s e `ALTER DEFAULT PRIVILEGES` e uma `DATABASE_URL` só para o `migrate deploy`. **[Pendente: decisão de arquitetura]**
- Conexão com TLS (`sslmode=require` ou mais estrito) quando o banco não estiver no mesmo host da aplicação. **[Pendente]**
- Regras de acesso do `pg_hba.conf` (só o host da aplicação, com `scram-sha-256`) e `listen_addresses` restrito. **[Pendente]**
- Versão do PostgreSQL de produção (desenvolvimento usa 18; o compose antigo usava 16). **[Pendente]**
- Backup e restore antes da primeira carga real ([D-028](../00-governance/decision-register.md#d-028--retenção-de-backup), [D-029](../00-governance/decision-register.md#d-029--cadência-de-teste-de-restore)).

## 6. Ordem no primeiro deploy

1. Superusuário cria o usuário de aplicação e o banco (seção 3) e confere (seção 4).
2. A senha vai para o gerenciador de segredos; o `DATABASE_URL` do ambiente é montado lá.
3. `npx prisma migrate deploy` como etapa do deploy.
4. Domínios das empresas cadastrados ([runbook-tenant-domains.md](runbook-tenant-domains.md)).
5. Sobe a aplicação.
