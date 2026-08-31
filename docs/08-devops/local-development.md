# Ambiente de Desenvolvimento Local

O desenvolvimento local deve ser simples e funcionar tanto em Windows quanto em Linux, sem depender de serviços de nuvem.

## 1. Requisitos locais

- Docker + Docker Compose (executa PostgreSQL, Redis e, opcionalmente, o próprio backend/frontend).
- Node.js LTS (versão fixada em `.nvmrc`/`engines` de cada repositório).

## 2. Docker Compose (visão conceitual)

Serviços mínimos para `crm-backend` local:

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: crm
      POSTGRES_USER: crm
      POSTGRES_PASSWORD: crm
    ports: ["5432:5432"]
    volumes: ["pgdata:/var/lib/postgresql/data"]

  redis:
    image: redis:7
    ports: ["6379:6379"]

volumes:
  pgdata:
```

O backend/frontend em si podem rodar via `npm run dev` fora de container durante desenvolvimento ativo (hot reload mais simples), com container reservado para infraestrutura (Postgres/Redis) — `[DECISÃO PENDENTE]`: containerizar também app em dev, avaliado quando o setup de cada repositório for criado.

## 3. Variáveis de ambiente

Cada repositório mantém um `.env.example` versionado, nunca `.env` com valores reais. Variáveis mínimas esperadas no backend:

```
DATABASE_URL=postgresql://crm:crm@localhost:5432/crm
REDIS_URL=redis://localhost:6379
JWT_ACCESS_SECRET=change-me
JWT_REFRESH_SECRET=change-me
JWT_ACCESS_TTL=900
NODE_ENV=development
```

Segredos de provedores externos (telefonia/WhatsApp) seguem o mesmo padrão, com nomes prefixados por provedor (`[DECISÃO PENDENTE]`: convenção exata, definida quando o provedor for escolhido — ver [../03-architecture/integrations.md](../03-architecture/integrations.md)).

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
