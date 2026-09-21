# Decision Register

Registro central de todas as decisões do projeto. Substitui a leitura de `[DECISÃO PENDENTE]` espalhado pelos documentos: cada ocorrência nos documentos agora carrega um status e aponta para uma entrada `D-xxx` deste registro.

## Como usar

Cada decisão tem um **status**:

| Status | Significado | Bloqueia desenvolvimento? |
|---|---|---|
| `DECIDIDO` | Decisão definitiva para a fase atual | Não — é para seguir |
| `PROPOSTO` | Direção definida, pode ser refinada depois | Não |
| `ADIADO` | Não precisa ser decidido agora | Não |
| `VALIDAÇÃO DE NEGÓCIO` | Depende de stakeholders humanos, não de arquitetura | Só na fase que depende dela |
| `BLOQUEADOR` | Precisa ser resolvido antes da fase correspondente | Sim, para aquela fase |

**Regra principal**: uma decisão pendente só bloqueia o desenvolvimento quando impacta diretamente a implementação ou os critérios de aceite da fase atual. Nenhuma decisão marcada `ADIADO`, `PROPOSTO` ou `VALIDAÇÃO DE NEGÓCIO` justifica parar uma fase que não depende dela.

## Situação atual

**Bloqueadores para a FASE 1 (Fundação técnica): nenhum.** A Fase 1 pode iniciar imediatamente.

| Fase | Decisões que precisam estar resolvidas antes |
|---|---|
| Fase 1 — Fundação técnica | D-001, D-012, D-017, D-018, D-020, D-021, D-022, D-023 — todas `DECIDIDO`/`PROPOSTO`. Nada pendente. |
| Fase 2 — Auth/Usuários/Tenants | D-002, D-003, D-004, D-005, D-006, D-016, D-037, D-056 a D-063 — todas `DECIDIDO`. Nada pendente. |
| Fase 3 — CRM | D-007, D-008, D-031, D-032, D-033, D-034, D-035, D-058, D-065, D-066, D-067, D-068, D-069 — todas `DECIDIDO`. Nada pendente. Decision Gate (2026-09-16) e Implementation Gate (2026-09-16) concluídos. |
| Fase 4 — Atendimento/Conversas | D-071 (modelagem de disponibilidade — `VALIDAÇÃO DE NEGÓCIO`; a regra já está `DECIDIDO`) e pendências de D-070. Só bloqueiam a parte de disponibilidade/atendimento, não a Fase 3. |
| Fase 5 — WhatsApp/Conversas | D-011, D-013, D-024, D-025, D-039 (D-010 e D-045 — telefonia/discador — estão **fora de escopo**, ver D-070) |
| Fase 6 — Omnichannel | Nenhuma definida hoje; provedores de canais futuros (ex.: D-040) são decididos quando entrarem no roadmap |
| Fase 7+ | D-038, D-040, D-046, D-049 |
| Antes do primeiro cliente em produção | D-027, D-028, D-029, D-043, D-047, D-064 |

---

## Fundação e identidade

### D-001 — Estratégia de identificador primário
**Status**: `DECIDIDO` · **Fase**: 1 · **ADR**: [ADR-009](../adr/ADR-009.md)

UUID **v7** como chave primária de todas as entidades de negócio. Nunca usar ID autoincremental como identificador público.

**Motivo**: ordenação temporal, melhor comportamento de índice (menos fragmentação que v4), não expõe volume/sequência, e facilita paginação cronológica.

### D-017 — Biblioteca de validação de DTO
**Status**: `DECIDIDO` · **Fase**: 1

`class-validator` + `class-transformer` no backend, por integração nativa com os pipes do NestJS. Zod permanece no frontend (React Hook Form). Não usar as duas bibliotecas no backend.

### D-018 — Estado global no frontend
**Status**: `DECIDIDO` · **Fase**: 1

Context API + hooks para o estado global de UI (sessão, tema, conectividade). **Não** adotar Zustand ou outra store no MVP — o volume de estado global é pequeno porque o estado de servidor fica no TanStack Query. Reavaliar apenas se surgir necessidade real.

### D-020 — Ferramenta de E2E de frontend
**Status**: `DECIDIDO` · **Fase**: 1

Playwright.

### D-021 — Plataforma de CI
**Status**: `PROPOSTO` · **Prazo**: início da Fase 1

GitHub Actions como direção. Depende de onde os repositórios serão hospedados — se a hospedagem for outra (GitLab, Bitbucket), trocar a implementação do pipeline sem alterar a estratégia de testes de [../09-testing/testing-strategy.md](../09-testing/testing-strategy.md).

### D-022 — Estratégia de branches
**Status**: `DECIDIDO` · **Fase**: 1

Trunk-based com `main` como única branch de longa duração, mais branches curtas `feature/*`, `fix/*`, `refactor/*`. **Sem** `develop` — não há múltiplos ambientes/times simultâneos que justifiquem o custo do fluxo duplo.

### D-023 — Ambiente de desenvolvimento local
**Status**: `DECIDIDO` · **Fase**: 1

Infraestrutura (PostgreSQL, Redis) em Docker Compose; aplicação (backend/frontend) rodando via `npm run dev` fora de container, por causa do hot reload. Containerizar a aplicação apenas para build/deploy.

---

## Multi-tenancy e segurança

### D-002 — Estratégia de multi-tenancy
**Status**: `DECIDIDO` · **Fase**: 2 · **ADR**: [ADR-004](../adr/ADR-004.md)

PostgreSQL compartilhado com `tenant_id` obrigatório em toda entidade pertencente a um tenant.

**Regra crítica**: o `tenant_id` nunca é recebido do frontend como fonte confiável. O tenant é sempre derivado do contexto autenticado:

```
Request → JWT → Auth Guard → Tenant Context → Service → Repository/Prisma → filtro obrigatório por tenant_id
```

Rotas como `GET /customers?tenant_id=123`, ou qualquer mecanismo em que o usuário escolha livremente o tenant acessado, são proibidas.

### D-003 — PostgreSQL Row Level Security
**Status**: `DECIDIDO` — **opção B: não implementar no MVP** · **Fase**: 2 (fechado em 2026-09-09) · **Gatilho de reavaliação**: ver seção "Quando reabrir"

Análise formal feita ao fechar a Fase 2 (prazo original: "até o fim da Fase 2"). Avaliada nas dez dimensões pedidas:

1. **Benefício de isolamento**: defesa em profundidade — se um Repository novo esquecer o filtro de `tenant_id`, o banco ainda barraria o vazamento.
2. **Complexidade operacional com Prisma, especificamente**: **alta**. Prisma não tem `@@rls` nem qualquer suporte declarativo — RLS exige SQL raw nas migrations (`ENABLE ROW LEVEL SECURITY` + `CREATE POLICY`) e, mais importante, um mecanismo para o Postgres saber qual é o tenant da sessão atual (`current_setting('app.tenant_id')`).
3. **Compatibilidade com Prisma**: aqui mora o risco real. Prisma gerencia um **pool de conexões** — duas queries seguidas do mesmo request não têm garantia de usar a mesma conexão física, exceto dentro de um `$transaction`. Isso significa que, para RLS funcionar corretamente, **toda query tenant-scoped precisaria rodar dentro de uma transação** que abre com `SET LOCAL app.tenant_id = '...'` (a própria documentação do Prisma recomenda exatamente isso, pelo mesmo motivo). Hoje só as mutações que gravam auditoria usam `$transaction` (ver `UsersService.create/update/deactivate`); leituras não. Envolver **toda** leitura em uma transação é uma mudança de arquitetura grande, com custo de performance (conexão presa por request) desproporcional ao ganho atual.
4. **Risco de consultas administrativas**: o Super Admin da plataforma precisa de queries **sem** filtro de tenant (listar todos os tenants). RLS bem feito exigiria um role de banco à parte com bypass, mais uma superfície para acertar.
5. **Impacto em migrations**: cada tabela tenant-scoped precisaria de uma migration própria habilitando RLS + política. Hoje são ~10 tabelas; na Fase 3+ serão dezenas — o custo de manutenção cresce proporcionalmente ao número de tabelas, não é um investimento único.
6. **Impacto em testes**: os testes de integração/e2e criam fixtures via Prisma direto, fora do fluxo de aplicação (`test/e2e/utils/fixtures.ts`) — com RLS ativo, cada fixture precisaria rodar sob um contexto de tenant ou usar um role de bypass, adicionando fricção em toda a suíte existente (52 testes).
7. **Impacto em manutenção**: um módulo/tabela novo precisaria **lembrar** de habilitar RLS + criar a política — isso é, na prática, **mais** um lugar para esquecer, não menos. A "camada adicional" só protege se ninguém esquecer de configurá-la em cada tabela nova, o que é o mesmo tipo de disciplina manual que o filtro no Repository já exige hoje.
8. **Aumenta a segurança de forma relevante na arquitetura atual?** Marginalmente. O filtro central no Repository já é obrigatório, documentado (`backend-architecture.md` seção 5) e **testado**: todo endpoint tenant-scoped exige teste e2e de vazamento cross-tenant (`testing-strategy.md` seção 2) — mecanismo simples, já validado por 13 testes de isolamento passando (`tenant-isolation.e2e-spec.ts`).
9. **Risco de falsa sensação de segurança — sim, e é o ponto decisivo**: implementar RLS incorretamente com Prisma (ex.: usar `SET` em vez de `SET LOCAL` dentro de transação, dado o pool de conexões) pode **vazar** o `tenant_id` de uma sessão para a próxima requisição que reusar a mesma conexão física — um vazamento cross-tenant **pior** do que não ter RLS. E a presença de RLS tende a relaxar a disciplina de testes/filtros na aplicação, que é o mecanismo que hoje comprovadamente funciona.
10. **Alternativas já em uso**: `TenantContextStorage` (AsyncLocalStorage) derivado só do JWT + filtro obrigatório em todo Repository + teste e2e de vazamento obrigatório para todo endpoint novo (regra já em `testing-strategy.md` e nos `CLAUDE.md` dos dois repositórios de código).

**Decisão**: **B) não implementar no MVP.** O custo operacional (rearquitetar toda leitura para rodar em transação) e o risco de introduzir um vazamento por implementação incorreta superam o ganho de defesa em profundidade, dado que o isolamento primário já é testado e validado.

**Regra que permanece inalterada**: os testes automatizados de isolamento cross-tenant continuam obrigatórios para todo endpoint novo, independentemente desta decisão.

**Quando reabrir**: antes de aceitar um cliente com exigência contratual de isolamento reforçado a nível de banco; ou se o número de pessoas/agentes tocando código de Repository crescer a ponto de a disciplina de filtro manual deixar de ser confiável só com revisão de código e teste automatizado. Reabrir com um ADR próprio (não editar esta entrada silenciosamente).

### D-004 — Estratégia de JWT
**Status**: `DECIDIDO` · **Fase**: 2 · **ADR**: [ADR-008](../adr/ADR-008.md)

- Access token: TTL de **15 minutos**.
- Refresh token: TTL de **7 dias**, com **rotação** a cada uso e possibilidade de **invalidação** (revogação individual e global).

### D-005 — Armazenamento do refresh token
**Status**: `DECIDIDO` · **Fase**: 2 · **ADR**: [ADR-008](../adr/ADR-008.md)

Cookie **httpOnly**, `Secure: true` em produção. O access token não é persistido permanentemente no navegador (mantido em memória da aplicação).

### D-006 — Topologia de domínio, SameSite e CSRF
**Status**: `DECIDIDO` · **Fase**: 2

[../08-devops/deployment.md](../08-devops/deployment.md) §2 já fixa a topologia de produção: um único host com Nginx como proxy reverso na frente de backend e frontend — **mesmo site** (mesmo domínio registrável), possivelmente até mesma origem via roteamento por path. Ambiente local também é mesmo site (`localhost`, portas diferentes — SameSite ignora porta).

Com base nisso:
- Cookie de refresh com **`SameSite=Lax`**, sem atributo `Domain` explícito (host-only — mais restritivo que compartilhar entre subdomínios), `Path=/v1/auth` (o cookie só é enviado para os endpoints de auth, nunca para o resto da API), `httpOnly=true`, `Secure=true` apenas quando `NODE_ENV=production`.
- **Token anti-CSRF explícito não é adotado agora** — `SameSite=Lax` já bloqueia o vetor clássico de CSRF (requisição simples disparada por outro site) numa topologia same-site como a definida acima.

**Gatilho de revisão**: se a topologia de deploy mudar para cross-site (frontend e API em domínios registráveis diferentes), este ADR/decisão precisa ser reaberto — `SameSite=Lax` deixa de bastar e um token anti-CSRF passa a ser obrigatório, conforme já antecipado no ADR-008.

### D-016 — Escopo de dados por equipe/filial
**Status**: `DECIDIDO` · **Fase**: 2

Atribuição **estática** usuário → equipe → filial. Hierarquia dinâmica (árvore de gerência com profundidade arbitrária) fica adiada até haver necessidade real validada.

### D-036 — Acesso de suporte do Super Admin a dados de tenant
**Status**: `VALIDAÇÃO DE NEGÓCIO` · **Prazo**: antes do painel de plataforma (pós-MVP)

**Decisão provisória vigente**: o Super Admin **não** possui acesso automático aos dados internos dos tenants. Não há exceção implementável enquanto não existir uma política explícita de suporte — o acesso simplesmente não existe.

O fluxo definitivo depende de política comercial e jurídica (consentimento do tenant, escopo, retenção), por isso permanece como validação de negócio. Não bloqueia o MVP, que não inclui painel de plataforma.

**Evolução futura registrada — "Support Access Controlado"** (não implementar agora): caso a política seja aprovada, o acesso de suporte deve ser desenhado com, no mínimo:
- **motivo obrigatório** registrado no momento da solicitação;
- **acesso temporário**, nunca permanente;
- **auditoria** completa de tudo que for acessado;
- **expiração automática** da concessão;
- **preferência por read-only**.

Qualquer implementação desse acesso exige um ADR próprio antes de codificar.

### D-047 — Fluxo operacional de LGPD (titular de dados)
**Status**: `VALIDAÇÃO DE NEGÓCIO` · **Prazo**: antes do primeiro cliente em produção

Se o atendimento a solicitações de titular (acesso, correção, exclusão) será self-service ou processo manual assistido depende de política jurídica do negócio. O modelo de dados (soft delete + auditoria) já suporta ambos.

---

## Dados e API

### D-007 — Estratégia de paginação
**Status**: `DECIDIDO` · **Fase**: 2 (primeiras listagens) / 3 (consolidação)

Estratégia **híbrida**:
- **Offset** (`?page=1&limit=20`) para recursos administrativos de volume moderado: usuários, clientes, leads, oportunidades, pipelines, configurações.
- **Cursor** (`?cursor=<uuid>&limit=20`) para recursos cronológicos ou potencialmente volumosos: mensagens, interações, eventos, chamadas, logs, histórico de atividades.

Não construir abstração genérica de paginação antes de existir necessidade real.

### D-008 — Campos personalizados (MVP)
**Status**: `DECIDIDO` · **Fase**: 3

Coluna `JSONB` (`custom_fields`) nas entidades que precisarem (Clientes, Leads). Estrutura permite evolução futura para definição de campos por tenant.

### D-009 — Sistema completo de campos personalizados
**Status**: `ADIADO` · **Prazo**: quando houver requisito real validado (pós-MVP)

Ficam fora do MVP: criação visual de campos, permissões por campo, regras complexas de validação, workflows baseados em campos, engine EAV. Objetivo: preparar a arquitetura sem construir uma plataforma de customização prematuramente.

### D-031 — Modelagem polimórfica de notas/tarefas/compromissos
**Status**: `DECIDIDO` · **Fase**: 3 (fechado em 2026-09-16)

Manter `entity_type` + `entity_id` em `notes`, `tasks` e `appointments`, com a integridade do vínculo validada na aplicação (camada de Service), sem coluna de FK dedicada por tipo de entidade.

**Decisão**: confirmar a proposta original — não criar `lead_id`/`customer_id`/`opportunity_id` como colunas separadas. A implementação deve incluir teste automatizado garantindo que `entity_type` + `entity_id` correspondem a uma entidade existente e do mesmo tenant antes da persistência.

**Motivo**: para o volume esperado no MVP, o risco de integridade órfã é mitigado por validação na aplicação coberta por teste; criar três colunas opcionais por entidade aumentaria a verbosidade do modelo sem ganho proporcional agora.

**Gatilho de reabertura**: se a ausência de FK nativa se mostrar um problema real de integridade em produção, reavaliar migração para colunas dedicadas.

### D-030 — Política de deprecação de versão de API
**Status**: `ADIADO` · **Prazo**: antes da primeira mudança incompatível (`/v2`)

Não há consumidor externo nem segunda versão no horizonte; definir o tempo mínimo de convivência entre versões quando houver necessidade concreta.

---

## Comunicação e provedores externos

### D-010 — Provedor de telefonia
**Status**: `ADIADO` · **Prazo**: sem fase — fora do escopo do produto ([D-070](#d-070--definição-de-produto-crm-comercial--atendimentoconversas--whatsapp-sem-call-center-telefônico), 2026-09-21)

**Atualização (D-070)**: o produto deixou de prever telefonia PSTN/Call Center; esta decisão **não é mais pré-requisito da Fase 5** (que passou a ser WhatsApp/Conversas). Só seria retomada por uma nova decisão explícita de escopo.

Texto original: não bloqueia as Fases 1, 2, 3 e 4. A arquitetura precisa apenas garantir a camada de abstração (`TelephonyAdapter` / `ChannelAdapter`), com implementações futuras plugáveis. Não escolher nem integrar provedor sem necessidade de negócio validada.

### D-011 — Provedor de WhatsApp
**Status**: `ADIADO` · **Prazo**: antes da Fase 5 (WhatsApp/Conversas — [D-070](#d-070--definição-de-produto-crm-comercial--atendimentoconversas--whatsapp-sem-call-center-telefônico); antes era "antes da Fase 6")

Direção definida: **WhatsApp Business Platform oficial ou BSP oficial** para o produto SaaS comercial. Soluções não oficiais não podem ser a base do produto principal. Abstração: `ChannelAdapter` com `sendMessage()`, `receiveWebhook()`, `sendTemplate()`, `getMedia()`.

### D-040 — Provedor de e-mail/SMS
**Status**: `ADIADO` · **Prazo**: quando esses canais entrarem no roadmap (pós-Fase 6)

### D-039 — Circuit breaker para provedores externos
**Status**: `ADIADO` · **Prazo**: Fase 5 (primeira integração externa real)

Timeout curto já é exigido desde a primeira integração; a biblioteca/abordagem de circuit breaker se decide com um provedor real em mãos.

### D-024 — Convenção de variáveis de ambiente de provedores
**Status**: `PROPOSTO` · **Prazo**: Fase 5

Prefixo por **capacidade**, não por marca do provedor (`WHATSAPP_*`; `TELEPHONY_*` só se telefonia voltar ao escopo — [D-070](#d-070--definição-de-produto-crm-comercial--atendimentoconversas--whatsapp-sem-call-center-telefônico)), para que a troca de provedor não exija renomear configuração. Consistente com a abstração de canal.

### D-045 — Discador preditivo
**Status**: `ADIADO` · **Prazo**: pós-Fase 5, mediante validação de negócio

Exige motor de pacing e tratamento de requisitos legais de abandono de chamada. MVP de telefonia é discagem manual/click-to-call.

**Atualização ([D-070](#d-070--definição-de-produto-crm-comercial--atendimentoconversas--whatsapp-sem-call-center-telefônico))**: discador e telefonia estão fora do escopo do produto; a decisão permanece registrada só por rastreabilidade.

---

## Infraestrutura, tempo real e escalabilidade

### D-012 — Redis + BullMQ
**Status**: `DECIDIDO` · **Fase**: 1 (infraestrutura disponível) · **ADR**: [ADR-006](../adr/ADR-006.md)

Redis como infraestrutura compartilhada (cache quando necessário, filas, escalabilidade futura de eventos/WebSocket). BullMQ como solução padrão de filas.

**Regra**: não criar filas desnecessárias no MVP. A operação permanece síncrona enquanto não houver necessidade real de processamento assíncrono.

### D-013 — WebSocket
**Status**: `ADIADO` · **Prazo**: Fase 5

Necessário para status de disponibilidade dos atendentes, filas de atendimento, supervisão em tempo real e eventos de conversas/atendimento ([D-070](#d-070--definição-de-produto-crm-comercial--atendimentoconversas--whatsapp-sem-call-center-telefônico): sem eventos de telefonia). Não antecipar implementação de WebSocket na Fase 1.

### D-046 — Adapter Redis para WebSocket multi-instância
**Status**: `ADIADO` · **Prazo**: quando houver mais de uma instância de backend (Fase 5/9)

### D-014 — Escalabilidade avançada
**Status**: `DECIDIDO` (não implementar agora) · **Prazo de revisão**: mediante evidência real

Não implementar prematuramente: Kubernetes, microsserviços, réplicas de leitura, particionamento, multi-região, sistemas distribuídos. Arquitetura inicial: monólito modular + NestJS + PostgreSQL + Redis + BullMQ. Evolução apenas com evidência de volume, gargalo, métrica ou necessidade operacional.

### D-025 — Secrets management em produção
**Status**: `PROPOSTO` · **Prazo**: antes da Fase 5 (primeiro segredo de provedor externo)

Variáveis de ambiente gerenciadas pela plataforma de deploy, com rotação manual documentada. Cofre dedicado (Vault/Doppler) quando o número de integrações crescer.

### D-026 — Registry de imagens Docker
**Status**: `ADIADO` · **Prazo**: antes do primeiro deploy real

### D-027 — Ambiente de staging
**Status**: `PROPOSTO` · **Prazo**: antes do primeiro cliente em produção

Introduzir quando houver mais de um desenvolvedor/agente atuando em paralelo, ou antes do primeiro cliente real — o que vier primeiro.

### D-028 — Retenção de backup
**Status**: `VALIDAÇÃO DE NEGÓCIO` · **Prazo**: antes do primeiro cliente em produção

Período depende de exigência contratual e de LGPD. Backup diário automático já é decidido; o que falta é o prazo de retenção.

### D-029 — Cadência de teste de restore
**Status**: `PROPOSTO` · **Prazo**: antes de produção

Testar restore a cada release relevante de infraestrutura, no mínimo trimestralmente. Restore não testado não conta como backup.

### D-049 — Ferramenta de teste de carga
**Status**: `ADIADO` · **Prazo**: Fase 9 (ou quando houver tráfego real para calibrar)

---

## Produto, MVP e frontend

### D-015 — Escopo oficial do MVP
**Status**: `DECIDIDO`

**Dentro**: CRM, multi-tenancy, RBAC, clientes, leads, distribuição de leads, oportunidades, pipeline, tarefas, notas, agenda básica, registro manual de atendimento, histórico unificado.

**Fora**: telefonia real, integração real com WhatsApp, discador preditivo, Kubernetes, microsserviços, IA como funcionalidade, engine avançada de automação, dashboard analítico complexo, sistema completo de campos personalizados.

### D-037 — Self-service de criação de tenant
**Status**: `DECIDIDO` · **Fase**: 2

Provisionamento manual/assistido no MVP. Self-service (signup público de tenant) fica fora até haver decisão comercial de go-to-market.

### D-050 — Papéis customizados via UI
**Status**: `ADIADO` · **Prazo**: pós-MVP, mediante demanda real

Papéis de fábrica (ver [../01-product/personas.md](../01-product/personas.md)) são suficientes para o MVP. O modelo de dados (`roles` + `permissions`) já suporta papéis customizados sem migração adicional.

### D-038 — Formatos de exportação de relatórios
**Status**: `ADIADO` · **Prazo**: Fase 7

### D-041 — Escopo de funcionamento offline do PWA
**Status**: `DECIDIDO` · **Fase**: 1 (setup) / 3 (uso real)

Apenas cache de assets estáticos e leitura dos últimos dados carregados. **Sem** fila de escrita offline com sincronização — risco de conflito de dados em operação de atendimento não se justifica no MVP.

### D-042 — Breakpoint de transição da navegação
**Status**: `PROPOSTO` · **Prazo**: Fase 3 (com teste em dispositivo real)

Usar apenas largura de viewport como critério (bottom navigation até `md`, sidebar a partir de `lg`). Considerar orientação apenas se o teste em tablet real mostrar problema.

### D-043 — Paleta de marca
**Status**: `VALIDAÇÃO DE NEGÓCIO` · **Prazo**: antes do primeiro cliente/piloto

Não bloqueia a Fase 1: o design system usa paleta neutra de placeholder, com cores como tokens — trocar a paleta depois é alterar tokens, não componentes.

### D-019 — Geração de tipos a partir do OpenAPI
**Status**: `PROPOSTO` · **Prazo**: Fase 2/3, quando o contrato estabilizar

Direção: gerar tipos TypeScript do frontend a partir de [../05-api/openapi.yaml](../05-api/openapi.yaml), em vez de manter tipos manuais duplicados.

### D-044 — Aplicativo mobile nativo
**Status**: `ADIADO` · **Prazo**: pós-MVP, mediante evidência · **ADR**: [ADR-007](../adr/ADR-007.md)

PWA cobre o MVP. Reavaliar apenas se houver necessidade comprovada (ex.: push notification em segundo plano crítico para operadores).

### D-048 — Escopo de IA como funcionalidade do produto
**Status**: `ADIADO` · **Prazo**: Fase 10

---

## Decisões da Fase 1 (fundação técnica)

### D-051 — Prisma 6 e mecanismo de geração de UUID v7
**Status**: `DECIDIDO` · **Fase**: 1 · **Implementa**: [D-001](#d-001--estratégia-de-identificador-primário) / [ADR-009](../adr/ADR-009.md)

Todo modelo declara `@default(uuid(7))` no schema; a geração fica a cargo do Prisma Client, em qualquer caminho de escrita (inclusive aninhado e seed).

**Verificação feita antes de decidir** (nas versões reais do projeto, não por suposição):
- Prisma **5.22 rejeita** `@default(uuid(7))` — o argumento só existe a partir do Prisma 6.6. Por isso o projeto foi atualizado para **Prisma 6.19.3**.
- PostgreSQL **16 não tem `uuidv7()`** nativo (chegou no 18), então gerar no banco exigiria função SQL própria — descartado.
- `uuid@11` fornece `v7()` para o único caso em que a aplicação precisa do id **antes** do insert (id do refresh token, embutido no token entregue ao cliente). Exposto em `src/infrastructure/database/uuid-v7.ts`.

Nenhum `@default(uuid())` (v4), `gen_random_uuid()` ou `randomUUID()` permanece no código — há teste de guarda travando isso.

### D-052 — CI dentro de cada repositório
**Status**: `PROPOSTO` · **Fase**: 1 · **Relacionada**: [D-021](#d-021--plataforma-de-ci)

Os workflows vivem em `crm-backend/.github/workflows/ci.yml` e `crm-frontend/.github/workflows/ci.yml`, não em um workflow único na raiz — a raiz do workspace não é um repositório git, e o projeto é multi-repo por decisão de produto. Escopo da Fase 1: install → lint → test (unitário) → build. Integração/e2e exigem Postgres e Redis e entram na Fase 2.

### D-053 — Ambiente local: um compose com dois modos
**Status**: `DECIDIDO` · **Fase**: 1 · **Relacionada**: [D-023](#d-023--ambiente-de-desenvolvimento-local)

`docker-compose.yml` na raiz do workspace:
- `docker compose up -d` → apenas Postgres e Redis (fluxo diário, apps via `npm run dev` com hot reload — D-023);
- `docker compose --profile apps up --build` → stack completa em container, para validar reprodutibilidade.

Assim o requisito de "ambiente reproduzível com os quatro serviços" convive com D-023 sem contradição.

### D-054 — Versionamento do workspace
**Status**: `DECIDIDO` · **Fase**: 1 (fechamento operacional, 2026-09-09)

Criado o repositório **`crm-workspace`**, separado, responsável por infraestrutura e desenvolvimento local: `docker-compose.yml`, `scripts/` (setup e execução de testes), `.env.example` de ambiente e a documentação de setup integrado.

**Forma escolhida**: a própria pasta que contém os três repositórios *é* o `crm-workspace`, com `crm-backend/`, `crm-frontend/` e `crm-spec/` no `.gitignore`.

**Por quê**: os contextos de build do compose (`./crm-backend`, `./crm-frontend`) continuam válidos sem reescrita, o clone dos três repositórios permanece independente, e nada precisa ser reestruturado. A alternativa — mover os arquivos para uma subpasta `crm-workspace/` — exigiria contextos `../crm-backend` e um layout de clone mais confuso.

**O que continua valendo**: `crm-backend` e `crm-frontend` **não** viram um repositório único; `crm-spec` segue sendo a fonte da verdade da documentação de produto/arquitetura, e o `crm-workspace` documenta apenas ambiente local.

Opções descartadas: mover os arquivos para `crm-spec` (misturaria documentação com runtime) e deixá-los sem versionamento (o problema original).

### D-055 — `endOfLine: auto` no Prettier
**Status**: `DECIDIDO` · **Fase**: 1

Com `core.autocrlf=true` no Windows, o checkout é CRLF enquanto o repositório guarda LF; o Prettier (padrão `lf`) acusava mais de 2000 erros e o lint nunca passava localmente. `endOfLine: "auto"` no `.prettierrc` mais `.gitattributes` com `* text=auto eol=lf` fazem o lint passar no Windows e no Linux sem reescrever nenhum arquivo.

## Decisões da Fase 2 (auth, tenants, users)

Todas resultam da auditoria formal do código que já existia como adiantamento da Fase 1 — ver `crm-spec/CLAUDE.md` e `crm-backend/CLAUDE.md`.

### D-056 — Política de reuso de refresh token (família de sessões)
**Status**: `DECIDIDO` · **Fase**: 2 · **Implementa**: ADR-008

ADR-008 já definia "reuso revoga a família de tokens", mas nunca detalhou o que é "família" nem o que a API deve responder — sem isso, a auditoria da Fase 2 encontrou o método pronto (`revokeAllForUser`) mas nunca chamado. Fechando a lacuna:

- **Família de sessões** = todos os refresh tokens do mesmo `userId`, independentemente de dispositivo/IP (o modelo de dados não distingue dispositivo hoje — granularidade por dispositivo fica para quando houver necessidade real, ex. tela de "sessões ativas").
- **Reuso "comprovado"** — a coluna `revoked_reason` (`rotated` / `logout` / `reuse_detected`) distingue *por que* um token foi revogado. Só reapresentar um token cujo motivo é **`rotated`** conta como reuso de um token já rotacionado (ADR-008) e dispara a varredura da família. Reapresentar um token revogado por **`logout`** é apenas "sessão já encerrada" — comportamento esperado (ex.: uma aba antiga tentando renovar depois que o usuário saiu deliberadamente), não evidência de comprometimento, e **não** varre as demais sessões.
  - Achado durante a implementação: sem essa distinção, um `logout` seguido de qualquer reuso do token (retry de rede, aba duplicada) varria também sessões saudáveis do mesmo usuário em outros dispositivos — falso positivo. Coberto por teste e2e dedicado.
- **Resposta ao cliente**: idêntica a qualquer outro refresh token inválido (401, mesmo código de erro padronizado) — não expõe ao chamador que um reuso foi detectado (isso seria informação útil a um atacante testando o comportamento da API).
- **Registro do evento de segurança**: fica pendente do módulo de auditoria (L1/D-058-adjacent — ver seção "auditoria básica" no roadmap da Fase 2). Até lá, o evento fica implícito no efeito (todas as sessões caem), sem log estruturado dedicado.

### D-057 — Logout global
**Status**: `DECIDIDO` · **Fase**: 2 · **Implementa**: ADR-008/D-004

Novo endpoint `POST /v1/auth/logout-all`, público (não exige access token válido — útil quando ele já expirou), identifica o usuário pelo refresh token apresentado (cookie) e revoga todos os refresh tokens ativos daquele `userId`. Mesmo mecanismo de revogação usado pela resposta a reuso (D-056).

### D-058 — Escopo de RBAC na Fase 2 e na Fase 3: apenas tenant
**Status**: `DECIDIDO` · **Fase**: 2 · **Reafirmado para a Fase 3 em 2026-09-16**

A Fase 2 implementa e valida **RBAC com escopo de tenant apenas**: uma permissão concedida (ex.: `users:read`) dá acesso a todos os recursos daquele tenant, sem filtro adicional por equipe/filial. `teamId`/`branchId` continuam existindo no schema (suporte de D-016), mas nenhum código de autorização os utiliza ainda.

**Decisão do Decision Gate da Fase 3 (2026-09-16)**: a Fase 3 **não ativa** o escopo por Equipe/Filial. O CRM da Fase 3 continua usando **somente escopo por Tenant** como isolamento de dados — assim como na Fase 2. Não implementar nesta fase: filtro por `team_id`/`branch_id` em listagens/consultas de CRM, CRUD de `Team`, CRUD de `Branch`, ou qualquer regra de visibilidade por equipe/filial. A coluna "R (equipe)"/"CRUD (equipe)" da matriz de [../01-product/personas.md](../01-product/personas.md) §3 (Gerente/Supervisor) continua **não aplicada** — esses papéis leem/gerenciam o tenant inteiro também na Fase 3, exatamente como na Fase 2.

**Motivo**: ativar o escopo Equipe/Filial exigiria construir CRUD de Team/Branch (que não têm controller/tela hoje) e adicionar filtro em praticamente todo endpoint de CRM — escopo que o roadmap original da Fase 3 não previa. Manter o escopo simples (Tenant) evita aumentar o tamanho da fase sem necessidade validada.

A estrutura de dados (`teamId`/`branchId`) permanece preparada para a evolução futura, sem migração destrutiva quando o escopo for ativado. **Fase de ativação**: a definir (fica para uma fase futura, não amarrada a nenhum número específico do roadmap atual) — não simular esse escopo parcialmente enquanto não for essa fase.

### D-059 — Provisionamento de tenant permanece manual (Fase 2)
**Status**: `DECIDIDO` · **Fase**: 2

Nenhuma ferramenta nova de provisionamento nesta fase — sem self-service, painel, API pública de criação de tenant, billing ou planos (consistente com [D-037](#d-037--self-service-de-criação-de-tenant)). O procedimento atual (`prisma/seed.ts` editado à mão / acesso direto ao banco) permanece documentado como o caminho oficial para desenvolvimento/testes. Uma melhoria futura, se necessária, é um script administrativo interno (CLI local, não exposto como funcionalidade do produto) — não abre escopo arquitetural novo.

### D-063 — Fase 2 não exige interface mínima (opção B)
**Status**: `DECIDIDO — opção B` · **Fase**: 2 (fechado em 2026-09-09)

Analisado formalmente: `roadmap.md` define os critérios de aceite da Fase 2 inteiramente em termos de API/testes automatizados ("testes automatizados de isolamento entre tenants e de permissão por papel passando... segundo tenant de teste não consegue, em nenhuma rota, ler dado do primeiro") — nenhuma menção a UI. Nenhum caso de uso em `use-cases.md` amarra login/CRUD de usuários a uma tela específica desta fase. `requirements.md` RF-01/02/04 são satisfeitos pela existência da capacidade via API, não por uma interface.

**Decisão**: **B) Fase 2 é validada por API; a UI de login/sessão/gestão de usuários entra em fase posterior** (quando o frontend também tratar dessas telas — não necessariamente amarrado a uma fase numerada específica do roadmap atual, que é organizado por capacidade de backend). Não é uma lacuna da Fase 2, é escopo que nunca foi dela.

O único preparo já feito no frontend (`credentials: 'include'` no cliente HTTP) é forward-compatible, não antecipação de UI.

### D-060 — Auditoria básica: write-only nesta fase
**Status**: `DECIDIDO` · **Fase**: 2

BR-23/BR-24 exigem que toda criação/edição/exclusão de dado sensível gere entrada de auditoria imutável — não exigem um endpoint de leitura. A Fase 2 entrega o modelo `audit_log` (com `tenant_id`, corrigido em [entities.md](../04-database/entities.md)) e a gravação, em transação atômica com a mutação que a origina, para `users` (create/update/deactivate). Não há endpoint de consulta ainda — ler via banco. Tela/API de auditoria fica para quando houver demanda real (mais módulos gerando eventos, necessidade de investigação por usuários não-técnicos).

### D-061 — Paginação de `/users` corrigida para offset
**Status**: `DECIDIDO` · **Fase**: 2

Achado na Fase 2: `GET /users` usava paginação por **cursor**, contradizendo [D-007](#d-007--estratégia-de-paginação) (usuários estão na lista de recursos administrativos → offset) e o próprio `openapi.yaml`/`api-guidelines.md`, que já documentavam `?page=&limit=` desde a Fase 0. Corrigido para offset (`{data, page, limit, total}`); `cursor.util.ts` permanece no código para os recursos cronológicos que D-007 atribui a cursor (mensagens, interações, chamadas — ainda não implementados).

### D-062 — Validação de UUID nos DTOs deve aceitar v7, não v4
**Status**: `DECIDIDO` · **Fase**: 2

Achado na Fase 2: `CreateUserDto.role_ids` e (na primeira versão) `UpdateUserDto.role_ids` usavam `@IsUUID('4', { each: true })`, rejeitando qualquer UUID v7 — ou seja, **todo** `role_ids` enviado via API real falharia com 400, já que D-001/ADR-009 usam v7 em todo o sistema. Nunca foi detectado porque os testes existentes inseriam papéis direto no banco (bypassando a validação da API). Corrigido para `@IsUUID('7', { each: true })` nos dois DTOs; adicionado teste e2e que envia `role_ids` via API de verdade. Ao adicionar `IsUUID` em qualquer DTO novo, usar `'7'`, nunca `'4'` (ou a versão-padrão do sistema, se um dia mudar — mas hoje é v7 em tudo).

### D-064 — RF-03 (redefinição de senha): fase e fluxo indefinidos
**Status**: `VALIDAÇÃO DE NEGÓCIO` · **Prazo**: antes do primeiro cliente em produção

Achado no fechamento da Fase 2 ([phase-02.md](../09-testing/phase-acceptance/phase-02.md)) e confirmado na validação de pré-fechamento seguinte: [requirements.md](../01-product/requirements.md) RF-03 exige que o sistema permita redefinição de senha, mas nunca recebeu fase, dono ou critério de aceite no roadmap — não é `PROPOSTO` nem `ADIADO`, simplesmente nunca foi decidido. Não bloqueia nenhuma fase hoje (não é critério de aceite de nenhuma fase declarada em [roadmap.md](../10-roadmap/roadmap.md)), mas não pode ficar indefinido indefinidamente sob risco de virar dívida esquecida.

Depende de decisão de produto sobre qual(is) fluxo(s) suportar — não mutuamente exclusivos:
- **admin reseta a senha de um usuário do próprio tenant** — não depende de provedor de e-mail, poderia entrar em qualquer fase que já tenha CRUD de usuários (ou seja, já poderia ser hoje, se decidido);
- **usuário autenticado troca a própria senha** — idem, não depende de e-mail;
- **"esqueci minha senha" via e-mail** — depende de [D-040](#d-040--provedor-de-e-mailsms) (provedor de e-mail/SMS, `ADIADO` até Fase 7+).

Nenhum dos três fluxos está implementado. Este registro existe para que nenhum agente futuro decida silenciosamente qual construir ou em qual fase — a decisão é de produto, não de arquitetura.

## Decisões da Fase 3 (CRM)

### D-065 — Contacts: sub-recurso de Customer, não módulo próprio
**Status**: `DECIDIDO` · **Fase**: 3 (fechado em 2026-09-16)

`contacts` é implementado como **sub-recurso de `customers`** (`GET/POST /v1/customers/{id}/contacts`), sem módulo Nest independente (sem `modules/contacts/` próprio) nesta fase. A lógica de acesso a dados deve permanecer organizada internamente (repository próprio, ainda que dentro do módulo `customers`) para que possa ser isolada em módulo dedicado depois, caso o domínio evolua (ex.: busca de contato independente do cliente).

**Motivo**: um Contact só existe vinculado a um Customer (1:N), sempre consultado no contexto de um cliente específico — caso clássico de sub-recurso REST; evita um módulo inteiro (controller/service/repository/DTOs/module) para uma entidade simples.

### D-066 — Fundação Frontend de Auth/RBAC faz parte da Fase 3
**Status**: `DECIDIDO` · **Fase**: 3 (fechado em 2026-09-16)

A Fase 2 validou a autenticação/RBAC apenas via API ([D-063](#d-063--fase-2-não-exige-interface-mínima-opção-b)) — não existe nenhuma UI de login, sessão ou RBAC no `crm-frontend`. Como os critérios de aceite formais da Fase 3 ([roadmap.md](../10-roadmap/roadmap.md)) exigem UC-01 a UC-04 executáveis **via API e UI**, a "Fundação Frontend" de Auth/RBAC passa a ser a **primeira entrega da Fase 3 no frontend**, antes das telas de Customers/Leads/Opportunities/Pipeline.

**Escopo mínimo** (não adicionar nada além disso nesta fundação): tela de login; gerenciamento de sessão com access token em memória (nunca `localStorage`, conforme ADR-008); refresh automático via cookie httpOnly já existente, disparado em 401; `ProtectedRoute`; leitura das permissões do usuário e ocultação/desabilitação de ações conforme RBAC; logout; suporte a `POST`/`PATCH`/`DELETE` no cliente HTTP (`src/services/api.ts`), hoje limitado a `GET`.

**Não altera**: a arquitetura de autenticação do backend (ADR-008, D-004, D-005, D-006) permanece exatamente como está — esta decisão é só sobre o que falta construir no frontend para consumi-la.

**Motivo**: sem sessão autenticada na UI, nenhuma tela de CRM da Fase 3 tem onde se apoiar; tratar isso como item à parte, sem fase associada, arriscava a Fase 3 nunca satisfazer seu próprio critério de aceite formal ("via API e UI").

### D-067 — Deduplicação de Customer é bloqueante (409)
**Status**: `DECIDIDO` · **Fase**: 3 (fechado no Implementation Gate, 2026-09-16)

Ao criar um Customer cujo documento/telefone/e-mail já identifica um cliente existente no tenant (BR-07/BR-08), o sistema **não cria um duplicado automaticamente**: retorna `409` com o(s) candidato(s) encontrados. O usuário decide, pela UI, usar o cliente existente ou seguir por um fluxo explicitamente permitido pela aplicação. Quando houver **múltiplos candidatos** (ex.: telefone bate com um cliente, e-mail com outro), o sistema retorna todos — nunca escolhe automaticamente entre eles.

**Motivo**: evitar heurística automática arriscada (escolher errado é pior que pedir confirmação); mantém o dono da decisão comercial (qual cliente é "o mesmo") do lado humano.

### D-068 — Estratégia técnica de round-robin: cursor em `tenant_settings`
**Status**: `DECIDIDO` · **Fase**: 3 (fechado no Implementation Gate, 2026-09-16)

A distribuição round-robin de leads (BR-05, RF-12) usa um cursor persistido na tabela `tenant_settings` (`key = "crm.lead_round_robin.cursor"`, `value = {"last_assigned_user_id": "..."}`), com `SELECT ... FOR UPDATE` na linha correspondente dentro da mesma transação que cria/atualiza o lead — serializa concorrência entre leads simultâneos do mesmo tenant sem bloquear outros tenants. Horário de atendimento (BR-05), quando configurado, usa a mesma tabela (`key = "crm.business_hours"`); **na ausência de configuração, todos os vendedores ativos permanecem elegíveis** (fallback obrigatório — ausência de configuração nunca impede a distribuição).

**Achado nesta etapa**: `tenant_settings` está documentada em [entities.md](../04-database/entities.md) desde a Fase 0, mas **nunca foi criada** no `prisma/schema.prisma` real do `crm-backend`. A criação desta tabela entra no escopo de schema da Fase 3 (junto aos catálogos de CRM), não é reaproveitamento de infraestrutura já existente.

**Quando não houver vendedor elegível** (ver [D-069](#d-069--alerta-de-lead-não-atribuído-só-auditoria-sem-módulo-de-notificações) abaixo): o lead permanece `owner_id = null`, `status = new` — isso já representa a fila "não atribuído", sem necessidade de status/tabela adicional.

**Evolução prevista ([D-071](#d-071--disponibilidade-de-consultoratendente-para-distribuição-automática), 2026-09-21)**: a elegibilidade descrita acima (usuário ativo + tenant + permissão `leads:update`) passa a incluir **disponibilidade** — ativo + disponível + permissão — quando a modelagem de disponibilidade for validada. Até lá o comportamento implementado na Fase 3.4 não filtra por disponibilidade.

### D-069 — Alerta de lead não atribuído: só auditoria, sem módulo de notificações
**Status**: `DECIDIDO` · **Fase**: 3 (fechado no Implementation Gate, 2026-09-16)

Quando o round-robin (D-068) não encontra nenhum vendedor elegível, a Fase 3 registra o evento apenas via `AuditModule` (ação `lead.unassigned`) — não grava na tabela `notifications`, não cria módulo/endpoint/UI de notificações, não cria fila dedicada para isso. A tabela `notifications` (já modelada desde a Fase 0) só passa a ser escrita/lida a partir da "primeira versão de Notificações" da [Fase 4](../10-roadmap/roadmap.md).

**Motivo**: evitar antecipar o módulo de Notificações (explicitamente Fase 4 no roadmap) só por causa de um único gatilho da Fase 3; o registro de auditoria já é suficiente para rastreabilidade/investigação até lá.

## Ajuste de escopo de produto (2026-09-21)

Ajuste solicitado pelo responsável pelo produto **após** a implementação das Fases 3.1–3.5. É uma correção de definição de produto e de terminologia — **não altera código, schema, migrations nem decisões anteriores fechadas** (D-031 a D-069).

### D-070 — Definição de produto: CRM Comercial + Atendimento/Conversas + WhatsApp (sem Call Center telefônico)
**Status**: `DECIDIDO` · **Fase**: transversal (ajuste de escopo, 2026-09-21)

O produto é **CRM Comercial + Atendimento/Conversas + WhatsApp + futuro Omnichannel**. "Atendimento" significa conversas/interações comerciais, principalmente via WhatsApp, e as funções relacionadas a Lead/Cliente.

O produto **não é** um Call Center telefônico tradicional. Ficam **fora de escopo**: URA, telefonia PSTN, gravação de chamadas, infraestrutura de telefonia e filas de chamadas telefônicas.

**Consequências**:
- **Roadmap** (significado funcional, sem renumerar fases): Fase 3 = CRM Comercial; Fase 4 = Atendimento/Conversas; Fase 5 = WhatsApp/Conversas; Fase 6 = Omnichannel. Fases 7–10 preservadas. Ver [roadmap.md](../10-roadmap/roadmap.md).
- **Regras de negócio**: BR-14, BR-15, BR-16 e BR-18 reescritas para atendimento/conversas e disponibilidade; **BR-17 (gravação de chamada) removida sem regra substituta**; BR-19 a BR-21 (Conversas/WhatsApp) preservadas. Ver [business-rules.md](../02-business/business-rules.md).
- **Decisões anteriores afetadas** (sem reabrir o mérito): D-010 (provedor de telefonia) e D-045 (discador preditivo) ficam **sem fase e fora do escopo**; D-011 (provedor de WhatsApp) passa a ser pré-requisito da Fase 5; D-013, D-024 e D-039 seguem na Fase 5, agora referidas a WhatsApp/atendimento.
- **Modelo de dados**: o grupo "Call Center" de [entities.md](../04-database/entities.md) e [relationships.md](../04-database/relationships.md) passa a ser tratado como **legado a revisar antes da implementação**. `calls`, `recording_url` e `queues.channel_type = voice` são específicos de telefonia e **não serão implementados**. `queues`, `queue_members`, `dispositions` e `agent_status_log` permanecem como conceitos reaproveitáveis, sujeitos à modelagem definida em D-071. Nada disso existe no `schema.prisma` — nenhuma migration é criada por esta decisão.
- **Não altera**: código já implementado (Fases 3.1–3.5), Round Robin (D-068) e alerta de lead não atribuído (D-069).

**Pendências de negócio registradas (não inventadas — decidir antes da fase que as implementa)**:
1. BR-15: o que caracteriza uma Conversa/atendimento "finalizado" e se toda conversa exige disposição.
2. BR-16: limite de pausa configurável (valor e onde se configura) e destinatário do alerta — depende da primeira versão de Notificações (Fase 4).
3. BR-18: pontos de medição do SLA de uma Conversa e nível de configuração (fila, canal ou tenant).
4. Se "filas" de atendimento existem já na Fase 4 ou só na Fase 5.
5. Terminologia dos papéis de fábrica/personas "Supervisor (Call Center)" e "Operador de Call Center" (renomear papéis exige mudança de seed — fora deste ajuste).

### D-071 — Disponibilidade de consultor/atendente para distribuição automática
**Status**: regra `DECIDIDO` · modelagem `VALIDAÇÃO DE NEGÓCIO` · **Prazo**: antes de implementar disponibilidade (Fase 4). Não bloqueia a Fase 3 (Notes/Tasks/Appointments não dependem dela).

**Regra decidida (2026-09-21)**: a distribuição automática de novos Leads/atendimentos só considera consultores/atendentes **ativos e disponíveis**. Usuário ativo porém **indisponível não integra o conjunto elegível** do Round Robin. A disponibilidade é um estado comercial/de atendimento do usuário — **não é "Call Center"**, **não é atrelada a um papel específico** e é reutilizável por: distribuição de leads, distribuição de conversas de WhatsApp, filas de atendimento e outros canais do Omnichannel. Ver BR-14 e BR-05.

**Divergência com a Fase 3.4 (registrada, não corrigida agora)**: o Round Robin implementado (D-068) considera **usuário ativo + mesmo tenant + permissão `leads:update`** (`UsersService.listActiveIdsWithPermission`). **Não considera disponibilidade.** Evolução desejada: **ativo + disponível + permissão** — a elegibilidade continua por permissão, não por papel. Enquanto a modelagem não for validada, o comportamento atual permanece; quando todos os elegíveis estiverem indisponíveis, vale o que D-068/D-069 já definem para "nenhum elegível" (lead fica `owner_id = null`, `status = new`, evento `lead.unassigned` na auditoria).

**Conceito já existente na especificação (reaproveitar, não recriar)**: `agent_status_log` em [entities.md](../04-database/entities.md) (`user_id`, `status` enum `available | busy | paused | offline`, `started_at`, `ended_at`), RF-15 (usuário altera seu status), BR-14/BR-16, `AgentStatus` e o evento `agent.status_changed` em [architecture.md](../03-architecture/architecture.md). Hoje esse conceito está descrito como parte do "Call Center" e não existe no `schema.prisma`.

**Lacuna de modelagem — pendências de negócio (não decididas; nenhum enum, campo ou migration foi escolhido)**:
1. **Estado atual**: `agent_status_log` é só histórico — não há campo de "status corrente". Representar o estado atual como campo do usuário, derivá-lo da última linha aberta do log ou usar outra estrutura?
2. **Conjunto de estados**: os quatro estados atuais servem para conversas? Quais contam como "disponível" para a distribuição (`busy` e `offline` são elegíveis)? Qual a relação com login/logout e sessão?
3. **Quem altera**: o próprio usuário, gestor/supervisor, transições automáticas (login, logout, inatividade)?
4. **Escopo**: disponibilidade única por usuário ou por fila/canal?
5. **Relação com `crm.business_hours`** (BR-05, formato ainda indefinido): soma-se ao horário de atendimento ou o substitui?
6. **Fallback**: se o tenant não usar disponibilidade, todos os ativos continuam elegíveis (como hoje)?
7. **Leads já atribuídos** a quem fica indisponível: permanecem com o dono (assumido por padrão, hoje) ou há redistribuição?
8. **Nomenclatura neutra**: `agent_status_log`/`AgentStatus` carregam o vocabulário de Call Center; renomear?

## Regras de negócio validadas pelo responsável pelo produto (Fase 3)

Estas decisões **não devem ser inventadas por nenhum agente** — foram validadas diretamente com o responsável pelo produto em 2026-09-16, no fechamento do Decision Gate da Fase 3. Os documentos correspondentes deixam de carregar `[VALIDAÇÃO DE NEGÓCIO NECESSÁRIA]` e passam a refletir a regra decidida abaixo.

### D-032 — Ordem de movimentação entre etapas do pipeline
**Status**: `DECIDIDO` · **Fase**: 3 (fechado em 2026-09-16)

A oportunidade pode ser movimentada **livremente** entre as etapas do pipeline, inclusive pulando uma ou mais etapas. Quando o usuário pular etapa(s), uma **justificativa é obrigatória** e fica registrada junto ao histórico de movimentação.

**Toda movimentação registra** (BR-10): oportunidade, etapa anterior, etapa nova, usuário responsável, data/hora, e a justificativa quando houver salto de etapa.

**Motivo**: preservar a flexibilidade comercial do processo de vendas (inclusive vendas de consórcio) sem perder rastreabilidade para análise de conversão e auditoria comercial futura (Fase 4+). O pipeline não se torna um fluxo rigidamente sequencial.

**Impacto em código**: DTO de `POST /opportunities/{id}/move` ganha campo opcional `justification`/`justificativa`; regra de obrigatoriedade condicional (exigir quando `to_stage.order` não é imediatamente adjacente a `from_stage.order`) é validada no Service, não no banco.

### D-033 — Reabertura de lead desqualificado (BR-06)
**Status**: `DECIDIDO` · **Fase**: 3 (fechado em 2026-09-16)

Quando um lead desqualificado retorna, o sistema **reabre o lead existente** — não cria automaticamente um novo lead para a mesma pessoa/contato. O histórico anterior (incluindo o motivo da desqualificação anterior) permanece preservado, nunca é apagado. A reabertura registra usuário, data/hora e a alteração de status.

**Motivo**: preservar a história comercial do cliente/contato e permitir, no futuro, analisar quantas tentativas foram feitas antes da conversão (auditoria comercial, Fase 4+).

### D-034 — Obrigatoriedade de valor em oportunidade (BR-13)
**Status**: `DECIDIDO` · **Fase**: 3 (fechado em 2026-09-16)

O valor (`value`) da oportunidade **não é obrigatório na criação** — a oportunidade pode ser criada sem valor. O valor **se torna obrigatório a partir de uma etapa comercial configurável do pipeline** (não um nome fixo de etapa como "Proposta" ou "Fechamento" — os pipelines/stages são customizáveis por tenant, então a regra não pode depender de nome).

**Consequência técnica registrada e fechada no Implementation Gate (2026-09-16)**: a documentação já tinha identificado que faltava uma propriedade para representar essa regra — modelada como campo booleano `requires_value` na entidade `stages` (ver [entities.md](../04-database/entities.md) seção "CRM Core"). A regra final adotada para esta implementação é **por etapa individual, sem propagação por `order`**: o valor só é obrigatório quando a oportunidade está exatamente numa etapa com `requires_value = true` — etapas anteriores ou posteriores não marcadas não herdam a obrigatoriedade, mesmo que uma etapa anterior no fluxo esteja marcada. Uma regra de "a partir de uma etapa" com propagação por ordem foi cogitada, mas **não é implementada nesta fase** — fica registrada como evolução técnica futura, a avaliar apenas se a regra por etapa individual se mostrar insuficiente na prática.

**Motivo**: no contexto comercial (ex.: consórcio), a consultora frequentemente não sabe o valor final logo no primeiro contato — exigir valor cedo demais atrapalha o cadastro do lead/oportunidade. Por outro lado, oportunidades maduras precisam ter valor para permitir análise de quanto está "em jogo" em cada etapa do funil.

### D-035 — Regra de aprovação para exclusão por vendedor
**Status**: `DECIDIDO` · **Fase**: 3 (fechado em 2026-09-16)

Vendedor/Consultora **não pode excluir** registros de negócio (Leads, Clientes, Oportunidades) livremente. A exclusão desses registros fica restrita a perfis de gestão/administração (Gerente/Admin), conforme a matriz de permissões ([personas.md](../01-product/personas.md) §3). Não há fluxo de solicitação/aprovação nesta fase — o vendedor simplesmente não tem a permissão de exclusão.

Toda exclusão continua sendo **soft delete** (BR-22) e continua sendo auditada (BR-23/24); exclusão física nunca é exposta via API.

**Motivo**: reduzir o risco de leads/oportunidades mal trabalhados "sumirem" do funil sem visibilidade do gerente, mantendo a autonomia de criação/edição do vendedor sobre seus próprios registros.

---

## Histórico de revisões

| Data | Alteração |
|---|---|
| 2026-09-08 | Criação do registro; consolidação e classificação das ~55 ocorrências de `[DECISÃO PENDENTE]` da Fase 0. Nenhum bloqueador remanescente para a Fase 1. |
| 2026-09-08 | Validação final da Fase 0. D-036 ampliada com a decisão provisória explícita (sem acesso automático) e a evolução futura "Support Access Controlado". Corrigidas 3 inconsistências detectadas na auditoria: restrição do Super Admin em `personas.md`, réplica de leitura em `scalability.md` §3, e marcação de fase em `requirements.md` (Relatórios/Dashboard e Notificações). |
| 2026-09-16 | Decision Gate da Fase 3 (CRM) fechado com o responsável pelo produto. D-031 (`PROPOSTO`→`DECIDIDO`), D-032, D-033, D-034, D-035 (`VALIDAÇÃO DE NEGÓCIO`→`DECIDIDO`) e D-058 (reafirmado para a Fase 3: escopo permanece Tenant-only) resolvidos. Duas decisões novas registradas: D-065 (Contacts como sub-recurso de Customer) e D-066 (Fundação Frontend de Auth/RBAC como primeira entrega da Fase 3). Consistência documental atualizada em `entities.md`, `relationships.md`, `business-rules.md`, `personas.md`, `use-cases.md`, `workflows.md`, `roadmap.md`, `api-guidelines.md` e `openapi.yaml`. |
| 2026-09-16 | Implementation Gate da Fase 3 fechado — última validação antes da implementação, sem reabrir nenhuma decisão anterior. D-034 teve sua consequência técnica precisada: `stages.requires_value` é regra **por etapa individual, sem propagação por `order`** (removida a leitura anterior de "etapa igual ou posterior"). Três decisões técnicas novas registradas: D-067 (deduplicação de Customer é bloqueante, `409` com candidatos, sem escolha automática), D-068 (round-robin usa cursor em `tenant_settings` com lock transacional; achado que essa tabela nunca foi criada no `crm-backend` real, apesar de documentada desde a Fase 0 — criação entra no escopo de schema da Fase 3) e D-069 (lead não atribuído gera só evento de auditoria, sem usar a tabela `notifications` nem antecipar o módulo de Notificações da Fase 4). Consistência documental atualizada em `entities.md` e `business-rules.md`. |
| 2026-09-21 | Ajuste de escopo de produto (documentação apenas, sem alteração de código/schema). D-070 (`DECIDIDO`): o produto é CRM Comercial + Atendimento/Conversas + WhatsApp + futuro Omnichannel — **não** um Call Center telefônico (sem URA, PSTN, gravação de chamadas, infraestrutura de telefonia nem filas de chamadas). D-071: regra de disponibilidade `DECIDIDO` (distribuição automática só para consultor/atendente ativo **e** disponível); modelagem `VALIDAÇÃO DE NEGÓCIO` (reaproveita o conceito `agent_status_log`/RF-15; lacunas registradas); divergência com o Round Robin da Fase 3.4 (ativo + permissão, sem disponibilidade) documentada. D-010 e D-045 ficam sem fase/fora de escopo; D-011 passa a ser pré-requisito da Fase 5 (WhatsApp/Conversas). BR-14/15/16/18 reescritas, BR-17 removida, BR-19–21 preservadas. Roadmap: Fase 3 CRM Comercial, Fase 4 Atendimento/Conversas, Fase 5 WhatsApp/Conversas, Fase 6 Omnichannel. |
