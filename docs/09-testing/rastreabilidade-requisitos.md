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
| RF-06 Usuário só lê o próprio tenant | Validado | idem; guards globais | Padrão frágil: `update/delete where { id }` dependem da busca prévia no service (ver DV-11) |
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
| RF-18 Histórico completo por cliente | Parcial | Timeline Interações + Notas por entidade (`interactions-timeline.e2e`) | Sem agregação Lead → Cliente → Oportunidade; conflito roadmap × D-079 (DV-01, VN-14) |
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
| RNF-03 Processos pesados assíncronos | Parcial | — | Importação de Leads síncrona (até 5.000 linhas), contra o RNF e o MVP (DV-03) |
| RNF-04 Fallback de WebSocket | Bloqueado | Sem WebSocket (D-013); polling | Fase 5 |
| RNF-05 Falha de provedor externo não derruba o sistema | Parcial | — | Módulo legado `communications` chama o WhatsApp sem timeout (DV-09) |
| RNF-06 Filas com retry, backoff e dead-letter | Parcial | Retry e backoff no legado e na fila de exemplo | Sem dead-letter explícita |
| RNF-07 HTTPS/WSS | Bloqueado | HSTS do Helmet | Sem ambiente de deploy (D-027) |
| RNF-08 Hash forte de senha | Validado | bcrypt 6; testes de auth | — |
| RNF-09 Tenant e permissão em todo endpoint | Validado | Guards globais; e2e de RBAC e isolamento | — |
| RNF-10 Upload validado | Implementado | Importação: limite de 10 MB, só `.csv`/`.xlsx`, processada em memória | Não há armazenamento de arquivos ainda |
| RNF-11 LGPD (acesso, correção, exclusão) | Bloqueado | — | D-047 |
| RNF-12 Utilizável em 360 px | Implementado | Mobile First; evidências do MAT-014 e da E1 em 390 px | Sem verificação sistemática por tela |
| RNF-13 Primeiro atendimento em 15 min de treino | Bloqueado | — | Depende de teste com usuário |
| RNF-14 Log estruturado com request id e tenant | Implementado | `http-logger.config.ts` (tenant, usuário, redação de segredos) | Correlação além do id incremental do pino não verificada |
| RNF-15 Health checks | Validado | `health.e2e` (`/health`, `/health/ready`) | — |
| RNF-16 Contrato versionado | Implementado | `/v1`, `openapi.yaml` | Sem teste de contrato automático |
| RNF-17 ADR para decisão arquitetural | Implementado | ADR-001 a 012 | — |

**Distribuição:** Validado 3 · Implementado 7 · Parcial 3 · Bloqueado 4.

## 5. Casos de uso do MVP

| UC | Situação | Observação |
|---|---|---|
| UC-01 Captação e distribuição | Parcial | Cadastro manual e distribuição funcionam; **importação só pela API** (sem tela) |
| UC-02 Qualificação e conversão | Validado | Qualificar → converter (Cliente novo ou existente, deduplicação) → "Criar oportunidade" em dois passos |
| UC-03 Pipeline | Validado | Kanban, salto com justificativa (corrigido na E1 para contar etapas), ganho e perda; histórico de etapas visível desde a E2 |
| UC-04 Follow-up e agenda | Parcial | Tarefas e compromissos com conclusão; "notifica antes do vencimento" não existe (DV-06) |
| UC-09 Configuração inicial do tenant | Parcial | Usuários, papéis (leitura), origens, horário, disponibilidade e pipelines pela tela (E1); filiais e equipes sem CRUD (D-058) |
| UC-10 Auditoria | Não iniciado | D-060: só gravação |
| UC-11 a UC-15 (Fase 4) | Validado | Disponibilidade (ligável pela tela desde a E1), interações, notificações, conversas e liberações; MATs com aceite humano pendente |
| UC-05 a UC-08 | Fora do MVP | Telefonia fora de escopo (D-070); WhatsApp na Fase 5 |

**Critério de saída do MVP** ([mvp.md](../10-roadmap/mvp.md) §5): o fluxo Lead → distribuição → contato → qualificação → oportunidade → negociação → venda/perda roda ponta a ponta, multi-tenant e com RBAC. Faltam: importação pela tela, histórico único do cliente (decisão), Sentry (previsto no MVP) e o E2E de navegador (D-020).

## 6. Maturidade por módulo

| Módulo | Funciona de ponta a ponta | Incompleto | Testes | Falta para "pronto" |
|---|---|---|---|---|
| Autenticação e sessão | Sim | E-mail de recuperação (D-040) | e2e auth, sessão, rate limit, várias abas | Aceite humano D-084, D-090, D-091 |
| Usuários e papéis | Sim | Papéis customizados pela UI (D-050) | e2e RBAC, UI `UsersPage` | Aceite humano D-087, D-093 |
| Tenants, planos e trial | Sim, provisionamento por script | Platform Owner, checkout, consumo de armazenamento | e2e trial | Decisões comerciais |
| Clientes e contatos | Sim | Tags na tela; cascata na exclusão | e2e, UI | DV-08 |
| Leads e origens | Sim (manual) | Importação pela tela; deduplicação no cadastro manual | e2e, UI | E3 |
| Pipelines e oportunidades | Sim (E1, E2) | Motivo de perda em lista | e2e, UI | DV-04 |
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
| DV-03 | O MVP diz que a importação é a única fila justificada; ela é síncrona e não tem tela | mvp.md §2, RNF-03 × `leads.service.ts` | **Decidida: D-096** (fila BullMQ, até 5.000 linhas em lotes) |
| DV-04 | BR-06 e BR-12 pedem motivos de lista configurável; o modelo usa texto livre | business-rules × entities.md | **Decidida: D-099** (listas por tenant, "Outro" com justificativa) |
| DV-05 | D-032 "Impacto em código" falava em `order` adjacente; o código comparava a diferença numérica, o que trata etapas vizinhas como salto quando há lacunas | D-032 × `opportunities.service.ts` | **Resolvida na E1** pela regra de negócio (salto = etapa ativa no meio), sem mudar a decisão |
| DV-06 | UC-04 e RF-26 pedem aviso de tarefa vencendo; a D-080 limita a v1 a `lead.assigned` | use-cases × D-080 | Agendador e ator Sistema (P1) |
| DV-07 | UC-10 pede consulta da auditoria; a D-060 deixou só gravação | use-cases × D-060 | Quando abrir a consulta e para quem |
| DV-08 | Excluir um Cliente deixa Oportunidades abertas e Leads convertidos apontando para ele; a spec não define cascata | `customers.service.ts` | **Decidida: D-098** (409, sem cascata) |
| DV-09 | O módulo `communications` está "congelado" (D-073), mas registra varredura de hora em hora e expõe `/v1/automations` e `/v1/messages` a Admin e Gerente, com credencial global, sem timeout e sem opt-in | D-073 × `whatsapp-queue.service.ts`, `tenant-roles.ts` | **Decidida: D-097** (desligado por padrão até a F5.0) |
| DV-10 | O MVP prevê captura de erro (Sentry); não existe | mvp.md §2 | Ferramenta e orçamento |
| DV-11 | `update/delete where { id }` em 22 repositórios dependem de o service buscar antes com `tenantId` | repositórios | Defesa em profundidade (`updateMany` com `tenantId`) — técnica, sem regra nova |
| DV-12 | Documentos defasados: "Próximas ações" do `PROJECT-CONTEXT` tratava o D1 do F4.7 como não integrado; status do `crm-backend/CLAUDE.md` e do `crm-frontend/CLAUDE.md` são da Fase 1 | — | Só atualização |
| DV-13 | `crm-spec` e `crm-frontend` são públicos no GitHub (registrado no `CLAUDE.md` deste repositório desde a Fase 1) | GitHub | Reavaliar antes de produção: a spec descreve a arquitetura de segurança, os runbooks e as lacunas conhecidas |

## 8. Plano de entregas

| Entrega | Prioridade | Conteúdo | Depende de | Critério de aceite | Situação |
|---|---|---|---|---|---|
| **E1** Configuração pela tela | P1 | Ligar/desligar disponibilidade; pipelines e etapas; correção do filtro `unassigned=false`; salto de etapa por contagem (DV-05) | — | Admin configura tudo pela tela; testes de API e UI; e2e de salto com lacuna e `order` espaçado; `unassigned=false` não filtra | **Concluída em 10/11/2026** (branches locais, sem push; seção 9) |
| E2 Histórico de etapas visível | P1 | `GET /v1/opportunities/{id}/stage-history` (aditivo no OpenAPI) e seção no detalhe da Oportunidade | — | Mostra de/para, usuário, data e justificativa; isolamento e RBAC testados | **Concluída em 10/11/2026** (seção 9) |
| E3 Importação de Leads pela tela | P1 | Fila BullMQ, lotes, acompanhamento e erros por linha; tela de upload | D-096 | Arquivo válido importa sem bloquear a API; progresso e erros visíveis; tenant respeitado | Decidida; a implementar |
| E4 Histórico único do cliente | P1 | Agregar timeline conforme a decisão | D-095 | Critério de aceite da Fase 4 cumprido | Decidida; a implementar |
| E5 Contenção do legado | P0 de produção | Chave de ambiente desligando rotas, varredura e envio do `communications` | D-097 | Desligado: rotas recusadas, nenhuma varredura, nenhum envio | Decidida; a implementar |
| E6 Integridade | P2 | Cascata de exclusão (DV-08); `updateMany` com `tenantId` (DV-11); mapeamento P2002 compatível com o adaptador do Prisma 7 | DV-08 | Testes de cascata e de repositório | Parte técnica pronta para iniciar |
| E7 Preparação para produção | P3 | Playwright do fluxo do MVP (D-020), Sentry (DV-10), teste de carga (D-049), runbook de permissões F4.2/F4.4/F4.6 para empresas existentes, proteção de branch (D-021/D-052) | D-025, D-027 a D-029, D-036, D-047 | Fluxo do MVP automatizado no CI | Parcialmente bloqueada |
| E8 Experiência visual | P4 | Textos sem acento na UI ("Historico", "Nao foi possivel"...), hierarquia e navegação | E1–E7 | — | Depois |

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
