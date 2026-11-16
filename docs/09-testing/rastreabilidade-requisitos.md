# Rastreabilidade de requisitos e maturidade funcional

> Documento vivo. Cruza [requirements.md](../01-product/requirements.md), [use-cases.md](../01-product/use-cases.md), o [roadmap](../10-roadmap/roadmap.md), o [MVP](../10-roadmap/mvp.md) e o [Decision Register](../00-governance/decision-register.md) com o código. Ao fechar uma entrega, atualize o status do requisito e a seção 8. Em conflito, valem os documentos oficiais e o comportamento verificável do sistema, nesta ordem: código e testes, decisões, roadmap, anotações históricas.

## 1. Escopo e método (auditoria de 10/11/2026)

- **Código auditado:** `crm-backend` `ccfee7a` (+ `906e13d`, só `CLAUDE.md`), `crm-frontend` `3d40079`, `crm-spec` `7165f00`. Árvores limpas.
- **Fontes:** este repositório inteiro, a auditoria anterior (`universal-crm/AUDITORIA-TECNICA.md`, 03/11/2026, cujos achados de segurança foram tratados nas D-084 e D-090 a D-093) e as notas do Obsidian (`02 - Produtos Proprios/CRM Universal`).
- **Testes executados de verdade** (cópia isolada dos repositórios, PostgreSQL 16 e Redis 7 descartáveis):

| Momento | Backend | Frontend |
|---|---|---|
| Linha de base (`main`) | `tsc` e lint OK; unitários 429/429; integração 2/2; **e2e 501/502** | lint e build OK; **413/413** |
| Depois da E1 | `tsc`, lint e build OK; unitários 433/433; integração 2/2; **e2e 503/504** | lint e build OK; **440/440** |

  A única falha de e2e (`integrity-conflicts` › documento de cliente já usado → 409) é do **ambiente da auditoria**, não do código: o host de binários do Prisma estava bloqueado e os testes rodaram com o adaptador `@prisma/adapter-pg`, que entrega o erro P2002 com outro formato de `meta` (sem `target`). O CI do GitHub, com o motor nativo, passou nesse teste em 07/11/2026. **Atenção para o Prisma 7**, que torna o adaptador obrigatório: `common/exceptions/unique-conflict.ts` precisará ler também o formato do adaptador.

- **Integração frontend/backend da E1:** verificada no navegador (Chromium) contra o backend real com o seed: login em `exemplo.localhost`, ligar a disponibilidade, criar pipeline, adicionar, reordenar e editar etapas, tornar padrão, conferir pela API e em 390 px de largura (sem rolagem horizontal). Roteiro fora do repositório; o E2E com Playwright (D-020) continua pendente.

## 2. Legenda

| Status | Significado |
|---|---|
| **Validado** | Implementação existente e comportamento comprovado por testes automatizados adequados (API e, quando há tela, UI). Aceite humano à parte. |
| **Implementado** | Existe no código, sem prova suficiente (sem teste, sem medição ou sem uso ponta a ponta). |
| **Parcial** | Existe, mas falta parte do fluxo, da regra ou da tela. |
| **Não iniciado** | Sem implementação identificável. |
| **Bloqueado** | Depende de decisão, informação, integração ou recurso externo. |

## 3. Requisitos funcionais (26; RF-20 removido pela D-070)

| RF | Status | Evidência | Lacuna |
|---|---|---|---|
| RF-01 Login JWT + refresh em cookie, pelo endereço da empresa | Validado | `auth.e2e`, `rbac-tenant-domains.e2e`, `session-lifecycle.e2e`; `LoginPage` | — |
| RF-02 Logout individual e global | Validado | `auth.e2e` (logout, logout-all); `AppShell` | — |
| RF-03 Redefinição de senha | Parcial | `account-recovery.e2e` (troca própria e link do Admin, D-064) | "Esqueci minha senha" por e-mail espera a D-040 |
| RF-04 Vários usuários e papéis por tenant | Validado | `users`, `rbac-tenant-domains.e2e`; `UsersPage` | Papéis customizados pela UI adiados (D-050) |
| RF-05 Dado de negócio pertence a um tenant | Validado | `tenant-isolation.e2e` e testes de isolamento por módulo | — |
| RF-06 Usuário só lê o próprio tenant | Validado | idem; guards globais | Escritas dos repositórios também filtram por `tenantId` desde 12/11/2026 (DV-11 resolvida) |
| RF-07 Super Admin provisiona e suspende | Parcial | Suspensão (MAT-008, `session-lifecycle.e2e`); provisionamento por script (`tenant:provision-trial`, D-059) | Não existe Platform Owner nem Central Administrativa |
| RF-08 CRUD com soft delete de Clientes, Leads, Contatos, Oportunidades | Validado | `customers`, `leads`, `opportunities.e2e`; telas de lista, detalhe, edição e exclusão | Exclusão em cascata indefinida (DV-08) |
| RF-09 Pipelines e etapas configuráveis | **Validado** (E1) | API: `opportunities.e2e` › Pipelines + Stages; tela: `PipelinesSettingsPage.test.tsx` | Antes da E1 só pela API |
| RF-10 Histórico de mudança de etapa | **Validado** (E2) | Gravação (`opportunities.e2e` › Move) e leitura `GET /v1/opportunities/{id}/stage-history` (`opportunities.e2e` › stage-history); `StageHistorySection` no detalhe | Antes da E2, gravado e invisível |
| RF-11 Ganha/Perdida com motivo de perda | Validado | `opportunities.e2e` › Win/Lose; `OpportunityActionPanel` | Motivo é texto livre; a BR-12 pede lista configurável (DV-04) |
| RF-12 Distribuição round-robin; Lead sem dono é válido | Validado | `leads.e2e`, `distribution-availability.e2e` (concorrência) | Política posterior de Leads sem dono (VN-16) |
| RF-13 Tarefas, notas e compromissos vinculados | Validado | `follow-up.e2e`; seções no detalhe de Cliente, Lead e Oportunidade; `/follow-ups` | — |
| RF-14 Tags e campos personalizados | Parcial | `tags` e `custom_fields` (JSONB) aceitos pela API de Clientes/Leads | Nenhuma tela mostra ou edita tags; gestão visual adiada (D-009) |
| RF-15 Disponibilidade do consultor | **Validado** (E1, escopo F4) | `availability.e2e`, `tenant-settings.e2e`; seletor, `/team/availability` e `/settings/availability` | Antes da E1 o Admin não tinha como ligar o mecanismo pela tela. Filas: Fase 5 |
| RF-16 Distribuir só a ativos e disponíveis | Parcial | Leads: `distribution-availability.e2e` (D-078) | Conversas e atendimentos: Fase 5 |
| RF-17 Disposição do atendimento | Bloqueado | — | BR-15 depende de decisão de negócio (D-070, VN-12) |
| RF-18 Histórico completo por cliente | Parcial | Timeline do Cliente consolida as interações das Oportunidades dele (D-095, `interactions-timeline.e2e`) | Conversas e mensagens ainda fora da timeline; Lead de origem fora por decisão (D-079) |
| RF-19 Supervisão em tempo real | Parcial | `/team/availability` com polling de 30 s | Sem tempo real (D-013) e sem filas: Fase 5 |
| RF-21 WhatsApp | Bloqueado | — | Gate da Fase 5 (D-072) |
| RF-22 Abstração de canais | Parcial | Núcleo de conversas agnóstico (`channel_type`, D-081) | `ChannelAdapter`: Fase 5 |
| RF-23 Webhook idempotente | Bloqueado | — | Fase 5 |
| RF-24 Dashboard de vendas e atendimento | Parcial | `GET /v1/dashboard/summary` (`branding-dashboard.e2e`); painel inicial | Funil, conversão, SLA e filtros: Fase 7 |
| RF-25 Exportação de relatórios | Não iniciado | — | Fase 7 (D-038) |
| RF-26 Notificações | Parcial | Só `lead.assigned` (`notifications.e2e`, D-080) | Tarefa vencendo e oportunidade parada exigem agendador (DV-06) |
| RF-27 Log de auditoria | Validado | `audit_log` gravado na transação da mutação em todos os módulos de negócio | Consulta (UC-10) não existe por decisão (D-060, DV-07) |

**Distribuição (depois da E2):** Validado 13 · Implementado 0 · Parcial 9 · Não iniciado 1 · Bloqueado 3. Na auditoria (antes da E1): Validado 10 · Parcial 12.

## 4. Requisitos não funcionais (17)

| RNF | Status | Evidência | Lacuna |
|---|---|---|---|
| RNF-01 Listagens ≤ 300 ms (p95), paginação obrigatória | Implementado | Paginação offset/cursor em todas as listagens | Latência nunca medida (D-049) |
| RNF-02 Backend sem estado, escala horizontal | Implementado | Sessão no banco, rate limit no Redis | Rate limit cai para memória sem Redis (contagem por instância) |
| RNF-03 Processos pesados assíncronos | Validado | Importação de Leads em fila BullMQ, em lotes (D-096): `lead-imports.e2e` (202 imediato, lotes, retomada), medição no navegador (API respondendo em 6–25 ms durante uma importação de 343 linhas) | Relatórios e envio em massa ainda não existem |
| RNF-04 Fallback de WebSocket | Bloqueado | Sem WebSocket (D-013); polling | Fase 5 |
| RNF-05 Falha de provedor externo não derruba o sistema | Parcial | Módulo legado desligado por padrão (D-097): nenhuma chamada externa sem a chave | Quando religado, ainda sem timeout; tratar na F5.0 |
| RNF-06 Filas com retry, backoff e dead-letter | Parcial | Retry e backoff no legado e na fila de exemplo | Sem dead-letter explícita |
| RNF-07 HTTPS/WSS | Bloqueado | HSTS do Helmet | Sem ambiente de deploy (D-027) |
| RNF-08 Hash forte de senha | Validado | bcrypt 6; testes de auth | — |
| RNF-09 Tenant e permissão em todo endpoint | Validado | Guards globais; e2e de RBAC e isolamento | — |
| RNF-10 Upload validado | Validado | Importação: limite de 10 MB, só `.csv`/`.xlsx`, até 5.000 linhas, lida na requisição; só as linhas (texto) ficam no banco, o arquivo não é guardado; `lead-imports.e2e` e testes da tela | Não há armazenamento de arquivos ainda |
| RNF-11 LGPD (acesso, correção, exclusão) | Bloqueado | — | D-047 |
| RNF-12 Utilizável em 360 px | Implementado | Mobile First; evidências do MAT-014 e da E1 em 390 px | Sem verificação sistemática por tela |
| RNF-13 Primeiro atendimento em 15 min de treino | Bloqueado | — | Depende de teste com usuário |
| RNF-14 Log estruturado com request id e tenant | Implementado | `http-logger.config.ts` (tenant, usuário, redação de segredos) | Correlação além do id incremental do pino não verificada |
| RNF-15 Health checks | Validado | `health.e2e` (`/health`, `/health/ready`) | — |
| RNF-16 Contrato versionado | Validado | `/v1`, `openapi.yaml`; teste de contrato no CI (`api-contract-routes.e2e` e `api-contract-responses.e2e`, 13/11/2026): paridade de rotas e de status de sucesso em todas as rotas, schema das respostas numa amostra | Formato conferido só na amostra; corpo de requisição e mudança incompatível entre versões do contrato não automatizados; login e refresh respondem 201 contra 200 do contrato (DV-14, exceção no teste) |
| RNF-17 ADR para decisão arquitetural | Implementado | ADR-001 a 012 | — |

**Distribuição:** Validado 6 · Implementado 5 · Parcial 2 · Bloqueado 4 (recontada em 13/11/2026).

## 5. Casos de uso do MVP

| UC | Situação | Observação |
|---|---|---|
| UC-01 Captação e distribuição | Implementado | Cadastro manual, distribuição e **importação pela tela** (D-096: envio, andamento, erros por linha, link para os Leads); falta aceite humano |
| UC-02 Qualificação e conversão | Validado | Qualificar → converter (Cliente novo ou existente, deduplicação) → "Criar oportunidade" em dois passos |
| UC-03 Pipeline | Validado | Kanban, salto com justificativa (corrigido na E1 para contar etapas), ganho e perda; histórico de etapas visível desde a E2 |
| UC-04 Follow-up e agenda | Parcial | Tarefas e compromissos com conclusão; "notifica antes do vencimento" não existe (DV-06) |
| UC-09 Configuração inicial do tenant | Parcial | Usuários, papéis (leitura), origens, horário, disponibilidade e pipelines pela tela (E1); filiais e equipes sem CRUD (D-058) |
| UC-10 Auditoria | Não iniciado | D-060: só gravação |
| UC-11 a UC-15 (Fase 4) | Validado | Disponibilidade (ligável pela tela desde a E1), interações, notificações, conversas e liberações; MATs com aceite humano pendente |
| UC-05 a UC-08 | Fora do MVP | Telefonia fora de escopo (D-070); WhatsApp na Fase 5 |

**Critério de saída do MVP** ([mvp.md](../10-roadmap/mvp.md) §5): o fluxo Lead → distribuição → contato → qualificação → oportunidade → negociação → venda/perda roda ponta a ponta, multi-tenant e com RBAC. A captura de erros prevista no MVP está implementada e desligada por padrão (D-101, 13/11/2026): falta ligá-la, o que depende do responsável; o E2E de navegador do fluxo principal (D-020) foi entregue em 12/11/2026 (§9). Importação pela tela (D-096) e histórico único do cliente (D-095) foram entregues em 10/11/2026.

## 6. Maturidade por módulo

| Módulo | Funciona de ponta a ponta | Incompleto | Testes | Falta para "pronto" |
|---|---|---|---|---|
| Autenticação e sessão | Sim | E-mail de recuperação (D-040) | e2e auth, sessão, rate limit, várias abas | Aceite humano D-084, D-090, D-091 |
| Usuários e papéis | Sim | Papéis customizados pela UI (D-050) | e2e RBAC, UI `UsersPage` | Aceite humano D-087, D-093 |
| Tenants, planos e trial | Sim, provisionamento por script | Platform Owner, checkout, consumo de armazenamento | e2e trial | Decisões comerciais |
| Clientes e contatos | Sim | Tags na tela; cascata na exclusão | e2e, UI | DV-08 |
| Leads e origens | Sim (manual e importação, D-096) | Deduplicação no cadastro manual | e2e, UI | Aceite humano |
| Pipelines e oportunidades | Sim (E1, E2, D-099) | — | e2e, UI | Aceite humano |
| Follow-up | Sim | Aviso de vencimento | e2e, UI | DV-06 |
| Interações e timeline | Por entidade | Histórico único | e2e, UI | DV-01 |
| Notificações | `lead.assigned` | Demais gatilhos; retenção | e2e, UI | DV-06, D-047 |
| Conversas (manual) | Sim | Disposição, transferência, filas (VN-12) | e2e, UI | Fase 5 |
| Disponibilidade | Sim (E1) | — | e2e, UI | Aceite humano |
| Horário e liberações | Sim, sem ativação real | Lacunas conhecidas PN-3 | e2e, MAT 009–016 assistidos | Aceite humano; runbook em ambiente real |
| Identidade visual | Sim | Logo e favicon (sem upload) | e2e, UI | Aceite humano |
| Dashboard | Resumo | Indicadores da Fase 7 | e2e | Fase 7 |
| Auditoria | Gravação | Consulta | via e2e dos módulos | D-060 |
| `communications` (legado) | Ativo, congelado | Fora da especificação | unitários | DV-09 |

## 7. Divergências e decisões pendentes encontradas

| ID | Divergência | Onde | Decisão necessária |
|---|---|---|---|
| DV-01 | O critério de aceite da Fase 4 pede "linha do tempo única" do cliente com leads e oportunidades; a D-079 proíbe herança Lead × Cliente e não decide Oportunidade → Cliente | roadmap Fase 4 × D-079, VN-14 | **Decidida: D-095** (Cliente + Oportunidades dele; Lead não) |
| DV-02 | BR-05 ainda diz "dentro do horário de atendimento"; a D-078 diz que o horário não filtra a distribuição | business-rules × D-078 | Só ajuste de texto da BR-05 |
| DV-03 | O MVP diz que a importação é a única fila justificada; ela é síncrona e não tem tela | mvp.md §2, RNF-03 × `leads.service.ts` | **Resolvida: D-096** (fila BullMQ em lotes e tela de importação, 10/11/2026) |
| DV-04 | BR-06 e BR-12 pedem motivos de lista configurável; o modelo usa texto livre | business-rules × entities.md | **Resolvida: D-099** implementada em 12/11/2026 (motivos padrão das empresas novas confirmados pelo responsável em 12/11/2026) |
| DV-05 | D-032 "Impacto em código" falava em `order` adjacente; o código comparava a diferença numérica, o que trata etapas vizinhas como salto quando há lacunas | D-032 × `opportunities.service.ts` | **Resolvida na E1** pela regra de negócio (salto = etapa ativa no meio), sem mudar a decisão |
| DV-06 | UC-04 e RF-26 pedem aviso de tarefa vencendo; a D-080 limita a v1 a `lead.assigned` | use-cases × D-080 | Agendador e ator Sistema (P1) |
| DV-07 | UC-10 pede consulta da auditoria; a D-060 deixou só gravação | use-cases × D-060 | Quando abrir a consulta e para quem |
| DV-08 | Excluir um Cliente deixa Oportunidades abertas e Leads convertidos apontando para ele; a spec não define cascata | `customers.service.ts` | **Decidida: D-098** (409, sem cascata) |
| DV-09 | O módulo `communications` está "congelado" (D-073), mas registra varredura de hora em hora e expõe `/v1/automations` e `/v1/messages` a Admin e Gerente, com credencial global, sem timeout e sem opt-in | D-073 × `whatsapp-queue.service.ts`, `tenant-roles.ts` | **Decidida: D-097** (desligado por padrão até a F5.0) |
| DV-10 | O MVP prevê captura de erro (Sentry); não existe | mvp.md §2 | **Implementada em 13/11/2026, desligada por padrão: [D-101](../00-governance/decision-register.md#d-101--captura-de-erros-sentry-desligada-por-padrão-e-regras-de-privacidade)** (`PROPOSTO`); ligar depende de conta, plano, região, retenção e DSN do responsável |
| DV-11 | `update/delete where { id }` em 22 repositórios dependem de o service buscar antes com `tenantId` | repositórios | **Resolvida em 12/11/2026**: escritas com `{ id, tenantId }` e teste que impede a volta do padrão |
| DV-12 | Documentos defasados: "Próximas ações" do `PROJECT-CONTEXT` tratava o D1 do F4.7 como não integrado; status do `crm-backend/CLAUDE.md` e do `crm-frontend/CLAUDE.md` são da Fase 1 | — | Só atualização |
| DV-14 | `POST /v1/auth/login` e `POST /v1/auth/refresh` respondem **201**; o contrato e o exemplo de `api-guidelines.md` §9 dizem **200** (as ações de senha usam `@HttpCode(200)`; outras ações POST respondem 201). Achado pelo teste de contrato | `auth.controller.ts` × `openapi.yaml` | Alinhar um dos lados: `@HttpCode(200)` nas duas rotas (ajustar `loginAs` e e2e que esperam 201) ou documentar 201. Até lá, exceção no teste |
| DV-13 | `crm-spec` e `crm-frontend` são públicos no GitHub (registrado no `CLAUDE.md` deste repositório desde a Fase 1) | GitHub | Reavaliar antes de produção: a spec descreve a arquitetura de segurança, os runbooks e as lacunas conhecidas |

## 8. Plano de entregas

| Entrega | Prioridade | Conteúdo | Depende de | Critério de aceite | Situação |
|---|---|---|---|---|---|
| **E1** Configuração pela tela | P1 | Ligar/desligar disponibilidade; pipelines e etapas; correção do filtro `unassigned=false`; salto de etapa por contagem (DV-05) | — | Admin configura tudo pela tela; testes de API e UI; e2e de salto com lacuna e `order` espaçado; `unassigned=false` não filtra | **Concluída em 10/11/2026** (branches locais, sem push; seção 9) |
| E2 Histórico de etapas visível | P1 | `GET /v1/opportunities/{id}/stage-history` (aditivo no OpenAPI) e seção no detalhe da Oportunidade | — | Mostra de/para, usuário, data e justificativa; isolamento e RBAC testados | **Concluída em 10/11/2026** (seção 9) |
| E3 Importação de Leads pela tela | P1 | Fila BullMQ, lotes, acompanhamento e erros por linha; tela de upload | D-096 | Arquivo válido importa sem bloquear a API; progresso e erros visíveis; tenant respeitado | **Concluída em 10/11/2026** (seção 9) |
| E4 Histórico único do cliente | P1 | Agregar timeline conforme a decisão | D-095 | Critério de aceite da Fase 4 cumprido | **Concluída em 10/11/2026** (E5, seção 9) |
| E5 Contenção do legado | P0 de produção | Chave de ambiente desligando rotas, varredura e envio do `communications` | D-097 | Desligado: rotas recusadas, nenhuma varredura, nenhum envio | **Concluída em 10/11/2026** (E3, seção 9) |
| E6 Integridade | P2 | Cascata de exclusão (DV-08); `updateMany` com `tenantId` (DV-11); mapeamento P2002 compatível com o adaptador do Prisma 7 | DV-08 | Testes de cascata e de repositório | **Concluída** (DV-08 pela D-098 em 10/11; DV-11 e P2002 em 12/11/2026, seção 9) |
| E7 Preparação para produção | P3 | Playwright do fluxo do MVP (D-020; **fluxo principal e acessibilidade entregues em 12/11/2026**, ver §9), Sentry (DV-10; **implementado e desligado por padrão em 13/11/2026**, ver §9; ligar depende do responsável, D-101), teste de carga (D-049), runbook de permissões F4.2/F4.4/F4.6 para empresas existentes (**comando e runbook entregues em 13/11/2026**, ver §9; execução em ambiente real pendente), proteção de branch (D-021/D-052) | D-025, D-027 a D-029, D-036, D-047 | Fluxo do MVP automatizado no CI | Parcialmente bloqueada |
| E8 Experiência visual | P4 | Textos sem acento na UI ("Historico", "Nao foi possivel"...), hierarquia e navegação | E1–E7 | — | **Em andamento**: textos, ficha de registro, Follow-ups, filtros e acessibilidade em 12/11/2026 (seção 9) |

## 9. Registro de entregas

### E1 — 10/11/2026
- **Backend** (branch `fix/e1-unassigned-filter-and-stage-skip`, a partir de `906e13d`): `GET /v1/conversations?unassigned=false` deixou de devolver só as sem responsável (o `@Transform` lia o valor já convertido pelo `enableImplicitConversion`; agora lê o bruto, como `access-exception.dto.ts`; valor não booleano = 400). Salto de etapa (D-032) passou a contar as etapas ativas entre origem e destino (`PipelinesService.countStagesBetween`, na transação do move). Testes: `conversation.dto.spec.ts` (4) e casos novos em `conversations.e2e` e `opportunities.e2e` (lacuna de etapa excluída; `order` 10/20/30). Mutação confirmada: sem as correções, os testes novos falham.
- **Frontend** (branch `feat/e1-settings-availability-pipelines`, a partir de `3d40079`): Configurações > Disponibilidade (`/settings/availability`) e Configurações > Pipelines e etapas (`/settings/pipelines`); a tela da equipe aponta para onde ligar; o painel de movimentação usa a mesma regra de salto. 27 testes novos (`AvailabilitySettingsPage`, `PipelinesSettingsPage`, `lib/stages`, `OpportunityActionPanel`, `TeamAvailabilityPage`).
- **Sem migration, sem regra de negócio nova, sem alteração do OpenAPI** (os contratos usados já existiam).
- **Requisitos:** RF-09 e RF-15 passaram a Validado; DV-05 resolvida.
- **Pendente:** push e PRs (aguardam autorização), CI no GitHub, aceite humano.

### E2 — 10/11/2026
- **Backend** (branch `feat/e2-opportunity-stage-history`, empilhada sobre a E1): `GET /v1/opportunities/:id/stage-history` (`opportunities:read`), mais recente primeiro, cursor opaco `(changed_at, id)`, `limit` 1..100 (padrão 50); etapas excluídas aparecem pelo nome; mesma visibilidade da oportunidade (404 para inexistente, excluída ou de outro tenant). 4 e2e novos (jornada completa com salto e ganho, cursor sem repetir nem pular, etapa excluída, isolamento e RBAC).
- **Frontend** (branch `feat/e2-opportunity-stage-history`, empilhada sobre a E1): `StageHistorySection` no detalhe da Oportunidade, com "Carregar mais"; atualiza após mover, ganhar ou perder. 3 testes novos.
- **Contrato:** path e schemas `OpportunityStageHistoryItem`/`OpportunityStageHistoryList` adicionados ao `openapi.yaml` (aditivo; 80 paths, nenhuma referência quebrada).
- **Integração:** verificada no navegador contra o backend real (mover pulando etapa com justificativa e ver o histórico atualizar).
- **Testes:** backend unitários 433/433, integração 2/2, e2e 507/508 (mesma falha de ambiente da §1); frontend 443/443; lint, `tsc` e build OK.
- **Requisitos:** RF-10 passou a Validado.

### E3 — `communications` desligado por padrão (D-097) — 10/11/2026
- **Backend** (`feat/e3-communications-off`, empilhada sobre a E2): chave `COMMUNICATIONS_LEGACY_ENABLED` (padrão desligado); sem varredura agendada (e a antiga removida do Redis), worker fechado, rotas `403 COMMUNICATIONS_DISABLED`, provider sem ler credencial global; dados preservados. Testes: `legacy-switch.spec.ts`, spec do service ajustado ao modo ligado, e2e `communications-off` e `communications-legacy-on`; o e2e do MVP passou a esperar o 403.

### E4 — exclusão de Cliente com Oportunidade aberta (D-098) — 10/11/2026
- **Backend** (`feat/e4-customer-delete-guard`, empilhada sobre a E3): `409 CUSTOMER_HAS_OPEN_OPPORTUNITIES`, sem cascata; encerradas preservadas; trava compartilhada na criação de Oportunidade contra a corrida. 4 e2e novos (aberta bloqueia, encerradas não, aberta excluída não, corrida sem órfão).
- **Frontend** (`feat/e4-customer-delete-guard`): teste que fixa a exibição da mensagem do 409 no detalhe do Cliente (a tela já mostrava a mensagem da API).
- **Contrato:** 409 documentado em `DELETE /customers/{id}`.
- **DV-08** resolvida.

### E5 — timeline consolidada do Cliente (D-095) — 10/11/2026
- **Backend** (`feat/e5-customer-consolidated-timeline`, empilhada sobre a E4): a timeline do Cliente soma as interações das Oportunidades não excluídas dele, por consulta, para quem tem `opportunities:read`; itens com `entity_type`/`entity_id`. 2 unitários e 1 e2e (Lead, Oportunidade excluída, outro Cliente e notas de Oportunidade fora; cursor de 1 em 1; nada copiado; leitor sem a permissão).
- **Frontend** (`feat/e5-customer-consolidated-timeline`): item de Oportunidade marcado com link; criar/excluir interação recarrega todas as timelines. 1 teste novo (445/445).
- **Contrato:** `TimelineItem` ganhou `entity_type`/`entity_id` (aditivo) e a descrição de `/customers/{id}/interactions`.
- **DV-01** resolvida pela D-095.

### Importação de Leads em fila (D-096; plano E3) — 10/11/2026
- **Backend** (`feat/d096-async-lead-import`): `POST /v1/leads/import` lê o arquivo, grava a importação e uma linha pendente por linha do arquivo (mesma transação, auditada) e responde **202**; o worker da fila `lead-imports` processa lotes de 100 linhas, cada lote um job, com o seguinte no fim da fila (empresas diferentes se intercalam). Cada Lead e o resultado da sua linha na mesma transação, com teste-e-set da linha (dois processamentos do mesmo lote não duplicam). Antes de cada lote: quem importou ativo e com `leads:create`/`leads:read`, `allowsBackgroundWork`, origem e responsável existentes; senão a importação para com `failure_code`. Job leva só tenant e id; toda consulta filtra pelos dois. Retomada na subida para importação sem job. Consulta: `GET /v1/lead-imports`, `/{id}` e `/{id}/rows` (`leads:create` + `leads:read`, offset). Migration aditiva `lead_imports`/`lead_import_rows`. `QUEUE_PREFIX` separa as filas dos e2e das de um `npm run dev` no mesmo Redis.
- **Frontend** (`feat/d096-lead-import-page`): `/leads/imports` (envio com origem e responsável opcional, lista das importações) e `/leads/imports/:id` (andamento a cada 2 s enquanto roda, contadores, motivo de interrupção, linhas filtráveis com link para o Lead criado ou já existente); botão "Importar" na lista de Leads.
- **Contrato:** `/leads/import` (202), `/lead-imports`, `/lead-imports/{id}`, `/lead-imports/{id}/rows` e os schemas `LeadImport*` no `openapi.yaml`.
- **Testes:** backend unitários 451/451 (12 novos em `lead-import-row.rules` e `lead-import.processor`), integração 2/2, e2e 532/533 (17 novos em `lead-imports.e2e`; os 6 e2e que importavam passaram a esperar a fila; a falha é a de ambiente da §1); frontend 454/454 (9 novos); lint, `tsc` e build OK.
- **Integração:** no navegador contra o backend real com o seed: arquivo de 343 linhas (340 novas, 1 repetida, 2 inválidas) respondido em 219 ms, concluído em 6,8 s, `/health` respondendo em 6–25 ms durante o processamento; lista e detalhe em 1280 e 390 px sem rolagem horizontal.
- **Requisitos:** RNF-03 e RNF-10 passaram a Validado; UC-01 a Implementado; DV-03 resolvida.
- **Limites registrados:** a leitura do arquivo continua na requisição (até 10 MB); as linhas importadas ficam guardadas sem prazo (retenção junto com a D-047); duas importações simultâneas da mesma empresa podem criar o mesmo Lead se as duas tiverem a mesma pessoa (a deduplicação não trava, como no cadastro manual); a consulta das importações fica fora da restrição por horário, como o envio (PN-2).

### Integridade: escritas com tenant e P2002 pelo adaptador (plano E6) — 12/11/2026
- **Backend** (`fix/tenant-scoped-writes`, sobre a D-096; **local, sem commit**): os `update`/`delete` de 12 repositórios (appointments, contacts, customers, interactions, lead-sources, leads, notes, opportunities, pipelines, roles, tasks, users) passaram a filtrar por `{ id, tenantId }`. `tenant-scoped-writes.spec.ts` lê os repositórios e falha se uma escrita só por `id` voltar (exceções: legado `communications`, congelado, e o cursor do round-robin, travado por tenant na transação). `unique-conflict.ts` passou a ler o P2002 também no formato do adaptador de driver (capturado de verdade com `@prisma/adapter-pg`), o que prepara o Prisma 7.
- **Sem migration, sem mudança de contrato nem de regra de negócio.**
- **Testes:** unitários 460/460, e2e **533/533** (a falha de ambiente da §1 deixou de existir: era o P2002 pelo adaptador), lint, `tsc` e build OK. CI do GitHub ainda não executado para esta entrega.
- **DV-11 resolvida.**

### Motivos de perda e de desqualificação em listas (D-099) — 12/11/2026
- **Backend** (`feat/d099-reason-catalogs`, sobre `fix/tenant-scoped-writes`): módulo `closing-reasons` (lista por tipo, criar, renomear, excluir; "Outro" protegido; nome único por lista sob trava), `resolveForUse` na transação de perder e de desqualificar, colunas `*_reason_id` e `*_note`, migration aditiva `20261112120000_closing_reasons` (cria "Outro" para as empresas existentes com UUID v7 montado em SQL), `seedTenantCatalogs` com os motivos iniciais.
- **Frontend** (`feat/d099-reason-catalogs`, sobre a D-096): Configurações > Motivos (duas listas), seletor de motivo + observação/justificativa ao perder e ao desqualificar, exibição da observação no detalhe.
- **Contrato:** `/closing-reasons`, `/closing-reasons/{id}`, `ClosingReasonChoice` em `/lose` e `/disqualify` (incompatível com o texto livre anterior, por decisão), campos novos em `Lead` e `Opportunity`.
- **Testes:** backend unitários 460/460, e2e **546/546** (13 novos em `closing-reasons.e2e`: listas, CRUD, corrida de nomes, "Outro", RBAC, isolamento entre empresas, histórico preservado, legado em texto livre, semeadura idempotente; 14 chamadas antigas adaptadas); frontend 462/462 (8 novos); lint, `tsc` e build OK. Navegador contra o backend real: criar motivo, desqualificar com "Outro" + justificativa, perder com o motivo novo; 1280 e 390 px sem rolagem horizontal. CI do GitHub: ver o PR.
- **Requisitos:** BR-06 e BR-12 atendidas; DV-04 resolvida.
- **Motivos padrão:** confirmados pelo responsável em 12/11/2026 (D-099, item 5), iguais aos implementados.
- **Pendente:** rodar `tenant:seed-catalogs` nas empresas existentes (não executado em ambiente real).

### Experiência visual, primeira parte (plano E8) — 12/11/2026
- **Frontend** (`feat/ui-text-and-consistency`): ficha de registro única para Lead, Cliente e Oportunidade (`components/record`: cabeçalho com as ações principais, barra do funil, coluna de trabalho e resumo ao lado, primeiro no celular); cerca de 200 textos de tela passaram a português com acentos e "tenant" saiu do texto visível; `ui-text.test.ts` impede a volta; tabela de últimos leads do painel sem cortar o status.
- **Backend** (`feat/api-messages-accents`): mensagens de exceção e descrições do Swagger com acentos (a tela mostra a `message` quando não traduz o `code`). Códigos, status e comportamento inalterados.
- **Testes:** frontend 463/463, lint, tipos e build; backend 460 unitários e 546/546 e2e. Telas conferidas no navegador em 1280 e 390 px.
- **Falta na E8:** Follow-ups sem criação direta, filtros de lista (responsável, sem responsável), estados vazios com ação, revisão de acessibilidade.

### Experiência visual, segunda parte (plano E8) — 12/11/2026
- **Frontend** (`feat/ui-followups-and-filters`): Follow-ups abre nas tarefas de quem está logado e alterna para a equipe; cria tarefa avulsa e conclui na própria lista; o formulário de tarefa sugere 9h do dia seguinte e permite escolher o responsável. Listas de Leads e Oportunidades com filtro de responsável (meus, colega e, em Leads, sem responsável); lista vazia sob filtro oferece limpar os filtros.
- **Backend** (`feat/leads-unassigned-filter`): `GET /v1/leads?unassigned=true` (prevalece sobre `owner_id`; mesmo padrão de Conversas). Contrato atualizado no `openapi.yaml`.
- **Acessibilidade:** telas principais verificadas com axe (WCAG 2 A/AA). Corrigidos o contraste do selo de erro (4,41:1 para acima de 4,5:1), a estrutura da lista de definição do resumo e o texto auxiliar do pipeline. Resultado final: nenhuma violação nas 20 telas verificadas (largura de 1280 px, tema padrão). Não cobre tema escuro nem identidade personalizada por empresa.
- **Testes:** frontend 469/469, lint, tipos e build; backend: suíte e2e de Leads 37/37 local (suíte completa no CI do PR).
- **Fora desta entrega (precisa de decisão):** criar compromisso direto em Follow-ups. O compromisso não tem título nem descrição no modelo; solto, seria só um horário. Proposta: acrescentar `title` opcional a `appointments` (migration aditiva).
- **Falta na E8:** nada em aberto além do que a entrada seguinte registra como não coberto.

### E2E de navegador e acessibilidade no tema escuro (plano E7, parte; fecha a "revisão de acessibilidade" da E8) — 12/11/2026
- **Frontend** (`test/e2e-playwright`): suíte Playwright em `e2e/` (`npm run test:e2e`, só Chromium, contra o backend real com o seed, em `exemplo.localhost`).
  - `01-main-flow`: login → Lead (nome, telefone, origem) → qualificar → converter em Cliente novo → Oportunidade → ganhar → estado "Ganha" na tela, também após recarregar. Dados com sufixo único por execução.
  - `02-accessibility`: axe (WCAG 2 A e AA) em 15 telas autenticadas (início; leads lista, novo, detalhe; clientes lista, detalhe; oportunidades lista, detalhe; pipeline; follow-ups; conversas; configurações; usuários; plano; minha conta) e num diálogo aberto, em quatro identidades visuais (padrão clara, tema escuro, personalizada clara, personalizada escura), mais a tela de login. Verificações objetivas: foco visível (contorno ≥ 2 px, contraste ≥ 3:1), diálogo (foco entra, permanece, Esc fecha, foco volta), menu por teclado, "Mais" no celular, 390 px sem rolagem horizontal em 13 telas.
  - O tema escuro e as identidades personalizadas são ativados respondendo ao `GET /v1/branding` no navegador do teste (aplicar de verdade exige `branding:manage`, da plataforma). As duas paletas personalizadas foram conferidas contra a validação do backend.
- **Correções que a suíte motivou** (todas por token ou estrutura, sem mudança de regra): `<dl>` inválido no resumo de Lead/Cliente/Oportunidade; texto de erro sobre o fundo suave em 4,41:1 (`--color-danger` passa a `#b91c1c`; nos temas de empresa as cores de estado são ajustadas até AA contra o próprio fundo suave); total da coluna do pipeline em 4,34:1; contorno de foco da barra lateral (2,67:1 numa identidade personalizada) passa a usar a tinta da barra; diálogos passam a manter Tab e Shift+Tab dentro do painel. No tema escuro padrão o axe não encontrou violação de contraste.
- **CI** (crm-backend `ci/browser-e2e`): job `browser-e2e` com PostgreSQL e Redis descartáveis, `migrate deploy` + seed, API real, checkout do crm-frontend sem segredo (branch de mesmo nome, senão a provisória `test/e2e-playwright`, senão `main`), Vite com `/v1` encaminhado preservando o `Host`, relatório e traces como artefato em caso de falha. O CI do crm-frontend não ganha job de navegador (o backend é privado); a pasta `e2e/` passa por lint e tipos lá.
- **Testes (local):** Playwright **96/96** em três execuções seguidas (duas com o Vite já no ar, uma com o Playwright subindo o Vite em modo CI), cerca de 2,5 min cada; Vitest 469/469; lint, `tsc` e build OK. **CI do GitHub:** job `browser-e2e` verde na primeira execução (crm-backend #21).
- **Não cobre:** registrar atendimento/conversa, permissões por papel (só o Admin do seed), importação de Leads, restrição por horário, trial expirado, Firefox/WebKit, leitor de tela real, critérios WCAG que o axe não automatiza; gravação e validação da identidade visual no backend (ficam nos e2e da API); a tela de login só existe na identidade padrão.
- **Observação de produto (sem mudança):** o formulário "Converter em cliente > Novo cliente" não vem preenchido com os dados do Lead; "Novo lead" na lista é botão que navega, não link.

### Regularização de acesso das empresas existentes (plano E7, parte) — 13/11/2026
- **Backend** (`feat/tenant-access-regularization`): `npm run tenant:regularize-access` (`prisma/tenant-access-regularization.ts` + CLI `prisma/regularize-tenant-access.ts`). Concede aos papéis de fábrica existentes só as permissões de `availability`, `interactions` e `conversations` previstas em `FACTORY_ROLES` e ausentes (42 concessões em 8 papéis numa empresa sem nenhuma). Simulação por padrão em transação somente leitura; aplicação por empresa, sob o advisory lock das mudanças de papel (chave extraída para `src/common/rbac/access-lock.ts`), com `audit_log` na mesma transação. Sem migration, sem mudança no provisionamento de empresa nova, sem mudança de contrato.
- **Achado**: os três recursos são permissões de papel; `conversations` é também funcionalidade de plano (bloqueia a escrita) e a disponibilidade depende de `crm.availability.enabled`, que o provisionamento de empresa nova não grava. Plano e configuração são só relatados.
- **Spec**: [runbook-tenant-access-regularization.md](../08-devops/runbook-tenant-access-regularization.md); [D-100](../00-governance/decision-register.md#d-100--regularização-de-acesso-das-empresas-existentes-regras-do-passo) (`PROPOSTO`).
- **Testes (local, banco descartável):** `tenant-access-regularization.e2e-spec.ts` **33/33**; com `rbac-tenant-domains` e `tenant-catalogs`, 63/63 (antes do teste de reversão); unitários 460/460; lint e `tsc` OK. Suíte e2e completa: só no CI.
- **Não cobre:** execução em ambiente real, volume grande de empresas, MATs; `access_exceptions:manage` e marcadores do F4.7 (runbook próprio); demais divergências dos papéis de fábrica fora do escopo (só relatadas).

### Captura de erros (DV-10, D-101; plano E7, parte) — 13/11/2026
- **Backend** (`feat/error-monitoring`): `src/common/monitoring` com a interface `ErrorReporter` (Sentry e nula; só `sentry-error-reporter.ts` importa `@sentry/node` 10.x). Reporta 5xx que não é de domínio no `AllExceptionsFilter`, a falha definitiva do lote da importação de Leads e erro fatal do processo; `beforeSend` por lista de permissão, reaproveitando a lista de redação dos logs. Variáveis `SENTRY_DSN`, `SENTRY_ENVIRONMENT`, `SENTRY_RELEASE`, `SENTRY_TRACES_SAMPLE_RATE` (padrão 0). Sem migration, sem mudança de contrato.
- **Frontend** (`feat/error-monitoring`): `features/monitoring`, SDK `@sentry/react` por import dinâmico e fora do precache do PWA; tela de erro "Algo deu errado" com "Recarregar" no `errorElement` das rotas de topo e num boundary externo; erros não tratados da janela; `ApiError` 4xx nunca reportado; fragmento (`#token=`) e query string nunca saem. Variáveis `VITE_SENTRY_DSN`, `VITE_SENTRY_ENVIRONMENT`, `VITE_SENTRY_RELEASE`. Bundle inicial 627,54 → 630,59 kB (gzip 172,82 → 173,93 kB); o SDK (88,5 kB, gzip 30,2 kB) só é baixado com DSN.
- **Spec**: [D-101](../00-governance/decision-register.md#d-101--captura-de-erros-sentry-desligada-por-padrão-e-regras-de-privacidade) (`PROPOSTO`) e [runbook](../08-devops/runbook-error-monitoring.md).
- **Testes:** backend unitários 506/506 e e2e `error-monitoring` 10/10 (com `health`, `auth`, `lead-imports` e `session-lifecycle`, 57/57); frontend 487/487 (18 novos). Sem rede: transporte falso, SDK real com transporte em memória e coletor HTTP local (API e navegador com e sem DSN: sem DSN, nenhuma requisição ao SDK nem ao coletor).
- **Não cobre:** envio a um Sentry real (sem conta), ligação em qualquer ambiente, Playwright (nada do que a suíte cobre mudou).

### Teste de contrato da API (RNF-16) — 13/11/2026
- **Backend** (`test/api-contract`): `test/e2e/utils/api-contract.ts` lê o `openapi.yaml` (`OPENAPI_SPEC_PATH`, padrão `../crm-spec/...`; sem o arquivo, falha com a causa). `api-contract-routes.e2e`: rotas do Express × operações do contrato nos dois sentidos, status de sucesso pelos metadados do Nest (com autoverificação do caminho remontado) e exceções que deixaram de valer. `api-contract-responses.e2e`: `expectMatchesContract(res, 'GET /v1/leads/{id}', 200)` valida o corpo com Ajv (OpenAPI 3.0 convertido: `nullable`, `$ref`, formatos) e acusa campo não declarado; casos de violação do próprio verificador. CI: o job `backend` baixa o crm-spec sem token. Dependências de desenvolvimento: `ajv`, `ajv-formats`, `js-yaml` (já presentes como transitivas).
- **Contrato corrigido** (`docs/api-contract`): chave `"422"` duplicada em `POST /opportunities/{id}/lose` (o YAML perdia a primeira; unificadas); `GET /roles/{id}` (existia sem contrato); campos do Lead da D-094 (`name`, `document`, `phone`, `email`, `custom_fields`) na resposta, na criação e na edição; `birth_date` e `last_interaction_at` do Cliente; 401 em `GET /users/me` e 400 em `POST /leads`.
- **Exceções registradas no teste:** `/health` e `/health/ready` (fora de `/v1`); rotas do legado `communications` (D-073/D-097); `/calls/*` do contrato (D-070, mantidas por rastreabilidade); status 201 de login e refresh (DV-14).
- **Testes (local, banco descartável):** contrato **14/14** (4 de rotas e status, 10 de respostas: 34 conferências em 31 operações); com `health` e `auth`, 28/28; as 354 respostas documentadas compilam no Ajv; unitários 460/460; lint, `tsc` e build OK; `npm audit --omit=dev`: 0 vulnerabilidades. Falhas conferidas: rota apagada ou renomeada no contrato e arquivo ausente geram a mensagem esperada. Suíte e2e completa: só no CI.
- **Não cobre:** corpo de requisição; formato das respostas fora da amostra (as demais rotas só por paridade e status); mudança incompatível entre versões do `openapi.yaml`.
