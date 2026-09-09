# Manual Acceptance Test (MAT)

## O que é isto

Uma camada de teste que **não existia** até o fechamento da Fase 2: testes automatizados
(unit/integration/e2e) provam que o código faz o que o código diz que faz; um MAT prova que
**o comportamento observável bate com a especificação de produto** — o mesmo roteiro que um
humano (ou um agente revisor) executaria para aceitar a fase, com resultado esperado e
resultado proibido escritos antes da execução, não depois.

**Testado automaticamente não é a mesma coisa que aceito manualmente.** Um teste e2e verde
prova que aquele código específico se comporta como o autor do teste esperava — não prova que
ninguém leu a spec errado, nem pega um caso que ninguém pensou em testar. O MAT é a checagem
independente disso.

## Quando um MAT é executado

- No fechamento formal de cada fase do roadmap (obrigatório).
- Sempre que uma mudança tocar um fluxo coberto por um MAT existente (ex.: qualquer PR em
  `auth` deveria rodar os MAT-001 a MAT-004 antes de mesclar, não só os testes automatizados).
- Sob demanda, quando há dúvida se o comportamento real bate com o documentado.

## Como este MAT foi executado no fechamento da Fase 2

Como a Fase 2 não tem UI (ver [D-063](../../00-governance/decision-register.md#d-063--fase-2-não-exige-interface-mínima-opção-b)), todo MAT desta fase foi executado via API real —
backend rodando localmente contra Postgres/Redis reais (mesmo ambiente do
[`crm-workspace`](../../../../crm-workspace/README.md)), requisições HTTP de verdade
(`curl`), sem mock. A evidência embutida em cada MAT-00X é a resposta HTTP real capturada
nessa execução, não um exemplo ilustrativo. Fases futuras com UI vão precisar de
screenshot/gravação para os passos que passam pela interface — a seção "Evidências" de cada
MAT já indica quando isso será necessário.

## Índice — Fase 2

| MAT | Nome | Prioridade |
|---|---|---|
| [MAT-001](MAT-001-login.md) | Autenticação — Login | Crítica |
| [MAT-002](MAT-002-refresh.md) | Autenticação — Refresh | Crítica |
| [MAT-003](MAT-003-logout.md) | Autenticação — Logout individual | Alta |
| [MAT-004](MAT-004-logout-global.md) | Autenticação — Logout global | Alta |
| [MAT-005](MAT-005-users-crud.md) | Usuários — CRUD | Crítica |
| [MAT-006](MAT-006-rbac.md) | RBAC — permissão concedida vs. negada | Crítica |
| [MAT-007](MAT-007-tenant-isolation.md) | Isolamento entre tenants | Crítica |
| [MAT-008](MAT-008-tenant-suspended.md) | Tenant suspenso | Alta |
| [MAT-SEC-TENANT-001](MAT-SEC-TENANT-001-template.md) | **Padrão reutilizável** de isolamento para toda entidade tenant-scoped futura | — (template) |

Resultado consolidado de cada execução: ver [phase-acceptance/phase-02.md](../phase-acceptance/phase-02.md).

## Padrão obrigatório de um MAT

Todo arquivo `MAT-XXX-*.md` segue esta estrutura, nesta ordem:

1. **Identificação** — código, nome, fase, prioridade.
2. **Objetivo** — o que está sendo validado, em uma frase.
3. **Pré-requisitos** — o que precisa estar de pé antes de começar (infra, dados).
4. **Dados de teste** — reproduzíveis; se dependem de um script de setup, o script é referenciado.
5. **Passos detalhados** — cada passo diz exatamente o que fazer, sem ambiguidade.
6. **Resultado esperado** — lista de afirmações verificáveis (✓).
7. **Resultado que NÃO deve acontecer** — obrigatório, nunca omitido (✗).
8. **Evidências** — o que foi de fato capturado (resposta HTTP, log, registro de banco).
   Proporcional ao risco: um 403 não precisa de screenshot, um vazamento cross-tenant merece
   registro completo.
9. **Resultado** — `PASSOU` / `FALHOU` / `BLOQUEADO`, com data e quem executou.
10. **Observações** — campo livre.

## Regra de evidência

Não exigir evidência para tudo. Regra prática:
- **Crítico** (isolamento entre tenants, autenticação, permissão): sempre capturar a resposta
  HTTP completa (status + corpo) e, quando aplicável, o registro correspondente no banco.
- **Alto/Médio**: status code + corpo da resposta bastam.
- Nunca exigir screenshot de uma chamada de API — não existe tela para fotografar. Quando a
  Fase com UI chegar, screenshot vira obrigatório só para os passos que passam pela interface.
