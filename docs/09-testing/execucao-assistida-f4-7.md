# F4.7 — Execução técnica assistida dos MATs 009 a 016

> **O que é este documento**: registro consolidado da **execução técnica assistida por IA** dos MATs do F4.7 (restrição de acesso por horário comercial e liberação excepcional — [D-082](../00-governance/decision-register.md#d-082--restrição-por-horário-comercial-e-liberação-excepcional-vn-07-vn-08)/[D-083](../00-governance/decision-register.md#d-083--exceções-de-acesso-modelo-técnico-e-critério-de-identificação-td-05-td-14)).
> **O que ele NÃO é**: validação manual do responsável nem aceite formal. A seção 9 ("Validação Manual do Responsável") de cada MAT permanece **em branco** e o aceite humano está **PENDENTE nos oito MATs**. Nenhum MAT está formalmente aceito.

Executor: Claude (Sonnet 5.5), a pedido do responsável pelo projeto. Datas: 2026-10-19 (execuções) e 2026-11-03 (verificação do defeito D1). Os resultados abaixo foram retirados das seções 9 dos MATs, onde tinham sido registrados em desacordo com o padrão (a seção 9 é reservada ao aceite oficial — ver o [README dos MATs](manual-acceptance/README.md)); nada foi perdido, só movido para cá.

## 1. Resultado consolidado

| MAT | Tema | Execução assistida (IA) | Verificações | Aceite humano (seção 9) |
|---|---|---|---|---|
| [MAT-009](manual-acceptance/MAT-009-restricao-toggle-global.md) | Toggle global (somente Admin) | PASSOU | 23/23 | PENDENTE |
| [MAT-010](manual-acceptance/MAT-010-restricao-acesso-dentro-fora-horario.md) | Acesso dentro e fora do horário | PASSOU | 24/24 | PENDENTE |
| [MAT-011](manual-acceptance/MAT-011-restricao-isencoes-multiplos-papeis.md) | Isenções e múltiplos papéis | PASSOU | 20/20 | PENDENTE |
| [MAT-012](manual-acceptance/MAT-012-restricao-liberacao-excepcional.md) | Liberação excepcional | PASSOU | 41/41 | PENDENTE |
| [MAT-013](manual-acceptance/MAT-013-restricao-isolamento-tenant.md) | Isolamento entre tenants | PASSOU | 16/16 | PENDENTE |
| [MAT-014](manual-acceptance/MAT-014-restricao-interface.md) | Interface (toggle, banner, 403, tela de liberações) | PASSOU | 39/39 | PENDENTE |
| [MAT-015](manual-acceptance/MAT-015-restricao-rotas-excluidas.md) | Rotas excluídas (D-082) | PASSOU | 14/14 | PENDENTE |
| [MAT-016](manual-acceptance/MAT-016-restricao-disponibilidade-distribuicao.md) | Disponibilidade e distribuição inalteradas | PASSOU | 9/9 | PENDENTE |

Observações sobre o resultado: (a) **PASSOU** vale para a execução técnica assistida, não para o aceite; (b) houve **um defeito menor de layout (D1)**, na seção 4; (c) houve **uma correção do roteiro** do MAT-014 (passo 7.2), na seção 5.

## 2. Ambiente e método

**Execução de 2026-10-19 (MATs de API: 009, 010, 011, 012, 013, 015 e 016)** — backend do `main` pós-merge (crm-backend `20ec912`, `nest build` local) em `http://localhost:3101`; banco **descartável** `crm_mat_f47`, criado na própria rodada (`prisma migrate deploy` + `npm run db:seed`); Postgres 16 e Redis locais; relógio real; requisições HTTP reais por script (Python) e consultas SQL. Tenants de teste: A (seed), B (criado por SQL, ver [F4-7-preparacao-do-ambiente.md](manual-acceptance/F4-7-preparacao-do-ambiente.md)) e, no MAT-014, C (sem horário). A execução foi feita duas vezes no mesmo dia: a primeira, mais cedo (≈ 15:50 UTC, registrada na seção 8 de cada MAT), e a reexecução com banco novo e mais verificações (≈ 16:20 UTC), descrita aqui.

**MAT-014 (interface)** — frontend do `main` (crm-frontend `289373e`, Vite dev com `VITE_API_URL=http://localhost:3101`) e o backend acima; **Google Chrome real** automatizado com `playwright-core` (headless, 1280×900); 35 screenshots.

**Verificação do D1 (2026-11-03)** — backend do `main` (`20ec912`), frontend na branch `fix/f4-7-access-exceptions-long-reason`, banco descartável `crm_d1_check` (criado e removido; `prisma migrate deploy` aplicou as migrations até a do F4.7), Chrome real.

Nada foi executado em ambiente real; nenhum dado de cliente real; o runbook dos tenants existentes e a ativação do toggle global **não** foram executados.

## 3. Detalhes por MAT

### MAT-009 — Toggle global (somente Admin)

- **Resultado (execução assistida)**: PASSOU, 23/23 verificações conforme o esperado.
- **Ambiente**: backend do `main` pós-merge (crm-backend `20ec912`, `nest build` local) em `http://localhost:3101`; banco descartável `crm_mat_f47` criado nesta rodada (`prisma migrate deploy` + `npm run db:seed`, 2026-10-19); Postgres 16 e Redis locais; relógio real; execução por script HTTP (Python) + consultas SQL, 16:20–16:21 UTC
- **Passos do roteiro cobertos**: ✔ 1 Estado inicial · ✔ 2 Ativar sem horário · ✔ 3 Desligar sem horário · ✔ 4 Horário inválido · ✔ 5 Ativar com horário · ✔ 6 Idempotência/formato · ✔ 7 Auditoria · ✔ 8 Perfis sem permissão · ✔ 9 Toggle intacto · ✔ 10 Desligar

**Observações**

23 de 23 verificações conforme o esperado. Auditoria: `2` registros (um por mudança de valor; o `PUT true` repetido não audita). Gerente, Vendedor, Supervisor, Operador e `multi` receberam `403 FORBIDDEN` em leitura e escrita; sem token, `401`. A interface do toggle foi validada no [MAT-014](manual-acceptance/MAT-014-restricao-interface.md).

**Evidências**

Seção "MAT-009" de [`evidence/F4-7/2026-10-19-execucao-api-mat009-016.log`](evidence/F4-7/2026-10-19-execucao-api-mat009-016.log) (status HTTP e corpo de cada passo; consulta SQL da auditoria).

### MAT-010 — Acesso dentro e fora do horário

- **Resultado (execução assistida)**: PASSOU, 24/24 verificações conforme o esperado.
- **Ambiente**: backend do `main` pós-merge (crm-backend `20ec912`, `nest build` local) em `http://localhost:3101`; banco descartável `crm_mat_f47` criado nesta rodada (`prisma migrate deploy` + `npm run db:seed`, 2026-10-19); Postgres 16 e Redis locais; relógio real; execução por script HTTP (Python) + consultas SQL, 16:20–16:21 UTC
- **Passos do roteiro cobertos**: ✔ 1 Dentro do horário · ✔ 2 Vendedor acessa · ✔ 3 Fora do horário · ✔ 4 Status fora · ✔ 5 Rotas bloqueadas (10 chamadas) · ✔ 6 Sem efeito colateral · ✔ 7 Não sujeito / permissão antes · ✔ 8 Desligar e religar

**Observações**

24 de 24 verificações conforme o esperado. As 10 chamadas do Passo 5 devolveram `403 OUTSIDE_BUSINESS_HOURS`; SQL: leads antes/depois `1|1`, nome do lead intacto (`MAT Lead A1`), `0` mensagens gravadas. Operador (sem marcador) `200`; Operador em `assign` recebeu `403 FORBIDDEN` (permissão antes do horário). Não foram chamadas manualmente as rotas `DELETE /leads/{id}`, `disqualify`, `reopen` de Leads e `assign`/`reopen` de Conversas pelo Vendedor (cobertas só pelos testes e2e).

**Evidências**

Seção "MAT-010" de [`evidence/F4-7/2026-10-19-execucao-api-mat009-016.log`](evidence/F4-7/2026-10-19-execucao-api-mat009-016.log).

### MAT-011 — Isenções e múltiplos papéis

- **Resultado (execução assistida)**: PASSOU, 20/20 verificações conforme o esperado.
- **Ambiente**: backend do `main` pós-merge (crm-backend `20ec912`, `nest build` local) em `http://localhost:3101`; banco descartável `crm_mat_f47` criado nesta rodada (`prisma migrate deploy` + `npm run db:seed`, 2026-10-19); Postgres 16 e Redis locais; relógio real; execução por script HTTP (Python) + consultas SQL, 16:20–16:21 UTC
- **Passos do roteiro cobertos**: ✔ 1 Papéis/marcadores do `multi` · ✔ 2 Isentos acessam · ✔ 3 Papel sem marcador · ✔ 4 Vendedor puro · ✔ 5 Concessão a não sujeito · ✔ 6 Troca de papéis

**Observações**

20 de 20 verificações conforme o esperado. `multi` com papéis `gerente` e `vendedor` e os três marcadores; Admin, Gerente, Supervisor e `multi` `200` fora do horário (`applies_to_me = false`); Vendedor puro `403`; `multi` só com `vendedor` `403` e `applies_to_me = true`, restaurado `200`. Passo 5 exercitado só com o alvo `multi` (`422 ACCESS_EXCEPTION_TARGET_NOT_RESTRICTED`); os alvos Operador/Gerente/Admin foram exercitados no [MAT-012](manual-acceptance/MAT-012-restricao-liberacao-excepcional.md) (passo 23). Diretor sem usuário no fixture.

**Evidências**

Seção "MAT-011" de [`evidence/F4-7/2026-10-19-execucao-api-mat009-016.log`](evidence/F4-7/2026-10-19-execucao-api-mat009-016.log).

### MAT-012 — Liberação excepcional

- **Resultado (execução assistida)**: PASSOU, 41/41 verificações conforme o esperado.
- **Ambiente**: backend do `main` pós-merge (crm-backend `20ec912`, `nest build` local) em `http://localhost:3101`; banco descartável `crm_mat_f47` criado nesta rodada (`prisma migrate deploy` + `npm run db:seed`, 2026-10-19); Postgres 16 e Redis locais; relógio real; execução por script HTTP (Python) + consultas SQL, 16:20–16:21 UTC
- **Passos do roteiro cobertos**: ✔ 1 Bloqueado antes · ✔ 2 Concede `leads` · ✔ 3 Concede `conversations` · ✔ 4 Concede `all` · ✔ 5 Listagem/filtros · ✔ 6 Revogar uma · ✔ 7 Revogar todas · ✔ 8 Validações do corpo · ✔ 9 Quem pode gerir · ✔ 10 Expiração (30 s) · ✔ 11 Auditoria

**Observações**

41 de 41 verificações conforme o esperado. Listagem com `total = 3` (ordem `all`, `conversations`, `leads`); revogação repetida preservou `revoked_at` (`2026-10-19T16:20:47.254Z`); motivo de exatamente 1.000 caracteres aceito (`201`) e de 1.001 recusado (`400`); expiração em 30 s: dentro da validade `200`, após `2026-10-19T16:21:17Z` `403 OUTSIDE_BUSINESS_HOURS`; auditoria `access_exception.granted` = 5 (inclui a de 1.000 caracteres); nenhuma liberação vigente ao final. **Não exercitados nesta rodada**: `expires_at` ausente, campo não previsto `granted_by` e chamada sem token em `/access-exceptions` (cobertos pelos testes e2e). **Defeito de interface relacionado** (menor): ver o MAT-014 (motivo de 1.000 caracteres sem espaços estoura a largura da tela de liberações).

**Evidências**

Seção "MAT-012" de [`evidence/F4-7/2026-10-19-execucao-api-mat009-016.log`](evidence/F4-7/2026-10-19-execucao-api-mat009-016.log).

### MAT-013 — Isolamento entre tenants

- **Resultado (execução assistida)**: PASSOU, 16/16 verificações conforme o esperado.
- **Ambiente**: backend do `main` pós-merge (crm-backend `20ec912`, `nest build` local) em `http://localhost:3101`; banco descartável `crm_mat_f47` criado nesta rodada (`prisma migrate deploy` + `npm run db:seed`, 2026-10-19); Postgres 16 e Redis locais; relógio real; execução por script HTTP (Python) + consultas SQL, 16:20–16:21 UTC; tenant B criado pelo SQL de `F4-7-preparacao-do-ambiente.md` (validado nesta rodada)
- **Passos do roteiro cobertos**: ✔ 1 Criar em A · ✔ 2 B não lista · ✔ 3 B não revoga · ✔ 4 B não concede a A · ✔ 5 Lead/Conversa de A · ✔ 6 A intacta · ✔ 7 Toggle/horário por tenant · ✔ 8 Sem vazamento · ✔ 9 Liberação de B · ✔ 10 Limpeza

**Observações**

16 de 16 verificações conforme o esperado. Tenant B: listagem vazia (`total: 0`); `DELETE` da liberação de A e `POST` para usuário de A: `404 NOT_FOUND` (nunca `403`); leitura do Lead e da Conversa de A: `404`; a liberação de A seguiu com `revoked_at` nulo; o horário/toggle ligados em A não afetaram B; a liberação `all` de A não liberou o Vendedor de B (`403 OUTSIDE_BUSINESS_HOURS`); contagem por tenant: A `6`, B `1`.

**Evidências**

Seção "MAT-013" de [`evidence/F4-7/2026-10-19-execucao-api-mat009-016.log`](evidence/F4-7/2026-10-19-execucao-api-mat009-016.log) (respostas HTTP e consultas SQL).

### MAT-014 — Interface (toggle, banner, 403, tela de liberações)

- **Resultado (execução assistida)**: PASSOU, 39/39 verificações conforme o esperado.
- **Ambiente**: backend do `main` pós-merge (crm-backend `20ec912`) em `http://localhost:3101` e frontend do `main` (crm-frontend `289373e`) em `http://localhost:5173` (Vite dev, `VITE_API_URL=http://localhost:3101`); banco descartável `crm_mat_f47`; navegador **Google Chrome real** (automatizado por `playwright-core`, janela 1280×900, headless); usuários e tenants do arquivo de preparação (mais um tenant C sem horário para o Passo 2); relógio real
- **Passos do roteiro cobertos**: ✔ 1 Toggle só Admin · ✔ 2 Ligar/desligar e recusa · ✔ 3 Banner do Vendedor · ✔ 4 Banner parcial · ✔ 5 `403` nas telas · ✔ 6 Volta ao normal com liberação · ✔ 7 Tela de liberações · ✔ 8 Visibilidade por permissão

**Observações**

39 de 39 verificações conforme o esperado na execução final (35 screenshots). Toggle: o Admin liga/desliga (a API confirma o valor); o Gerente vê "Acesso restrito"; um perfil só com `tenant_settings:read` vê o estado e "Somente o Admin pode ligar ou desligar a restricao." sem botão; no tenant sem horário o botão "Ligar restricao" fica desabilitado com o aviso. Banner: aparece para o Vendedor (Leads e Conversas), cita só "Conversas" com liberação `leads` e some com `all`; não aparece para Gerente, Supervisor e Operador, com a restrição desligada nem dentro do horário. `403`: `/leads`, `/leads/:id`, `/conversations`, `/conversations/:id` e a seção "Conversas" do detalhe do Cliente mostram o aviso "Fora do horario de funcionamento" sem erro genérico. Tela de liberações: conceder (leads e conversations), recusas, filtros e revogação funcionam; Supervisor, Vendedor e Operador não veem o item de menu e recebem "Acesso restrito".

**Correção do roteiro (erro da minha especificação, achado na execução)**: o roteiro afirmava que motivo vazio e "Vale até" vazio mostram as mensagens "Informe o motivo da liberacao." e "Informe ate quando a liberacao vale.". Na interface real os dois campos são `required`: o **navegador bloqueia o envio** (validação nativa) e nada é criado; a mensagem "Informe o motivo da liberacao." aparece com motivo só de espaços e "A expiracao deve estar no futuro." com data passada. O Passo 7.2 e os esperados foram corrigidos de acordo; o comportamento da tela satisfaz o objetivo (recusar sem motivo/expiração). A primeira execução (4 divergências: esses dois pontos e dois de contagem de itens na lista, que assumiam uma lista vazia) está preservada em `2026-10-19-1a-execucao-descartada.log`.

**Defeito encontrado (menor, de layout) — D1**: na tela `/settings/access-exceptions`, um motivo longo **sem espaços** (o de 1.000 caracteres criado no MAT-012, passo 16b) faz o documento ficar com **7.461 px de largura** (viewport 1.280 px): o texto não quebra e a página rola na horizontal; por isso as capturas do Passo 7 aparecem deslocadas à esquerda. Reprodução: conceder (ou criar pela API) uma liberação com motivo de 1.000 caracteres sem espaços e abrir a tela; evidência `2026-10-19-passo7-defeito-motivo-longo-sem-espacos-estoura-largura.png`. Causa provável: o parágrafo do motivo na lista não tem quebra de palavra (`overflow-wrap`/`break-words`). Não corrigido nesta etapa (decisão pendente). **Não é a lacuna conhecida** de `/leads/new`.

**Não exercitado**: a seção "Conversas" no detalhe de Oportunidade (não há oportunidade nos dados de teste); o envio do formulário de `/leads/new` e da edição de Lead (o Vendedor de fábrica não tem `lead_sources:read`; só a abertura da tela foi capturada — lacuna conhecida do tratamento do `403`); isolamento entre tenants na interface (validado só por API no MAT-013). Observação fora do escopo do F4.7: o menu lateral exibe a marca "CRM + Call Center" (terminologia que a D-070 manda evitar; texto preexistente).

**Evidências**

[`evidence/MAT-014/`](evidence/MAT-014/) — 35 screenshots (`2026-10-19-passoN-*.png`), log [`2026-10-19-execucao-ui.log`](evidence/MAT-014/2026-10-19-execucao-ui.log) e o script usado.

### MAT-015 — Rotas excluídas (D-082)

- **Resultado (execução assistida)**: PASSOU, 14/14 verificações conforme o esperado.
- **Ambiente**: backend do `main` pós-merge (crm-backend `20ec912`, `nest build` local) em `http://localhost:3101`; banco descartável `crm_mat_f47` criado nesta rodada (`prisma migrate deploy` + `npm run db:seed`, 2026-10-19); Postgres 16 e Redis locais; relógio real; execução por script HTTP (Python) + consultas SQL, 16:20–16:21 UTC
- **Passos do roteiro cobertos**: ✔ 1 Importação · ✔ 2 Conversão · ✔ 3 `lead-sources` (com papel personalizado) · ✔ 4 Perfil/status/disponibilidade/notificações · ✔ 5 Lacunas PN-3 · ✔ 6 Contraste

**Observações**

14 de 14 verificações conforme o esperado. Importação `201` e conversão `201` fora do horário; `lead-sources` `200` para o papel personalizado sujeito (e `403 FORBIDDEN` por permissão para o Vendedor de fábrica); `users/me`, `access-status`, `availability/me` e `notifications/unread-count` `200`. **Lacuna PN-3 observada**: `GET /customers`, `/opportunities` e `/tasks` devolveram `200` ao Vendedor fora do horário (não protegidos pela restrição, como aprovado em D-082). Não foram exercitados notas, compromissos, interações e timeline.

**Evidências**

Seção "MAT-015" de [`evidence/F4-7/2026-10-19-execucao-api-mat009-016.log`](evidence/F4-7/2026-10-19-execucao-api-mat009-016.log).

### MAT-016 — Disponibilidade e distribuição inalteradas

- **Resultado (execução assistida)**: PASSOU, 9/9 verificações conforme o esperado.
- **Ambiente**: backend do `main` pós-merge (crm-backend `20ec912`, `nest build` local) em `http://localhost:3101`; banco descartável `crm_mat_f47` criado nesta rodada (`prisma migrate deploy` + `npm run db:seed`, 2026-10-19); Postgres 16 e Redis locais; relógio real; execução por script HTTP (Python) + consultas SQL, 16:20–16:21 UTC
- **Passos do roteiro cobertos**: ✔ 1 Disponibilidade e estado inicial · ✔ 2 Distribuição fora do horário · ✔ 3 Notificação · ✔ 4 Consequência conhecida · ✔ 5 Disponibilidade intacta · ✔ 6 Toggle não mexe na disponibilidade

**Observações**

9 de 9 verificações conforme o esperado. Lead criado sem `owner_id` fora do horário e com a restrição ligada foi atribuído ao Vendedor `Disponível` (`owner_id` = id do Vendedor); `unread-count` `200` (`count: 2`, incluindo o lead da fixture); o Vendedor não abre o lead atribuído (`403 OUTSIDE_BUSINESS_HOURS` — consequência conhecida, não é falha); estado e histórico de disponibilidade idênticos antes, depois e após desligar/religar a restrição (`available|1`).

**Evidências**

Seção "MAT-016" de [`evidence/F4-7/2026-10-19-execucao-api-mat009-016.log`](evidence/F4-7/2026-10-19-execucao-api-mat009-016.log).

## 4. Defeito D1 — motivo longo sem espaços estoura a largura da tela de liberações

- **Sintoma**: em `/settings/access-exceptions`, um motivo de 1.000 caracteres consecutivos sem espaços (criado no MAT-012, passo 16b) deixa o documento com **7.461 px de largura** (viewport 1.280 px): o texto não quebra e a página rola na horizontal. Gravidade baixa (layout; não afeta dados nem permissões).
- **Reprodução**: criar uma liberação com `reason` de 1.000 caracteres sem espaços e abrir a tela. Evidência original (2026-10-19): `evidence/MAT-014/2026-10-19-passo7-defeito-motivo-longo-sem-espacos-estoura-largura.png`.
- **Causa**: o parágrafo do motivo não tinha quebra de palavra e o item flex que o contém não tinha `min-w-0`.
- **Correção** (somente frontend; branch `fix/f4-7-access-exceptions-long-reason` do `crm-frontend`; commit `c463c69`, publicada em `origin` (**não integrada ao `main`**)): em `AccessExceptionsPage.tsx`, `wrap-anywhere` (`overflow-wrap: anywhere`) no parágrafo do motivo e `min-w-0` no contêiner. Limite de 1.000 caracteres, contrato da API e regras de negócio **inalterados**. Teste novo em `AccessExceptionsPage.test.tsx` (motivo de 1.000 caracteres; confere as classes; verificado por mutação: falha sem a classe).
- **Verificação no navegador** (Chrome real, controle antes/depois, mesmos dados: motivo de 1.000 `a`, motivo normal e uma URL longa de 328 caracteres):

| Situação | Viewport | `scrollWidth` | Rolagem horizontal |
|---|---|---|---|
| Antes (código do `main`) | 1280×900 | **7.461 px** | sim (`scrollX` = 5000 após rolar) |
| Depois (com a correção) | 1280×900 | 1.280 px | não (`scrollX` = 0) |
| Depois (com a correção) | 390×844 (móvel) | 390 px | não |

  Evidências: `evidence/MAT-014/2026-11-03-d1-antes-sem-correcao-1280x900.png`, `2026-11-03-d1-corrigido-1280x900.png`, `2026-11-03-d1-corrigido-390x844.png`, `2026-11-03-d1-verificacao-layout.log` e `2026-11-03-d1-script-verificacao-layout.mjs`.
- **Testes do frontend com a correção**: `tsc` OK; lint OK; **276/276** testes (44 arquivos; 275 anteriores + 1 novo); build OK.
- **Pendente**: revisão e integração da branch (decisão do responsável).

## 5. Correção do roteiro do MAT-014 (passo 7.2) e primeira execução descartada

O roteiro previa que motivo vazio e "Vale até" vazio exibissem mensagens da própria tela. Na interface real os dois campos são `required`: o **navegador bloqueia o envio** (validação nativa) e **nenhum registro é criado**. As mensagens da tela aparecem com **motivo só de espaços** ("Informe o motivo da liberacao.") e com **data passada** ("A expiracao deve estar no futuro."). O texto do passo 7.2 foi corrigido no MAT-014 (com a anotação da correção) e o comportamento atende ao objetivo do MAT. **Não** é defeito de implementação: foi erro da especificação do roteiro, achado na execução.

A **primeira execução** do MAT-014 teve 4 divergências — esses dois pontos mais duas verificações de contagem de itens que assumiam uma lista vazia (problema de preparação do ambiente). Ela está **preservada**, junto com a segunda execução, em `evidence/MAT-014/2026-10-19-1a-execucao-descartada.log` e `2026-10-19-2a-execucao-sem-defeito-de-layout-registrado.log`; o log final é `2026-10-19-execucao-ui.log`.

## 6. Limitações

- **O executor é a IA**, por delegação: a execução técnica assistida não substitui o aceite do responsável, que deve rodar os roteiros por conta própria.
- Banco descartável e dados sintéticos; relógio real (rodar longe da meia-noite UTC).
- **Não exercitados**: a seção "Conversas" no detalhe de Oportunidade (não há oportunidade nos dados de teste); o envio do formulário de `/leads/new` e da edição de Lead (o Vendedor de fábrica não tem `lead_sources:read`; lacuna conhecida do tratamento do `403`); `expires_at` ausente, o campo `granted_by` e a chamada sem token em `/access-exceptions` (cobertos pelos testes e2e); o isolamento entre tenants na interface (só por API, MAT-013); notas, compromissos, interações e timeline (lacuna PN-3, sem evidência própria).
- As rotas `DELETE /leads/{id}`, `disqualify`, `reopen` de Leads e `assign`/`reopen` de Conversas pelo Vendedor não foram chamadas manualmente no MAT-010 (cobertas só pelos testes e2e).
- Observação fora do escopo do F4.7: o menu lateral exibe a marca "CRM + Call Center" (terminologia que a D-070 manda evitar; texto preexistente).
- **CI**: o CI do **frontend** foi confirmado com ressalva — a execução do push no `main` (`289373e`) foi **cancelada** pela regra de concorrência do workflow e a execução do evento de PR rodou sobre o `main` em `289373e` e passou (lint, 275 testes e build); a run cancelada não pôde ser reexecutada (token sem permissão de Actions). O **CI do backend** (`20ec912`) **continua pendente de verificação por alguém com acesso autorizado** ao repositório privado: não foi consultado nem contornado. O `crm-spec` não tem CI.

## 7. Pendências

1. **Aceite humano** dos MATs 009 a 016 (seção 9 de cada um): **PENDENTE nos oito**.
2. Revisão e decisão de integração da branch `fix/f4-7-access-exceptions-long-reason` (D1).
3. Verificação do CI do backend por quem tem acesso; reexecução do CI do `main` do frontend, se desejado.
4. Etapas operacionais separadas e **não executadas**: `migrate deploy` real, [runbook dos tenants existentes](../08-devops/runbook-f4-7-tenant-roles.md) e ativação do toggle global.
5. Fora deste escopo: o bug `ListConversationsQueryDto.unassigned` (F4.6), o F4.8 e a Fase 5.

## 8. Índice de evidências

- `evidence/F4-7/2026-10-19-execucao-api-mat009-016.log` e `2026-10-19-script-execucao-api.py` — execução por API.
- `evidence/MAT-014/` — 35 screenshots `2026-10-19-passoN-*.png`; logs `2026-10-19-execucao-ui.log`, `2026-10-19-1a-execucao-descartada.log`, `2026-10-19-2a-execucao-sem-defeito-de-layout-registrado.log`; script `2026-10-19-script-execucao-ui.mjs`.
- `evidence/MAT-014/2026-11-03-d1-*` — verificação antes/depois do D1 (3 screenshots, log e script).
- Os logs nunca imprimem tokens; as senhas de teste são fixtures.
- Os dois scripts `.mjs` de interface tiveram o prefixo local do caminho (`OUT`/`FE`) trocado por `<RAIZ>` antes de versionar, para não expor o diretório da máquina; o restante do código não foi alterado.
