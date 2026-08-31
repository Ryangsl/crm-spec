# Instruções — Codex no frontend (crm-frontend)

Este documento é a fonte para o `CLAUDE.md`/`AGENTS.md` que será criado em `crm-frontend` na Fase 1 do roadmap ([../docs/10-roadmap/roadmap.md](../docs/10-roadmap/roadmap.md)). Serve como guia para um agente (Codex ou equivalente) atuando em frontend.

## Onde este agente atua neste projeto (ver [divisão de agentes](reviewer.md))
- Frontend (`crm-frontend`): componentes, telas, integrações com a API.
- Testes de frontend (unit, component, E2E).
- Refatorações de UI.
- Code review de frontend.

Não decide arquitetura de produto/backend nem regra de negócio — isso vem definido em `crm-spec`.

## Antes de implementar qualquer coisa
1. Leia [../docs/06-frontend/frontend-architecture.md](../docs/06-frontend/frontend-architecture.md), [../docs/06-frontend/design-system.md](../docs/06-frontend/design-system.md) e [../docs/06-frontend/responsive.md](../docs/06-frontend/responsive.md).
2. Consulte o contrato real em [../docs/05-api/openapi.yaml](../docs/05-api/openapi.yaml) e [../docs/05-api/api-guidelines.md](../docs/05-api/api-guidelines.md) — nunca invente um endpoint ou formato de resposta.
3. Verifique se já existe um componente de design system equivalente antes de criar um novo estilo ad-hoc.

## Arquitetura (resumo)
- React + TypeScript + Vite + Tailwind + TanStack Query + React Hook Form + Zod, PWA.
- Um diretório `features/<nome>` por módulo de negócio, espelhando os módulos do backend.
- Estado de servidor: sempre TanStack Query. Nunca duplicar em estado global.
- Todo componente assíncrono trata loading, empty e error state — sem exceção (ver [../docs/06-frontend/frontend-architecture.md](../docs/06-frontend/frontend-architecture.md) seção 5).

## Como testar
- `npm run test` (Vitest, unit/component).
- `npm run test:e2e` (Playwright/E2E) para os fluxos críticos listados em [../docs/09-testing/testing-strategy.md](../docs/09-testing/testing-strategy.md).

## Como executar
`npm run dev` (Vite dev server) contra a API local (ver [../docs/08-devops/local-development.md](../docs/08-devops/local-development.md) para subir o backend).

## O que nunca fazer
- Nunca acessar banco de dados ou qualquer armazenamento além da API.
- Nunca implementar regra de negócio crítica no frontend (decidir se um lead pode ser convertido, se uma oportunidade pode mudar de etapa, etc.) — apenas enviar a intenção à API e tratar a resposta.
- Nunca estilizar um componente fora do design system sem antes verificar se falta um componente reutilizável.
- Nunca deixar uma tela sem tratamento explícito de loading/empty/error.
- Nunca assumir viewport desktop como padrão — todo componente novo é desenhado mobile-first (ver [../docs/06-frontend/responsive.md](../docs/06-frontend/responsive.md)).

## Estrutura de pastas
Ver [../docs/06-frontend/frontend-architecture.md](../docs/06-frontend/frontend-architecture.md) seção 2.

## Padrões
- Tipos derivados do contrato OpenAPI sempre que possível (evitar duplicar tipo manualmente quando já existe no contrato).
- Formulários sempre via React Hook Form + Zod, schema alinhado ao DTO do endpoint correspondente.

## Como consultar a documentação
`crm-spec` é a fonte da verdade do contrato e do design system. Dúvida sobre comportamento esperado de uma tela remete primeiro a [../docs/01-product/use-cases.md](../docs/01-product/use-cases.md) e [../docs/02-business/workflows.md](../docs/02-business/workflows.md).

## Como criar uma funcionalidade nova
1. Confirmar o contrato de API já existe (ou pedir/registrar a necessidade de um endpoint novo — não inventar um endpoint que o backend não expõe).
2. Montar a tela com componentes do design system existentes.
3. Cobrir loading/empty/error e os breakpoints `xs` a `xl`.
4. Escrever teste do fluxo (component e, se crítico, E2E).
