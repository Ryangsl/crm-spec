# Estratégia de Testes

## 1. Camadas de teste

| Tipo | Escopo | Ferramenta preferencial | Quando roda |
|---|---|---|---|
| Unit | Função/service isolado, dependências mockadas | Jest (backend), Vitest (frontend) | A cada commit (CI) |
| Integration | Módulo do backend + banco real (via container de teste) | Jest + Testcontainers/DB de teste | A cada PR |
| API/E2E backend | Requisição HTTP completa contra a API | Jest + Supertest | A cada PR |
| E2E frontend | Fluxo completo simulando usuário no navegador | Playwright (`[DECISÃO PENDENTE]`: confirmar vs. Cypress) | A cada PR (fluxos críticos) / nightly (suíte completa) |
| Frontend component | Componente isolado | Vitest + Testing Library | A cada commit (CI) |

## 2. Cobertura obrigatória (não negociável)

Toda mudança que toque as áreas abaixo exige teste automatizado cobrindo o caminho feliz **e** ao menos um caso de violação de regra:

- **Autenticação**: login válido/inválido, expiração e revogação de token.
- **Permissões (RBAC)**: usuário sem permissão não consegue executar a ação (nem ler o recurso, quando aplicável — 404 conforme BR-26).
- **Multi-tenancy**: usuário do tenant A nunca lê/escreve dado do tenant B — teste explícito de "vazamento entre tenants" é obrigatório para todo endpoint novo (ver [../03-architecture/security.md](../03-architecture/security.md) seção 1.3).
- **Regras de negócio de Leads/Pipeline**: conversão de lead (BR-04), transição de etapa e histórico (BR-09/BR-10), estado terminal de oportunidade (BR-11).
- **Call Center**: distribuição de atendimento por fila, obrigatoriedade de disposição ao encerrar (BR-15).
- **Integrações**: idempotência de webhook (BR-20), tratamento de falha de envio sem quebrar o restante do sistema.

## 3. O que não é obrigatório cobrir com o mesmo rigor

Telas puramente administrativas de configuração com baixo risco de regra de negócio (ex.: CRUD simples de tags) podem ter cobertura mais leve (unit/component), reservando integration/E2E para os fluxos críticos listados acima.

## 4. Dados de teste

- Nenhum teste roda contra dado real de tenant/cliente.
- Fixtures/factories representam os cenários de RBAC e multi-tenancy (ex.: sempre existir ao menos dois tenants e dois usuários com papéis diferentes na base de teste de integração), para que o teste de isolamento seja natural de escrever, não um esforço extra.

## 5. CI

- Testes unitários e de componente rodam em todo push.
- Testes de integração/API rodam em todo PR contra `main`.
- E2E de frontend: subconjunto de fluxos críticos (login, criar lead, converter em oportunidade, registrar atendimento) roda em todo PR; suíte completa roda em pipeline agendado (nightly) — `[DECISÃO PENDENTE]`: ferramenta de CI (GitHub Actions assumido como padrão, a confirmar).
- PR não é mesclado com suíte quebrada; falha de teste de tenant/permissão bloqueia merge sem exceção.

## 6. Testes de carga/performance

Fora do MVP como processo automatizado contínuo, mas RNF-01 (latência p95) deve ser validado manualmente antes de releases que alterem endpoints de alto volume (listagens, dashboard). `[DECISÃO PENDENTE]`: ferramenta (k6/Artillery) e cadência formal, a definir quando houver tráfego real para calibrar.
