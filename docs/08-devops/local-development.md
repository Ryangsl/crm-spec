# Ambiente de Desenvolvimento Local

O desenvolvimento local deve ser simples e funcionar tanto em Windows quanto em Linux, sem depender de serviços de nuvem.

## 1. Requisitos locais

- PostgreSQL nativo (ex.: PostgreSQL 18 no Windows) na porta 5433. **Desde 2026-11-05 é o padrão**: o Postgres saiu do Docker. Ver seção 3.1.
- Docker + Docker Compose, só para o Redis.
- Node.js LTS (versão fixada em `.nvmrc`/`engines` de cada repositório).

## 2. Docker Compose (visão conceitual)

Serviço do `crm-backend` local (o PostgreSQL é o nativo, seção 3.1):

```yaml
services:
  redis:
    image: redis:7
    ports: ["127.0.0.1:6379:6379"]
```

[D-023](../00-governance/decision-register.md#d-023--ambiente-de-desenvolvimento-local) (`DECIDIDO`): backend e frontend rodam via `npm run dev` **fora** de container durante o desenvolvimento ativo (hot reload mais simples e rápido), com Docker reservado à infraestrutura (Postgres/Redis). A aplicação só é containerizada para build/deploy.

## 3. Variáveis de ambiente

Cada repositório mantém um `.env.example` versionado, nunca `.env` com valores reais. Variáveis mínimas esperadas no backend:

```
DATABASE_URL=postgresql://crm_dev:<senha>@localhost:5433/crm_dev?schema=public
TEST_DATABASE_URL=postgresql://crm_dev:<senha>@localhost:5433/crm_test?schema=public
REDIS_URL=redis://localhost:6379
JWT_ACCESS_SECRET=change-me
JWT_REFRESH_SECRET=change-me
JWT_ACCESS_TTL=900
NODE_ENV=development
```

### 3.1 PostgreSQL nativo (padrão)

Porta **5433** (`port` no `postgresql.conf`), usuário de aplicação `crm_dev` e dois bancos de propriedade dele: `crm_dev` (desenvolvimento) e `crm_test` (só testes automatizados, que fazem `TRUNCATE`). Executado como `postgres` (pgAdmin, um comando por vez, ou `psql -h localhost -p 5433 -U postgres -d postgres`):

```sql
CREATE ROLE crm_dev WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD '<senha>';
CREATE DATABASE crm_dev OWNER crm_dev;
CREATE DATABASE crm_test OWNER crm_dev;
REVOKE ALL ON DATABASE crm_dev FROM PUBLIC;
REVOKE ALL ON DATABASE crm_test FROM PUBLIC;
GRANT CONNECT, TEMPORARY ON DATABASE crm_dev TO crm_dev;
GRANT CONNECT, TEMPORARY ON DATABASE crm_test TO crm_dev;
```

A criação é **manual**, por um superusuário, em qualquer ambiente; em produção o procedimento e os pontos pendentes estão em [runbook-database-provisioning.md](runbook-database-provisioning.md). Permissões: só `LOGIN` e a propriedade dos bancos (no PostgreSQL 15+ o dono do banco cria objetos no schema `public`). Sem superusuário, `CREATEDB`, `CREATEROLE` ou `REPLICATION`. A senha fica só no `.env` local.

**Rede e autenticação do PostgreSQL local** (revisão de 06/11/2026):

- `listen_addresses = 'localhost'` no `postgresql.conf`: o banco só aceita conexão da própria máquina. A instalação padrão do Windows vem com `'*'` (todas as interfaces); vale depois de reiniciar o serviço (PowerShell **como administrador**: `Restart-Service postgresql-x64-18`). Conferir: `Get-NetTCPConnection -LocalPort 5433 -State Listen` deve mostrar só `127.0.0.1` e `::1`.
- O `pg_hba.conf` da instalação padrão usa `trust` para `127.0.0.1` e `::1`: qualquer programa da máquina entra como qualquer usuário, inclusive `postgres`, **sem senha**. Recomendado trocar `trust` por `scram-sha-256` nas linhas `host`, **depois** de confirmar que a senha do `postgres` é conhecida (`ALTER ROLE postgres PASSWORD '<senha>'` antes, se preciso), e recarregar (`SELECT pg_reload_conf();`). A senha do `crm_dev` já fica no `.env`.

Os comandos `npm run db:setup`, `db:seed`, `db:migrate` e `db:reset` passam antes por `npm run db:check`, que mostra host, porta e banco e **recusa** banco fora da máquina, com nome de teste ou igual ao `TEST_DATABASE_URL`. Antes da primeira migration, confira também com `npx prisma migrate status`. `db:setup` usa `migrate deploy` e funciona sem CREATEDB; `db:migrate` (`migrate dev`) precisa de banco sombra (CREATEDB ou `shadowDatabaseUrl`), e as migrations do projeto são geradas por `migrate diff`.

O seed cria também os cadastros iniciais ([D-094](../00-governance/decision-register.md#d-094--cadastro-manual-de-lead-e-cadastros-iniciais-da-empresa)) nas duas empresas de exemplo: seis origens de Lead e o Pipeline Padrão com cinco etapas. Rodar de novo não duplica nada.

### 3.2 Endereço da empresa ([D-088](../00-governance/decision-register.md#d-088--identificação-da-empresa-pelo-endereço-de-acesso))

O login identifica a empresa pelo endereço. Em desenvolvimento, o seed cria `exemplo.localhost` (Empresa Exemplo) e `trial.localhost` (Empresa Trial); subdomínios de `localhost` resolvem para a própria máquina sem editar o arquivo hosts. Abra `http://exemplo.localhost:5173`. O frontend chama a API na mesma origem (`VITE_API_URL` vazio) e o proxy do Vite encaminha `/v1` ao backend preservando o `Host`. Não abra `http://localhost:5173` para entrar: `localhost` não é endereço de empresa. Outra empresa de teste precisa de uma linha em `tenant_domains` (ver [runbook-tenant-domains.md](runbook-tenant-domains.md)).

Segredos de provedores externos (telefonia/WhatsApp) só existem a partir da Fase 5. A convenção é prefixar por **capacidade, não por marca** (`TELEPHONY_*`, `WHATSAPP_*`), para que trocar de provedor não exija renomear configuração ([D-024](../00-governance/decision-register.md#d-024--convenção-de-variáveis-de-ambiente-de-provedores), `PROPOSTO`) — coerente com a abstração de canal em [../03-architecture/integrations.md](../03-architecture/integrations.md).

### 3.3 Verificação antes de subir a API

`npm run dev` roda antes `npm run dev:check`: conecta ao PostgreSQL e ao Redis do `.env` (no Redis, um `PING`) e, se algum não responder, não sobe a API e diz o que fazer (serviço do PostgreSQL nativo; `docker compose up -d` para o Redis). Não lê nem grava dados. Com a API já no ar, se o Redis cair, o aviso aparece uma vez a cada 30 s e a volta da conexão é registrada.

## 4. Migrations e seeds

- Migrations via Prisma Migrate, versionadas no repositório `crm-backend`.
- Seed de desenvolvimento cria: um tenant de exemplo, um usuário admin, papéis de fábrica, um pipeline padrão com etapas, uma fila de exemplo — suficiente para exercitar o fluxo ponta a ponta descrito em [../01-product/use-cases.md](../01-product/use-cases.md) sem dado de produção.
- Nunca usar dado real de cliente em seed/ambiente local.

## 5. Health checks locais

- Endpoint `GET /health` (liveness) e `GET /health/ready` (readiness, checando conexão com Postgres/Redis) disponíveis desde o início do backend — mesmo mecanismo usado em produção (ver [deployment.md](deployment.md)).

## 6. Backup e restore (local)

- `pg_dump`/`pg_restore` padrão contra o container Postgres local para reproduzir cenários de bug com dado (sempre sintético/seed, nunca dado real de tenant).

## 7. O que nunca fazer em ambiente local

- Nunca apontar `.env` local para banco de produção.
- Nunca desabilitar checagem de tenant/permissão "só para testar" de um jeito que possa vazar para configuração padrão (ver [../07-backend/coding-standards.md](../07-backend/coding-standards.md) seção 4).
