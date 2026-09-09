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
| Fase 2 — Auth/Usuários/Tenants | D-002, D-004, D-005, D-016, D-037 (`DECIDIDO`); D-003, D-006 (`PROPOSTO`, resolver até o fim da fase) |
| Fase 3 — CRM | D-007, D-008 (`DECIDIDO`); D-031 (`PROPOSTO`); D-032, D-033, D-034, D-035 (`VALIDAÇÃO DE NEGÓCIO`) |
| Fase 5 — Call Center | D-010, D-013, D-024, D-025, D-039 |
| Fase 6 — Omnichannel | D-011 |
| Fase 7+ | D-038, D-040, D-046, D-049 |
| Antes do primeiro cliente em produção | D-027, D-028, D-029, D-043, D-047 |

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
**Status**: `PROPOSTO` · **Prazo**: antes da conclusão da Fase 2

Avaliar RLS como **camada adicional** de defesa. O isolamento primário continua sendo responsabilidade da aplicação (Tenant Context, Guards, Services, filtro obrigatório no Repository).

**Regra**: RLS não substitui os testes automatizados de isolamento cross-tenant, que permanecem obrigatórios independentemente da adoção.

### D-004 — Estratégia de JWT
**Status**: `DECIDIDO` · **Fase**: 2 · **ADR**: [ADR-008](../adr/ADR-008.md)

- Access token: TTL de **15 minutos**.
- Refresh token: TTL de **7 dias**, com **rotação** a cada uso e possibilidade de **invalidação** (revogação individual e global).

### D-005 — Armazenamento do refresh token
**Status**: `DECIDIDO` · **Fase**: 2 · **ADR**: [ADR-008](../adr/ADR-008.md)

Cookie **httpOnly**, `Secure: true` em produção. O access token não é persistido permanentemente no navegador (mantido em memória da aplicação).

### D-006 — Topologia de domínio, SameSite e CSRF
**Status**: `PROPOSTO` · **Prazo**: antes da conclusão da Fase 2

O valor de `SameSite` do cookie de refresh depende da arquitetura final de domínio (frontend e API no mesmo site vs. cross-site). Se o deploy for cross-site, proteção CSRF (token anti-CSRF além de `SameSite`) passa a ser **obrigatória**. Decidir junto com a definição de domínios em [../08-devops/deployment.md](../08-devops/deployment.md).

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
**Status**: `PROPOSTO` · **Prazo**: antes da Fase 3

Manter `entity_type` + `entity_id` com integridade validada na aplicação. Revisar antes da Fase 3 se a ausência de FK nativa se mostrar um problema real de integridade.

### D-030 — Política de deprecação de versão de API
**Status**: `ADIADO` · **Prazo**: antes da primeira mudança incompatível (`/v2`)

Não há consumidor externo nem segunda versão no horizonte; definir o tempo mínimo de convivência entre versões quando houver necessidade concreta.

---

## Comunicação e provedores externos

### D-010 — Provedor de telefonia
**Status**: `ADIADO` · **Prazo**: antes da Fase 5

Não bloqueia as Fases 1, 2, 3 e 4. A arquitetura precisa apenas garantir a camada de abstração (`TelephonyAdapter` / `ChannelAdapter`), com implementações futuras plugáveis. Não escolher nem integrar provedor antes da Fase 5 sem necessidade de negócio validada.

### D-011 — Provedor de WhatsApp
**Status**: `ADIADO` · **Prazo**: antes da Fase 6

Direção definida: **WhatsApp Business Platform oficial ou BSP oficial** para o produto SaaS comercial. Soluções não oficiais não podem ser a base do produto principal. Abstração: `ChannelAdapter` com `sendMessage()`, `receiveWebhook()`, `sendTemplate()`, `getMedia()`.

### D-040 — Provedor de e-mail/SMS
**Status**: `ADIADO` · **Prazo**: quando esses canais entrarem no roadmap (pós-Fase 6)

### D-039 — Circuit breaker para provedores externos
**Status**: `ADIADO` · **Prazo**: Fase 5 (primeira integração externa real)

Timeout curto já é exigido desde a primeira integração; a biblioteca/abordagem de circuit breaker se decide com um provedor real em mãos.

### D-024 — Convenção de variáveis de ambiente de provedores
**Status**: `PROPOSTO` · **Prazo**: Fase 5

Prefixo por **capacidade**, não por marca do provedor (`TELEPHONY_*`, `WHATSAPP_*`), para que a troca de provedor não exija renomear configuração. Consistente com a abstração de canal.

### D-045 — Discador preditivo
**Status**: `ADIADO` · **Prazo**: pós-Fase 5, mediante validação de negócio

Exige motor de pacing e tratamento de requisitos legais de abandono de chamada. MVP de telefonia é discagem manual/click-to-call.

---

## Infraestrutura, tempo real e escalabilidade

### D-012 — Redis + BullMQ
**Status**: `DECIDIDO` · **Fase**: 1 (infraestrutura disponível) · **ADR**: [ADR-006](../adr/ADR-006.md)

Redis como infraestrutura compartilhada (cache quando necessário, filas, escalabilidade futura de eventos/WebSocket). BullMQ como solução padrão de filas.

**Regra**: não criar filas desnecessárias no MVP. A operação permanece síncrona enquanto não houver necessidade real de processamento assíncrono.

### D-013 — WebSocket
**Status**: `ADIADO` · **Prazo**: Fase 5

Necessário para status de operadores, filas, supervisão em tempo real e eventos de Call Center. Não antecipar implementação de WebSocket na Fase 1.

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

## Regras de negócio aguardando stakeholders

Estas decisões **não** devem ser inventadas por nenhum agente. Enquanto não validadas, os documentos correspondentes carregam `[VALIDAÇÃO DE NEGÓCIO NECESSÁRIA]`.

### D-032 — Ordem de movimentação entre etapas do pipeline
**Status**: `VALIDAÇÃO DE NEGÓCIO` · **Prazo**: antes da Fase 3

Mover uma oportunidade para uma etapa fora da ordem é livre, bloqueado, ou permitido com justificativa? Depende da política comercial do cliente-alvo.

### D-033 — Reabertura de lead desqualificado (BR-06)
**Status**: `VALIDAÇÃO DE NEGÓCIO` · **Prazo**: antes da Fase 3

Contato que retorna gera um lead novo, ou reabre o anterior?

### D-034 — Obrigatoriedade de valor em oportunidade (BR-13)
**Status**: `VALIDAÇÃO DE NEGÓCIO` · **Prazo**: antes da Fase 3

Valor monetário é sempre obrigatório, opcional, ou configurável por pipeline?

### D-035 — Regra de aprovação para exclusão por vendedor
**Status**: `VALIDAÇÃO DE NEGÓCIO` · **Prazo**: antes da Fase 3

Vendedor pode excluir (soft delete) os próprios registros livremente ou exige aprovação de gerente?

---

## Histórico de revisões

| Data | Alteração |
|---|---|
| 2026-09-08 | Criação do registro; consolidação e classificação das ~55 ocorrências de `[DECISÃO PENDENTE]` da Fase 0. Nenhum bloqueador remanescente para a Fase 1. |
| 2026-09-08 | Validação final da Fase 0. D-036 ampliada com a decisão provisória explícita (sem acesso automático) e a evolução futura "Support Access Controlado". Corrigidas 3 inconsistências detectadas na auditoria: restrição do Super Admin em `personas.md`, réplica de leitura em `scalability.md` §3, e marcação de fase em `requirements.md` (Relatórios/Dashboard e Notificações). |
