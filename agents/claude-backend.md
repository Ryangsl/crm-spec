# Instruções — Claude no backend (crm-backend)

Este documento é a fonte para o `CLAUDE.md`/`AGENTS.md` que será criado em `crm-backend` na Fase 1 do roadmap ([../docs/10-roadmap/roadmap.md](../docs/10-roadmap/roadmap.md)). Até lá, serve como guia de como um agente Claude deve atuar neste projeto quando trabalhar em backend, banco de dados, arquitetura e documentação.

## Onde Claude atua neste projeto (ver [divisão de agentes](reviewer.md))
- Product discovery e arquitetura (este repositório, `crm-spec`).
- Backend (`crm-backend`): módulos NestJS, regras de negócio, integrações, filas.
- Modelagem de banco de dados (Prisma/PostgreSQL).
- Code review complexo (regra de negócio, segurança, multi-tenancy).

## Antes de implementar qualquer coisa
1. Leia [../docs/01-product/vision.md](../docs/01-product/vision.md) e [../docs/01-product/personas.md](../docs/01-product/personas.md) se a tarefa envolve regra de acesso.
2. Verifique se a entidade/regra já existe em [../docs/04-database/entities.md](../docs/04-database/entities.md) e [../docs/02-business/business-rules.md](../docs/02-business/business-rules.md) antes de criar algo novo.
3. Verifique se o endpoint já existe em [../docs/05-api/openapi.yaml](../docs/05-api/openapi.yaml).
4. Se a tarefa exige uma decisão arquitetural nova (nova tecnologia, mudança de estratégia), crie/atualize um ADR em [../docs/adr/](../docs/adr/) **antes** de implementar.

## Arquitetura (resumo — ver [../docs/07-backend/backend-architecture.md](../docs/07-backend/backend-architecture.md))
- Monólito modular NestJS. Um módulo de negócio = uma pasta em `src/modules/<nome>`.
- Controller → Service → Repository. Regra de negócio só no Service.
- Nenhum módulo acessa Repository de outro módulo — apenas Service público, ou eventos de domínio.
- Toda query passa `tenant_id` do contexto autenticado, nunca de parâmetro do cliente.

## Como testar
- `npm test` para unit; `npm run test:integration` para integração com banco de teste; `npm run test:e2e` para API E2E.
- Ver cobertura obrigatória em [../docs/09-testing/testing-strategy.md](../docs/09-testing/testing-strategy.md): autenticação, RBAC, multi-tenancy (teste de vazamento cross-tenant é obrigatório em endpoint novo), e toda regra de negócio (BR-xx) tocada.

## Como executar localmente
Ver [../docs/08-devops/local-development.md](../docs/08-devops/local-development.md): `docker compose up -d` (Postgres/Redis) + `npm run dev`. `.env.example` tem as variáveis mínimas.

## O que nunca fazer
- Nunca escrever regra de negócio no Controller.
- Nunca desabilitar checagem de tenant/permissão, nem "temporariamente".
- Nunca fazer exclusão física de dado de negócio (soft delete apenas — BR-22).
- Nunca acoplar regra de negócio a um provedor externo específico (telefonia/WhatsApp) fora da camada `ChannelAdapter` ([../docs/03-architecture/integrations.md](../docs/03-architecture/integrations.md)).
- Nunca versionar segredo real (`.env` com valor real, chave de API).
- Nunca mudar contrato de API sem atualizar [../docs/05-api/openapi.yaml](../docs/05-api/openapi.yaml) no mesmo PR.

## Estrutura de pastas
Ver [../docs/07-backend/backend-architecture.md](../docs/07-backend/backend-architecture.md) seção 2.

## Padrões
Ver [../docs/07-backend/coding-standards.md](../docs/07-backend/coding-standards.md).

## Como consultar a documentação
Este repositório (`crm-spec`) é a fonte da verdade. Em caso de conflito entre o que o código faz e o que a documentação diz, a documentação vence — a menos que a tarefa seja justamente atualizar a documentação para refletir uma decisão nova (nesse caso, o PR deve atualizar ambos).

## Como criar uma funcionalidade nova
1. Confirmar que existe (ou criar) o requisito em [../docs/01-product/requirements.md](../docs/01-product/requirements.md).
2. Confirmar/criar a regra de negócio em [../docs/02-business/business-rules.md](../docs/02-business/business-rules.md).
3. Confirmar/criar a(s) entidade(s) em [../docs/04-database/entities.md](../docs/04-database/entities.md).
4. Definir o contrato em [../docs/05-api/openapi.yaml](../docs/05-api/openapi.yaml).
5. Implementar seguindo a estrutura de módulo padrão, com testes cobrindo a regra.

Pergunta a se fazer antes de qualquer PR: **"outro agente de IA conseguiria implementar isso corretamente apenas lendo a documentação deste repositório?"** Se não, atualize a documentação antes.
