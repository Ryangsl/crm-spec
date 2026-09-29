# Project Context

> Checkpoint operacional de continuidade do projeto. **Não substitui** o [Decision Register](docs/00-governance/decision-register.md), o [Roadmap](docs/10-roadmap/roadmap.md), o [Requirements](docs/01-product/requirements.md) ou qualquer outro documento oficial do `crm-spec` — em caso de conflito, os documentos oficiais prevalecem. Serve apenas para que uma nova sessão/agente entenda rapidamente onde o projeto parou, sem reauditar tudo do zero.

## Última atualização
- **Data**: 29/09/2026
- **Commit/referência**: crm-spec — `docs(product): finalize availability business rules` (último código: `ec63390` crm-backend · `dacf723` crm-frontend, inalterados)
- **Repositório**: crm-spec
- **Ação realizada**: consolidação das regras de negócio de disponibilidade (D-071), distinção Lead x Cliente, princípio da ociosidade de atendimento e terminologia do produto ("CRM Universal") — documentação apenas.

## Estado atual

**Fase 3 — CRM Comercial: CONCLUÍDA.** Os incrementos 3.1 a 3.6 estão concluídos e com commits fechados nos três repositórios (`crm-backend`, `crm-frontend`, `crm-spec`): Fundação Frontend Auth/RBAC, Customers/Contacts, Leads com round-robin, Pipelines, Opportunities e agora Follow-up (Notes/Tasks/Appointments). Em 2026-09-21 houve um ajuste de escopo de produto (D-070/D-071) que redefiniu o significado funcional das Fases 3–6 (CRM Comercial + Atendimento/Conversas + WhatsApp + futuro Omnichannel, sem Call Center telefônico) — ajuste documental, sem alterar código nem decisões já fechadas (D-031 a D-069). A Fase 3 está concluída; a Fase 4 (Atendimento/Conversas) ainda não foi iniciada. Em 2026-09-29 as regras de negócio de disponibilidade (D-071) foram consolidadas — D-071 deixa de bloquear o conceito básico de disponibilidade; sua implementação técnica será planejada na Fase 4.

## Última ação realizada

- **O que foi feito**: consolidação, com o responsável pelo produto, das regras de negócio de disponibilidade em [D-071](docs/00-governance/decision-register.md#d-071--disponibilidade-de-consultoratendente-para-distribuição-automática) — sem código, Prisma, migration, API ou frontend:
  - **Estados**: Disponível, Indisponível, Pausa, Almoço, Treinamento. Só **Disponível** recebe distribuição automática. Disponibilidade **global por usuário** (não por canal/fila).
  - **Alteração de status**: o próprio consultor controla; **Treinamento** só é definido/removido por Gestor ou Sistema (o consultor não entra nem sai dele). Configuração por tenant fica para o futuro.
  - **`business_hours`**: configuração administrativa do tenant (quando implementada); **não altera o status** automaticamente; pode restringir acesso de consultores a Leads/Conversas fora do horário, com liberação excepcional pelo Admin (detalhes técnicos na implementação) — BR-27.
  - **Lead x Cliente**: o CRM diferencia claramente Lead de Cliente; Lead não é tratado como Cliente — BR-28.
  - **Ociosidade**: regra de atendimento/conversa de **Cliente**, não de Lead; interações do consultor (ex.: "Só mais um momento") devem ser consideradas para evitar transferência indevida; regra de 5 minutos e demais detalhes adiados para o incremento da Fase 4 de atendimento de Cliente — BR-28. Não implementada.
  - **Terminologia**: o produto é o **"CRM Universal"** — CRM para empresas de vendas, também utilizável para controle e gestão de cadastros; "Call Center" não define o produto.
- **Repositórios/commits**:
  - crm-spec: `docs(product): finalize availability business rules`
  - crm-backend / crm-frontend: não alterados.
- **Arquivos/áreas afetadas**: `docs/00-governance/decision-register.md` (D-071, tabela de fases, histórico), `docs/02-business/business-rules.md` (BR-05, BR-14, BR-16, novas BR-27/BR-28), `docs/01-product/requirements.md` (RF-15), `docs/10-roadmap/roadmap.md` (Fase 3 concluída, Fase 4), `PROJECT-CONTEXT.md`.
- **Resultado**: regras de negócio de disponibilidade fechadas; nenhuma decisão anterior reaberta; nenhum código alterado.
- **Push**: sim, `origin/main` (crm-spec).

## Próxima etapa

- **Fase**: 4 — Atendimento/Conversas
- **Objetivo**: histórico unificado de interações (Lead/Cliente/Oportunidade) e disponibilidade de consultor/atendente. As regras de negócio de disponibilidade já estão fechadas (D-071); falta o **planejamento técnico** dentro da Fase 4. A regra detalhada de ociosidade de atendimento de Cliente será definida no incremento correspondente da Fase 4.
- **Repositório(s) envolvidos**: crm-backend, crm-frontend, crm-spec.

## Próximas ações

1. Iniciar a Fase 4 somente com autorização explícita; o primeiro passo é o planejamento técnico (não iniciado).
2. No planejamento técnico da disponibilidade: representação do estado atual vs. histórico (reaproveitando o conceito `agent_status_log`/RF-15, cujo enum em `entities.md` precisa ser revisto para os cinco estados), nomenclatura neutra, relação com login/logout, fallback para tenants sem disponibilidade e tratamento de leads já atribuídos (lacunas remanescentes de D-071).
3. Aplicar a disponibilidade ao Round Robin (evolução da F3.4, D-068): ativo + **Disponível** + permissão.
4. Definir o desenho do módulo de Interações (histórico unificado) sem antecipar WhatsApp (Fase 5).
5. No incremento de atendimento/conversas de Cliente: fechar os detalhes da ociosidade (BR-28) e as pendências de D-070 (BR-15/16/18, filas, terminologia de papéis).
6. Manter os mesmos padrões consolidados (tenant isolation, RBAC, soft delete, audit, OpenAPI, testes).
7. Ao concluir cada incremento da Fase 4, atualizar este arquivo (`PROJECT-CONTEXT.md`) com data, commits, resultado e próxima etapa.

## Decisões pendentes

| ID | Decisão necessária | Impacto | Fase limite | Status |
|----|---------------------|---------|--------------|--------|
| D-071 (implementação) | Planejamento técnico da disponibilidade: estado atual vs. histórico, nomenclatura neutra, relação com login/logout, fallback para tenant sem disponibilidade, leads já atribuídos a quem fica indisponível, formato de `business_hours` e da liberação excepcional pelo Admin | Distribuição automática por disponibilidade; acesso fora do horário | Planejamento da Fase 4 | Regras de negócio `DECIDIDO` (2026-09-29); implementação a planejar |
| D-071 (ociosidade) | Detalhes da ociosidade de atendimento de Cliente: regra de 5 minutos, eventos que reiniciam o contador, seleção do próximo consultor, prioridade, mensagens automáticas, transferência | Atendimento/conversas de Cliente (BR-28) | Incremento de atendimento de Cliente (Fase 4) | `VALIDAÇÃO DE NEGÓCIO` (princípio já `DECIDIDO`) |
| D-070 (pendências) | O que caracteriza uma Conversa/atendimento "finalizado"; limite de pausa e destinatário do alerta (e se Almoço/Treinamento contam); pontos de medição do SLA; se "filas" de atendimento existem já na Fase 4 ou só na Fase 5; terminologia dos papéis "Supervisor/Operador de Call Center" | BR-15, BR-16, BR-18 e nomenclatura de papéis (Fase 4/5) | Antes da fase que as implementa (Fase 4/5) | `VALIDAÇÃO DE NEGÓCIO` |

**D-071 deixou de ser decisão de negócio bloqueante** para o conceito básico de disponibilidade. As pendências acima são decididas no incremento da Fase 4 que as implementar — não impedem o início da Fase 4.

## Restrições importantes

- Não implementar telefonia, PSTN, URA, discador ou gravação de chamadas — fora de escopo do produto (D-070).
- Disponibilidade de consultor/atendente pertence à Fase 4: implementar somente após o planejamento técnico da fase, seguindo as regras de D-071. Não implementar a regra de ociosidade antes de seus detalhes serem definidos no incremento de atendimento de Cliente.
- Lead não é Cliente (BR-28): regras de atendimento de Cliente (ex.: ociosidade) não se aplicam a Lead.
- Usar a terminologia "CRM Universal"; não definir o produto como "Call Center".
- Reutilizar módulos/modelos já existentes antes de criar qualquer estrutura nova (ex.: F3.6 reaproveitou o padrão do módulo `tasks` para `notes`/`appointments`); manter o modelo polimórfico `entity_type` + `entity_id` (D-031), sem colunas de FK dedicadas por tipo de entidade.
- Manter tenant isolation, RBAC, soft delete e auditoria consistentes com os padrões já implementados em Customers/Leads/Opportunities/Notes/Tasks/Appointments.
- Não avançar automaticamente para a próxima fase (Fase 4) sem fechamento formal do incremento/fase atual.
- Não reabrir decisões já fechadas (D-031 a D-069), o ajuste de escopo D-070 nem as regras de negócio de D-071.
- `crm-spec` continua sendo a fonte oficial de especificações e decisões; este arquivo é apenas um checkpoint operacional.

## Histórico recente

| Data | Repositório | Ação | Commit | Resultado |
|------|-------------|------|--------|-----------|
| 2026-09-20 | crm-backend | Implementação de Opportunities + Pipeline (F3.5) | `d2ee3b3` | Módulo de funil implementado |
| 2026-09-20 | crm-frontend | Implementação de Opportunities + Pipeline (F3.5) | `e0063d2` | UI de funil implementada |
| 2026-09-20 | crm-spec | Documentação da API de Opportunities/Pipeline | `0387ae5` | OpenAPI atualizado |
| 2026-09-21 | crm-spec | Ajuste de escopo de produto — D-070/D-071 (CRM Comercial + Atendimento/Conversas + WhatsApp, sem Call Center telefônico) | `651b2c9` | Roadmap, business-rules e decision-register atualizados; código e decisões fechadas (D-031–D-069) preservados |
| 2026-09-27 | crm-backend | Alinhamento do README com D-070 | `0a5f681` | Documentação alinhada; nenhum código alterado; push feito |
| 2026-09-27 | crm-spec | Criação do checkpoint operacional `PROJECT-CONTEXT.md` | `60c2e22` | Arquivo criado; nenhuma decisão nova/reaberta |
| 2026-09-27 | crm-backend | F3.6 — Notes/Appointments implementados (Tasks já existia); e2e Follow-up | `ec63390` | 175 testes passando (35 unit + 140 e2e); lint/build limpos; push feito |
| 2026-09-27 | crm-frontend | F3.6 — UI de Notes/Tasks/Appointments integrada em Customer/Lead/Opportunity | `dacf723` | 128 testes passando; lint/type-check/build limpos; push feito |
| 2026-09-27 | crm-spec | F3.6 — OpenAPI de Notes/Tasks/Appointments | `dcb4189` | YAML validado, todos os $ref resolvidos; push feito |
| 2026-09-27 | crm-spec | Atualização do PROJECT-CONTEXT após F3.6 | `a642465` | Checkpoint atualizado; push feito |
| 2026-09-29 | crm-spec | Consolidação das regras de disponibilidade (D-071), Lead x Cliente, ociosidade (princípio), "CRM Universal" | `docs(product): finalize availability business rules` | Documentação apenas; nenhum código alterado; push feito |

## Roadmap atual

- **Fase atual**: Fase 3 — CRM Comercial — **concluída** (incrementos 3.1–3.6, incluindo Follow-up)
- **Próxima fase**: Fase 4 — Atendimento/Conversas (histórico unificado de interações, disponibilidade de consultor/atendente — regras de negócio fechadas em D-071, implementação técnica a planejar) — **não iniciada**
- **Fases posteriores (resumo)**:
  - Fase 5 — WhatsApp/Conversas (integração com provedor oficial/BSP, conversas distribuídas por disponibilidade)
  - Fase 6 — Omnichannel (novos canais além do WhatsApp em caixa de entrada unificada)
  - Fase 7 — Dashboard (indicadores de vendas e atendimento)
  - Fase 8 — Automações (campanhas, regras simples de automação)
  - Fase 9 — Escalabilidade (mediante evidência real de necessidade)
  - Fase 10+ — conforme [roadmap.md](docs/10-roadmap/roadmap.md)

## Regra de continuidade

Ao iniciar uma nova etapa:

1. Ler este arquivo primeiro.
2. Consultar os documentos oficiais referenciados quando necessário (Decision Register, Roadmap, Requirements, entities.md, etc.).
3. Verificar o estado real do repositório antes de implementar (não presumir que algo já existe ou já foi feito).
4. Não repetir trabalho já concluído.
5. Não alterar decisões já fechadas.
6. Ao finalizar uma etapa, atualizar este arquivo com a nova data, ação, commit, resultado e próxima etapa.
