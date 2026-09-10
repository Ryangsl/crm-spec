# Manual Acceptance Test (MAT)

## O que é isto

Uma camada de teste que **não existia** até o fechamento da Fase 2: testes automatizados
(unit/integration/e2e) provam que o código faz o que o código diz que faz; um MAT prova que
**o comportamento observável bate com a especificação de produto** — o mesmo roteiro que um
humano executaria para aceitar a fase, com resultado esperado e resultado proibido escritos
antes da execução, não depois.

**Testado automaticamente não é a mesma coisa que aceito manualmente.** Um teste e2e verde
prova que aquele código específico se comporta como o autor do teste esperava — não prova que
ninguém leu a spec errado, nem pega um caso que ninguém pensou em testar. O MAT é a checagem
independente disso, e desde 2026-09-10 cada MAT distingue explicitamente **quatro papéis**
diferentes (ver seção "As quatro camadas de um MAT" abaixo).

## Quem executa

- **A IA/agente**, durante a implementação ou o fechamento de uma fase — produz a seção
  "Resultado da IA" de cada MAT, com evidência real (resposta HTTP, consulta ao banco).
- **O responsável pelo projeto (humano)**, seguindo o "Tutorial de execução manual" de cada
  MAT — produz a seção "Validação Manual do Responsável". É esta validação, não a execução da
  IA, que fecha o aceite formal de um MAT.

## As quatro camadas de um MAT

Cada MAT-00X separa explicitamente:

1. **Tutorial de execução manual** — o roteiro reproduzível (comandos exatos, o que observar em
   cada passo), escrito para alguém que não participou da implementação nem precisa consultar o
   agente para executar.
2. **Resultado da IA (execução anterior)** — evidência histórica de quando a IA/agente já
   executou o roteiro contra um ambiente real, durante o fechamento da fase. **Isto não é
   validação manual do responsável.**
3. **Validação Manual do Responsável** — campo em branco, preenchido só quando uma pessoa de
   verdade executa o tutorial. Nunca é preenchido automaticamente pela IA.
4. **Critério de Aceite** — define objetivamente quando o MAT conta como `PASSOU` / `FALHOU` /
   `BLOQUEADO`, e deixa explícito que a execução da IA sozinha não fecha o aceite.

A distinção existe porque **"a IA já testou" e "o responsável validou" são registros
diferentes** — um MAT com a seção 2 preenchida e a seção 3 em branco está **executado, mas não
aceito**.

## Diferença entre teste automatizado, execução da IA, validação manual e aceite

| Camada | O que prova | Quem faz | Onde vive |
|---|---|---|---|
| Teste automatizado (unit/integration/e2e) | O código faz o que o autor do teste esperava | CI, a cada push/PR | `crm-backend`/`crm-frontend`, roda em segundos |
| Execução da IA (seção "Resultado da IA" de cada MAT) | O comportamento observável bateu com a spec, pelo menos uma vez, contra um ambiente real | IA/agente, no fechamento da fase | Este diretório, seção 8 de cada MAT |
| Validação manual (seção "Validação Manual do Responsável") | Uma pessoa confirmou o mesmo comportamento, de forma independente | Responsável pelo projeto | Este diretório, seção 9 de cada MAT — **em branco até ser preenchida** |
| Aceite | O critério de aceite (seção 10) foi satisfeito, com a validação manual preenchida | Responsável pelo projeto | `phase-acceptance/phase-XX.md` referencia o resultado consolidado |

## Como executar um MAT (para o responsável do projeto)

1. Abrir o arquivo `MAT-XXX-*.md`.
2. Seguir a seção "4. Pré-requisitos" para subir o ambiente.
3. Seguir cada passo da seção "6. Tutorial de execução manual" na ordem, comparando o resultado
   real com o "Resultado esperado" de cada passo.
4. Conferir a seção "7. Resultado que NÃO deve acontecer" — se qualquer item dela ocorrer, o
   MAT é `FALHOU`, independentemente do restante.
5. Preencher a seção "9. Validação Manual do Responsável" com o resultado real: executor, data,
   ambiente, resultado (`PASSOU`/`FALHOU`/`BLOQUEADO`), passos executados, observações e
   evidência (quando aplicável — ver "Regra de evidência" abaixo).
6. Marcar a linha correspondente na seção "11. Histórico".

## Como registrar resultado e evidência

- **Resultado**: sempre um de `PASSOU` / `FALHOU` / `BLOQUEADO` (ver seção "Critério de
  Aceite" de cada MAT para a definição exata de cada um).
- **Evidência**: proporcional ao risco — ver "Regra de evidência" abaixo. Nunca registrar um
  JWT, refresh token, secret ou senha real completos em texto — truncar/redigir (ex.:
  `eyJhbGci...redacted`). As credenciais de teste já documentadas nos MATs (ex.:
  `Admin123!`) são fixtures de seed, não secrets de produção, e podem continuar visíveis.

## Regra de não alterar evidência histórica

A seção "Resultado da IA" de cada MAT é um registro histórico — **nunca** é reescrita para
simular uma nova execução, nunca tem sua data alterada, e nunca é apagada para "resetar" o
MAT. Se um MAT precisar ser reexecutado pela IA no futuro (ex.: mudança de código que o
justifique), a execução nova é **adicionada**, não substitui a anterior — ver o padrão de
"Histórico" (seção 11) de cada MAT, que é uma tabela cumulativa, não um campo único.

## Quando um MAT é (re)executado

- No fechamento formal de cada fase do roadmap (pela IA, como primeira passada).
- Pelo responsável do projeto, no seu próprio ritmo, para fechar a "Validação Manual" antes do
  aceite formal — **não precisa acontecer na mesma sessão** em que a IA executou.
- Sempre que uma mudança tocar um fluxo coberto por um MAT existente (ex.: qualquer PR em
  `auth` deveria revalidar os MAT-001 a MAT-004, automatizado e manualmente, antes de mesclar).
- Sob demanda, quando há dúvida se o comportamento real bate com o documentado.

## Como este MAT foi executado no fechamento da Fase 2 (pela IA)

Como a Fase 2 não tem UI (ver [D-063](../../00-governance/decision-register.md#d-063--fase-2-não-exige-interface-mínima-opção-b)), todo MAT desta fase foi executado pela IA via API real —
backend rodando localmente contra Postgres/Redis reais (mesmo ambiente do
[`crm-workspace`](../../../../crm-workspace/README.md)), requisições HTTP de verdade
(`curl`), sem mock. A evidência na seção "Resultado da IA" de cada MAT é a resposta HTTP real
capturada nessa execução (2026-09-09), não um exemplo ilustrativo. Fases futuras com UI vão
precisar de screenshot/gravação para os passos que passam pela interface.

**Lacuna conhecida** (registrada em MAT-006, MAT-007 e MAT-008): os fixtures de um segundo
tenant ("MAT Tenant B", "MAT Tenant Suspenso") usados nessa execução não fazem parte do seed
padrão versionado (`crm-backend/prisma/seed.ts`) — foram provisionados manualmente durante a
execução de 2026-09-09, sem script commitado. Quem for reexecutar esses três MATs precisa
recriar esses fixtures primeiro (replicando a estrutura do tenant "Empresa Exemplo" do seed).

## Índice — Fase 2

| MAT | Nome | Prioridade | IA (seção 8) | Validação manual (seção 9) |
|---|---|---|---|---|
| [MAT-001](MAT-001-login.md) | Autenticação — Login | Crítica | PASSOU (2026-09-09) | PENDENTE |
| [MAT-002](MAT-002-refresh.md) | Autenticação — Refresh | Crítica | PASSOU (2026-09-09) | PENDENTE |
| [MAT-003](MAT-003-logout.md) | Autenticação — Logout individual | Alta | PASSOU (2026-09-09) | PENDENTE |
| [MAT-004](MAT-004-logout-global.md) | Autenticação — Logout global | Alta | PASSOU (2026-09-09) | PENDENTE |
| [MAT-005](MAT-005-users-crud.md) | Usuários — CRUD | Crítica | PASSOU (2026-09-09) | PENDENTE |
| [MAT-006](MAT-006-rbac.md) | RBAC — permissão concedida vs. negada | Crítica | PASSOU (2026-09-09) | PENDENTE |
| [MAT-007](MAT-007-tenant-isolation.md) | Isolamento entre tenants | Crítica (o mais crítico) | PASSOU (2026-09-09) | PENDENTE |
| [MAT-008](MAT-008-tenant-suspended.md) | Tenant suspenso | Alta | PASSOU (2026-09-09) | PENDENTE |
| [MAT-SEC-TENANT-001](MAT-SEC-TENANT-001-template.md) | **Padrão reutilizável** de isolamento para toda entidade tenant-scoped futura | — (template) | — | — |

Resultado consolidado de cada execução da IA: ver [phase-acceptance/phase-02.md](../phase-acceptance/phase-02.md) (não altera esta tabela — a tabela acima é o painel vivo de quais MATs ainda esperam validação manual).

## Padrão obrigatório de um MAT

Todo arquivo `MAT-XXX-*.md` segue esta estrutura, nesta ordem:

1. **Identificação** — ID, fase, prioridade, tipo, requisitos/ADRs/decisions relacionados.
2. **Objetivo** — o que está sendo validado, em uma frase.
3. **Escopo** — o que o MAT cobre e o que explicitamente não cobre (aponta para outros MATs quando aplicável).
4. **Pré-requisitos** — comandos explícitos para subir o ambiente; nunca presumir que quem executa já sabe.
5. **Dados de teste** — reproduzíveis; se dependem de um fixture fora do seed padrão, isso é sinalizado como lacuna.
6. **Tutorial de execução manual** — cada passo com Ação, Comando, Resultado esperado e O que observar. Sem instruções vagas ("testar login") — sempre reproduzível.
7. **Resultado que NÃO deve acontecer** — obrigatório, nunca omitido.
8. **Resultado da IA — Execução anterior** — evidência histórica, com data/executor/ambiente/método/resultado. Nunca reescrita retroativamente.
9. **Validação Manual do Responsável** — em branco até uma pessoa preencher; nunca gerada automaticamente.
10. **Critério de Aceite** — definição objetiva de `PASSOU`/`FALHOU`/`BLOQUEADO`, e a distinção explícita entre execução da IA e validação manual.
11. **Histórico** — tabela cumulativa (Data | Executor | Tipo | Resultado), nunca um campo único sobrescrito.

## Regra de evidência

Não exigir evidência para tudo. Regra prática:
- **Crítico** (isolamento entre tenants, autenticação, permissão): sempre capturar a resposta
  HTTP completa (status + corpo) e, quando aplicável, o registro correspondente no banco.
- **Alto/Médio**: status code + corpo da resposta bastam.
- Nunca exigir screenshot de uma chamada de API — não existe tela para fotografar. Quando a
  Fase com UI chegar, screenshot vira obrigatório só para os passos que passam pela interface.
- Nunca registrar JWT/refresh token/secret/senha real completos — truncar ou redigir.
