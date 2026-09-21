# CLAUDE.md — crm-spec

Instruções para agentes de IA trabalhando **neste repositório** (documentação). Para trabalhar em `crm-backend` ou `crm-frontend`, ver [agents/claude-backend.md](agents/claude-backend.md) e [agents/codex-frontend.md](agents/codex-frontend.md).

## Regra número 1

Antes de qualquer coisa, leia o **[Decision Register](docs/00-governance/decision-register.md)**. Ele é a fonte de verdade sobre o que está decidido, adiado ou pendente de stakeholder. Nunca rediscuta uma decisão `DECIDIDO` sem um motivo novo, nunca antecipe uma `ADIADO`, nunca invente uma `VALIDAÇÃO DE NEGÓCIO`.

## Como classificar uma decisão

| Status | Quando usar | Bloqueia? |
|---|---|---|
| `DECIDIDO` | Definitivo para a fase atual | Não |
| `PROPOSTO` | Direção definida, refinável depois | Não |
| `ADIADO` | Não precisa ser decidido agora | Não |
| `VALIDAÇÃO DE NEGÓCIO` | Depende de stakeholder humano | Só na fase que depende |
| `BLOQUEADOR` | Impede a fase correspondente | Sim, naquela fase |

Ao adiar, registre sempre: **quando** decidir, **qual fase** depende, e **por que** não bloqueia a fase atual.

Ao mudar uma decisão: atualize a entrada no register, atualize os documentos que a citam e, se for arquitetural, crie um ADR novo (nunca edite silenciosamente um ADR aceito).

## Estado atual

**FASE 0 — APROVADA. FASE 1 — APROVADA. FASE 2 — fechada em 2026-09-09, veredito 🟡 APTA COM RESSALVAS (ver [phase-02.md](docs/09-testing/phase-acceptance/phase-02.md)). FASE 3 aguarda autorização explícita.**

---

## Fechamento formal da Fase 2 (2026-09-09)

Relatório completo — matriz de auditoria spec↔código↔teste, divergências, decisões, MATs,
resultado dos testes, veredito — em
**[docs/09-testing/phase-acceptance/phase-02.md](docs/09-testing/phase-acceptance/phase-02.md)**.
Não duplicado aqui. Resumo do que mudou neste repositório:

- Nova camada de teste: **Manual Acceptance Test (MAT)** — `docs/09-testing/{manual-acceptance,phase-acceptance,evidence}/`. 8 MATs de Fase 2 + 1 template reutilizável (`MAT-SEC-TENANT-001`), todos executados de verdade contra o backend real, evidência embutida.
- D-003 (RLS) fechada: **não implementar no MVP** — análise completa no Decision Register, com risco técnico específico do Prisma (pool de conexões) documentado.
- D-063 (nova): Fase 2 não exige UI — validada por API.
- D-056 a D-062: correções de segurança e paginação da Fase 2 (ver `crm-backend/CLAUDE.md` para o histórico técnico).
- `requirements.md` RF-03/RF-07 marcados com a divergência encontrada (sem implementação, sem fase declarada) — não inventado, não corrigido silenciosamente.
- `personas.md` §4 ganhou a fronteira explícita Fase 2 (RBAC só tenant) vs. Fase 3+ (equipe/filial).

**Pendência aberta, sem dono ainda**: decidir em que fase entra a redefinição de senha (RF-03) — ver `phase-02.md` seção 15.

---

## Fechamento operacional da Fase 1 (2026-09-09)

### Repositórios e commits

| Repositório | Commit | Visibilidade | CI remoto |
|---|---|---|---|
| [crm-backend](https://github.com/Ryangsl/crm-backend) | `611cd4f` | privado | ✅ sucesso — install, prisma generate, lint, test, build |
| [crm-frontend](https://github.com/Ryangsl/crm-frontend) | `be436d3` | público | ✅ sucesso — install, lint, test, build |
| [crm-workspace](https://github.com/Ryangsl/crm-workspace) | `7976937` | privado | (sem CI — repositório de infraestrutura) |
| [crm-spec](https://github.com/Ryangsl/crm-spec) | `8b0f564` | público | (sem CI — documentação) |

O CI remoto rodou automaticamente no push e **passou em todos os passos** nos dois repositórios de código, resolvendo a única ressalva aberta no aceite da Fase 1.

### D-054 — resolvida

Criado o repositório **`crm-workspace`**: a pasta que agrupa os três repositórios passou a ser versionada, com `crm-backend/`, `crm-frontend/` e `crm-spec/` no `.gitignore`. Guarda `docker-compose.yml`, `scripts/setup.sh`, `scripts/test-all.sh`, `.env.example` e a documentação de setup integrado. Backend e frontend **não** foram fundidos. Detalhes e alternativas descartadas em [D-054](docs/00-governance/decision-register.md#d-054--versionamento-do-workspace).

### Situação das decisões

55 decisões: 21 `DECIDIDO`, 15 `ADIADO`, 11 `PROPOSTO`, 8 `VALIDAÇÃO DE NEGÓCIO`, **0 `BLOQUEADOR`**.

### Pendências transferidas para fases futuras

| Pendência | Para quando |
|---|---|
| Revisão formal de `auth`, `tenants` e `users` (construídos antes da hora) | Início da Fase 2 — não presumir prontos |
| RLS como segunda camada de isolamento ([D-003](docs/00-governance/decision-register.md#d-003--postgresql-row-level-security)) | Até o fim da Fase 2 |
| Testes de integração/e2e no CI (exigem Postgres e Redis nos runners) | Fase 2, junto do primeiro fluxo real |
| E2E de frontend com Playwright ([D-020](docs/00-governance/decision-register.md#d-020--ferramenta-de-e2e-de-frontend)) | Fase 2, quando existirem fluxos a cobrir |
| Provedor de telefonia ([D-010](docs/00-governance/decision-register.md#d-010--provedor-de-telefonia)) | Sem fase — telefonia está fora de escopo ([D-070](docs/00-governance/decision-register.md#d-070--definição-de-produto-crm-comercial--atendimentoconversas--whatsapp-sem-call-center-telefônico)) |
| Provedor de WhatsApp ([D-011](docs/00-governance/decision-register.md#d-011--provedor-de-whatsapp)) | Antes da Fase 5 (WhatsApp/Conversas) |
| Paleta de marca ([D-043](docs/00-governance/decision-register.md#d-043--paleta-de-marca)) e fluxo LGPD ([D-047](docs/00-governance/decision-register.md#d-047--fluxo-operacional-de-lgpd-titular-de-dados)) | Antes do primeiro cliente em produção |

### Observação sobre histórico

O código da Fase 1 foi commitado pelo dono do projeto em um único commit por repositório (`commit`), antes deste fechamento. Como já estava publicado, o histórico **não** foi reescrito — reescrever histórico compartilhado é destrutivo. Commits semânticos valem daqui em diante.

---

## Fase 1 — Fundação técnica (2026-09-08)

Backend e frontend com esqueleto executável, validados contra Postgres e Redis reais.

**Entregue**: `crm-frontend` criado do zero (React 19, Vite, Tailwind 4, PWA, Mobile First,
design system base, Context API, TanStack Query); no `crm-backend`, infraestrutura já existente
verificada e lacunas fechadas; `docker-compose.yml` de workspace com dois modos (D-053); CI em
cada repositório (D-052).

**Correções de aderência à spec** (o backend pré-existente violava decisões aprovadas):
- **UUID v7** (D-001/ADR-009): gerava v4. Verificado que Prisma 5.22 não suporta `uuid(7)` e
  Postgres 16 não tem `uuidv7()` → Prisma atualizado para 6.19.3 com `@default(uuid(7))`.
  Confirmado no banco real: 15 ids, 0 fora do padrão. Ver [D-051](docs/00-governance/decision-register.md#d-051--prisma-6-e-mecanismo-de-geração-de-uuid-v7).
- **Refresh token TTL** (D-004/ADR-008): era 30 dias, corrigido para 7.

**Fronteira de fase**: `auth`, `tenants` e `users` já existiam no backend, escopo que pertence
à Fase 2. Por decisão do dono do projeto foram mantidos, mas serão **formalmente revisados**
quando a Fase 2 abrir — não são entrega da Fase 1.

**Decisões novas registradas**: D-051 a D-055.

---

## Validação final da Fase 0 (2026-09-08)

**Status oficial: `APROVADA`.**

Verificações automatizadas, todas passando:

| Verificação | Resultado |
|---|---|
| Artefatos obrigatórios (visão, personas, requisitos, casos de uso, arquitetura, dados, API, roadmap, MVP, register) | 13/13 presentes |
| OpenAPI | YAML válido, 16 paths, 12 schemas, 0 `$ref` quebrada |
| Links internos | 101 referências `D-xxx` válidas, 0 âncora quebrada, 0 link de arquivo quebrado |
| Referências a ADR | 0 apontando para ADR inexistente (ADR-001 a ADR-009, todos "Aceito") |
| Decision Register | 50 decisões: 17 `DECIDIDO`, 15 `ADIADO`, 10 `PROPOSTO`, 8 `VALIDAÇÃO DE NEGÓCIO`, **0 `BLOQUEADOR`** |
| Decisões não-`DECIDIDO` sem prazo/fase | 0 |
| `[DECISÃO PENDENTE]` sem classificação | 0 |
| Fases com objetivo/funcionalidades/dependências/critérios/riscos | 11/11 |
| Fronteira do MVP (telefonia, WhatsApp, WebSocket, discador preditivo, microsserviços) | nenhuma inclusão indevida |

### Correções aplicadas na validação
1. **`personas.md`** — a linha "Restrições" do Super Admin dizia "sem acesso... *sem trilha de auditoria explícita*", o que implicava acesso permitido mediante auditoria e contradizia D-036. Reescrita: nenhum acesso existe hoje, por nenhum caminho.
2. **`scalability.md` §3** — apresentava réplica de leitura como cobertura do crescimento inicial, enquanto §8, D-014 e a Fase 9 a tratam como adiada. Reescrita para escalabilidade vertical primeiro, réplica na Fase 9.
3. **`requirements.md`** — seções "Relatórios e Dashboard" (Fase 7) e "Notificações" (Fase 4/8) não tinham marcação de fase, ao contrário de Call Center e Omnichannel. Marcadas.
4. **D-036 ampliada** — decisão provisória explícita (sem acesso automático a dados de tenant) e evolução futura registrada como "Support Access Controlado": motivo obrigatório, acesso temporário, auditoria, expiração automática, preferência por read-only. Exige ADR próprio se for implementada. Status mantido em `VALIDAÇÃO DE NEGÓCIO`.

### Observações não bloqueantes
- FASE 10 usa "Funcionalidades **candidatas**" e "Critérios de aceite: a definir" — adequado para uma fase cujo escopo é `ADIADO` (D-048), mas é a única fase sem critério de aceite fechado.
- D-007 (paginação híbrida) é a decisão técnica transversal mais relevante sem ADR próprio; a justificativa está no register e cabe dentro de ADR-005. Promover a ADR é opcional.

---

## Resumo da consolidação de decisões (2026-09-08)

Revisão das ~55 ocorrências de `[DECISÃO PENDENTE]` deixadas pela Fase 0. Todas foram classificadas; nenhuma foi apagada sem registro. O que mudou:

### Criado
- **[docs/00-governance/decision-register.md](docs/00-governance/decision-register.md)** — registro central com 50 decisões (D-001 a D-050), status, fase que depende de cada uma, e a tabela de portões por fase.
- **[ADR-008](docs/adr/ADR-008.md)** — autenticação: access token JWT de 15 min em memória, refresh token de 7 dias em cookie httpOnly com rotação e detecção de reuso.
- **[ADR-009](docs/adr/ADR-009.md)** — UUID v7 como identificador primário.

### Decisões consolidadas (antes pendentes, agora `DECIDIDO`)
- UUID v7 (D-001); multi-tenancy por `tenant_id` derivado do contexto autenticado, nunca do frontend (D-002).
- JWT 15 min / refresh 7 dias em cookie httpOnly (D-004, D-005).
- Paginação **híbrida**: offset para recursos administrativos, cursor para cronológicos (D-007).
- Campos personalizados via `JSONB`, sem engine de customização no MVP (D-008, D-009).
- Escopo de dados por atribuição estática usuário→equipe→filial (D-016).
- `class-validator` no backend, Context API no frontend, Playwright para E2E, trunk-based com `main`, app fora de container em dev (D-017, D-018, D-020, D-022, D-023).
- PWA offline apenas para leitura/assets (D-041); sem self-service de tenant no MVP (D-037).

### Decisões adiadas (com prazo e fase explícitos)
- Provedor de telefonia → sem fase, fora de escopo (D-010/D-070). WhatsApp → antes da Fase 5 (WhatsApp/Conversas), direção já fixada em API oficial/BSP (D-011).
- WebSocket → Fase 5 (D-013). Circuit breaker, secrets, registry, teste de carga, IA, app nativo, discador preditivo → suas respectivas fases.
- Escalabilidade avançada (K8s, microsserviços, réplicas, particionamento) → só com evidência real (D-014).

### Aguardando stakeholders (`VALIDAÇÃO DE NEGÓCIO`)
D-032 (ordem de etapas do pipeline), D-033 (reabertura de lead), D-034 (obrigatoriedade de valor), D-035 (aprovação de exclusão) — todas antes da Fase 3. D-028 (retenção de backup), D-043 (paleta de marca), D-047 (fluxo LGPD), D-036 (acesso de suporte) — antes de produção/painel de plataforma.

### Contradições corrigidas
- **Click-to-call saiu do MVP.** Estava como "stretch goal" em `mvp.md` enquanto o resto da documentação tratava telefonia como Fase 5. O MVP agora tem apenas registro manual de atendimento, sem nenhum provedor externo.
- **Contrato de API alinhado ao cookie httpOnly**: `openapi.yaml` não devolve mais `refresh_token` no corpo do login; `/auth/refresh` lê do cookie. Schema `TokenPair` virou `AccessToken`.
- **Paginação alinhada**: `users`, `customers` e `opportunities` passaram de cursor para offset no `openapi.yaml`; `interactions` seguiu com cursor. Parâmetro `Page` adicionado.
- **WebSocket removido da Fase 1** em `backend-architecture.md`, `frontend-architecture.md` e `architecture.md` — era descrito como "parcial no MVP".
- **Fases marcadas** em casos de uso (UC-05 a UC-08), workflows e requisitos (RF-15 a RF-21), que antes não distinguiam MVP de fases futuras.
- Referência quebrada a "[ADR pendente sobre discador]" em `workflows.md` substituída pela decisão real.

### Regra de bloqueio adotada
> Nenhuma decisão pendente bloqueia uma fase quando não impacta diretamente seus critérios de aceite ou a arquitetura necessária para ela.

Aplicada em [docs/10-roadmap/roadmap.md](docs/10-roadmap/roadmap.md) (tabela de portões por fase) e em [agents/reviewer.md](agents/reviewer.md) (bloquear PR por decisão de outra fase é erro de revisão).
