# Fase 2 — Autenticação + Usuários + Tenants

**Data do fechamento**: 2026-09-09 · **Executado por**: Claude (Sonnet 5)

Este documento é o relatório formal de fechamento. Segue a estrutura pedida na revisão de
encerramento da fase — comparando spec ↔ roadmap ↔ ADRs ↔ Decision Register ↔ backend ↔
frontend ↔ OpenAPI ↔ testes automatizados ↔ MAT.

---

## 1. Resumo executivo

A Fase 2 entrega autenticação (login/refresh/logout/logout-all), CRUD completo de usuários,
papéis de fábrica, isolamento de tenant e auditoria básica — com três divergências de
segurança contra decisão já aprovada (D1/D2/D3) corrigidas ao longo da fase, mais duas
divergências novas encontradas **nesta** revisão de fechamento (RF-03 e a fronteira
roadmap↔requirements sobre reset de senha) que **não** foram corrigidas — ficam registradas
como pendência explícita, não escondidas. D-003 (RLS) e D-063 (UI da Fase 2) foram fechadas
formalmente. 52 testes automatizados + 8 MAT executados manualmente contra o backend real,
todos passando.

## 2. O que foi revisado

`crm-spec/docs/01-product/{personas,requirements}.md`, `02-business/business-rules.md`,
`03-architecture/security.md`, `05-api/{api-guidelines,openapi.yaml}`,
`09-testing/testing-strategy.md`, `10-roadmap/roadmap.md`, `00-governance/decision-register.md`,
ADR-004/008/009 — contra o código real de `crm-backend/src/modules/{auth,users,tenants,audit}`,
`prisma/schema.prisma`, e a suíte de testes (`test/`).

## 3. Matriz de auditoria

`Sim`/`Não`/`Parcial`. **MAT** aponta o roteiro manual correspondente; "—" = não se aplica
(item de infraestrutura/decisão, não de comportamento observável).

| Item | Especificado | Implementado | Testado (automatizado) | MAT | Status |
|---|---|---|---|---|---|
| Login (RF-01) | Sim | Sim | 3 casos e2e | [MAT-001](../manual-acceptance/MAT-001-login.md) — PASSOU | 🟢 |
| Refresh + rotação (RF-01) | Sim | Sim | 2 casos e2e | [MAT-002](../manual-acceptance/MAT-002-refresh.md) — PASSOU | 🟢 |
| Reuso pós-rotação revoga família (D-056) | Sim | Sim | 2 casos e2e | MAT-002 — PASSOU | 🟢 |
| Logout individual (RF-02) | Sim | Sim | 1 caso e2e | [MAT-003](../manual-acceptance/MAT-003-logout.md) — PASSOU | 🟢 |
| Logout global (RF-02/D-057) | Sim | Sim | 1 caso e2e | [MAT-004](../manual-acceptance/MAT-004-logout-global.md) — PASSOU | 🟢 |
| Refresh via cookie httpOnly (D-005) | Sim | Sim | Atributos verificados em MAT-001 | MAT-001 — PASSOU | 🟢 |
| SameSite/CSRF (D-006) | Sim (fechado nesta fase) | Sim (`Lax`, sem token) | Atributo verificado | MAT-001 — PASSOU | 🟢 |
| CRUD usuários — create/read | Sim | Sim | Múltiplos e2e | [MAT-005](../manual-acceptance/MAT-005-users-crud.md) — PASSOU | 🟢 |
| CRUD usuários — update/delete | Sim (roadmap) | Sim | 4 casos e2e novos | MAT-005 — PASSOU | 🟢 |
| Redefinição de senha (RF-03) | Sim (`requirements.md`) | **Não** | Nenhum | Não aplicável (não existe) | 🔴 |
| Múltiplos usuários/papéis por tenant (RF-04) | Sim | Sim | Coberto indiretamente | — | 🟢 |
| Paginação offset em `/users` (D-007/D-061) | Sim | Sim (corrigido nesta fase) | 1 caso e2e | MAT-005 — PASSOU | 🟢 |
| `role_ids` aceita UUID v7 (D-062) | Sim (implícito, ADR-009) | Sim (corrigido nesta fase) | 1 caso e2e | MAT-005 — PASSOU | 🟢 |
| Papéis de fábrica (roadmap) | Sim (8 personas de tenant) | Sim — catálogo cobre só módulo `users` (único existente) | Seed + e2e indireto | — | 🟢 (completo para o escopo atual) |
| RBAC — permissão negada → 403 | Sim | Sim | 2 casos e2e | [MAT-006](../manual-acceptance/MAT-006-rbac.md) — PASSOU | 🟢 |
| RBAC — escopo tenant apenas (D-058) | Sim (decisão explícita) | Sim | — | MAT-006 (observação) | 🟢 |
| RBAC — escopo equipe/filial | Adiado (D-058, Fase 3+) | Não (esperado) | — | — | 🟢 (adiamento correto, não gap) |
| Isolamento entre tenants (RF-05/06) | Sim | Sim | 8 casos e2e | [MAT-007](../manual-acceptance/MAT-007-tenant-isolation.md) — PASSOU | 🟢 |
| Tenant suspenso bloqueia login | Sim (implícito) | Sim | 1 caso e2e | [MAT-008](../manual-acceptance/MAT-008-tenant-suspended.md) — PASSOU | 🟢 |
| Provisionamento/suspensão de tenant pelo Super Admin (RF-07) | Sim | Não (manual/seed — D-059) | — | — | 🟡 (adiamento já registrado, RF-07 não atualizado para refletir) |
| Auditoria básica (BR-23/BR-24) | Sim | Sim — só `users` (D-060) | Verificado em e2e + MAT | MAT-005 — PASSOU | 🟢 |
| RLS (D-003) | A decidir até fim da fase | Decidido: não implementar | — | — | 🟢 (decisão formal registrada) |
| UI mínima da Fase 2 (D-063) | A decidir | Decidido: não exigida | — | — | 🟢 (decisão formal registrada) |

**Legenda**: 🟢 conforme · 🟡 divergência não bloqueante, já com decisão registrada · 🔴 divergência sem correção nesta fase, pendência explícita.

## 4. Divergências encontradas

1. **RF-03 não implementado** — `requirements.md` exige "o sistema deve permitir redefinição de senha"; não existe nenhum endpoint de troca/reset de senha em `auth` nem `users`. Contradição adicional: `roadmap.md` (Fase 2 "Funcionalidades") **não menciona** redefinição de senha, então o roadmap e o requisito já não concordavam entre si antes desta fase começar — não foi um esquecimento desta implementação, é uma lacuna que atravessou da Fase 0/1.
2. **RF-07 parcialmente coberto** — "Super Admin deve conseguir provisionar e suspender tenants" não tem nenhuma superfície (nem API, nem CLI) — só edição direta de seed/banco. D-059 já cobre a intenção ("provisionamento manual" é aceitável para o MVP), mas RF-07 em si nunca foi atualizado para refletir essa decisão explicitamente.
3. *(Já corrigidas ao longo da fase, não repetidas aqui em detalhe — ver `crm-backend/CLAUDE.md` "ÚLTIMA AÇÃO" 2026-09-09)*: D1 (refresh no corpo), D2 (família de sessões não reagia a reuso), D3 (sem logout global), paginação cursor→offset, `@IsUUID('4')` rejeitando v7.

## 5. Divergências corrigidas

Todas as 5 do item 3 acima (D1/D2/D3, D-061, D-062) — commits `794cf87`/`63062f0` em
`crm-backend`, `861cd22` em `crm-spec`. Nenhuma divergência nova desta rodada de auditoria foi
corrigida silenciosamente: as duas do item 4 (RF-03, RF-07) ficam registradas como pendência
(seção 14), não escondidas atrás de uma correção rápida fora do escopo desta tarefa.

## 6. Decisões tomadas nesta revisão

| Decisão | Veredito | Onde |
|---|---|---|
| D-003 (RLS) | **B — não implementar no MVP** | [Decision Register](../../00-governance/decision-register.md#d-003--postgresql-row-level-security), [ADR-004](../../adr/ADR-004.md), [security.md](../../03-architecture/security.md) |
| D-063 (UI da Fase 2) | **B — Fase 2 validada por API** | [Decision Register](../../00-governance/decision-register.md#d-063--fase-2-não-exige-interface-mínima-opção-b) |

## 7. Decisão D-003 (RLS) — resumo

Análise completa nas dez dimensões pedidas está na entrada D-003 do Decision Register (link
acima). Resumo: com Prisma (pool de conexões), RLS seguro exige envolver **toda leitura**
tenant-scoped numa transação com `SET LOCAL` — mudança de arquitetura cara, cujo risco de
implementação incorreta (vazamento de sessão de banco entre tenants por reuso de conexão) é
**pior** do que a situação atual. O isolamento primário (`TenantContextStorage` + filtro
obrigatório no Repository + teste e2e de vazamento obrigatório) já é testado e comprovadamente
funcional (13 testes de isolamento passando). Reabrir só com evidência nova — critério
registrado no Decision Register.

## 8. Estratégia de testes criada

Camada nova: **Manual Acceptance Test (MAT)**, adicionada a `testing-strategy.md` seção 1.
Estrutura em `docs/09-testing/`:
```
manual-acceptance/   — os roteiros (MAT-001 a MAT-008 + template MAT-SEC-TENANT-001)
phase-acceptance/    — este arquivo e os próximos, um por fase, no fechamento
evidence/            — política de evidência (a maior parte cabe inline nos MATs)
```
Fonte de verdade única confirmada: `crm-spec/docs/09-testing/` (estratégia + MAT + critérios
de aceite); repositórios de código guardam só o "como executar" curto — ver seção 9.

## 9. MATs criados

8 MATs de Fase 2 + 1 template reutilizável — todos **executados de verdade** (não só
escritos) contra o backend real, com evidência de resposta HTTP e consulta ao banco embutida
em cada arquivo. Ver índice em [manual-acceptance/README.md](../manual-acceptance/README.md).
Todos: **PASSOU**.

## 10. Organização dos arquivos

### Backend (`crm-backend`)

| Item | Classificação | Motivo |
|---|---|---|
| Estrutura `src/modules/<nome>` | 🟢 manter | Consistente com `backend-architecture.md`, escala bem |
| `test/{unit,integration,e2e}` separados por config Jest | 🟢 manter | Clareza de propósito, já documentado |
| `README.md` | 🔴 **corrigido nesta tarefa** | Estava referenciando Fase 1, Swagger em `/docs` (agora `/api/docs`), UUID v4 e "refresh token no corpo" — tudo desatualizado desde as correções da própria Fase 1/2 |
| `CLAUDE.md` seções "Arquitetura desta fase", "Limitações conhecidas", "Dependências para o frontend", tabela de ADRs | 🔴 **corrigido nesta tarefa** | Mesma staleness do README — descreviam paginação cursor (agora offset), ADR-008 com o conteúdo antigo (pré-reescrita), Swagger em `/docs` |
| `test.md` (467 linhas) | 🟡 melhorar futuramente | Sobreposição real com `crm-workspace/README.md` nas seções 1-6 (setup de Docker/Node/env); seções 7-10 (execução por camada + troubleshooting Windows) são valiosas e não duplicadas em lugar nenhum — não apagar, só marcar como candidato a divisão numa fase futura com menos urgência que os outros itens 🔴 |

### Frontend (`crm-frontend`)

| Item | Classificação | Motivo |
|---|---|---|
| `README.md`/`CLAUDE.md`/`test.md` | 🟢 manter | Já corretos — nenhuma menção a algo que a Fase 2 do backend invalidasse; "ainda não existe UI" continua verdade após D-063 |
| `src/{app,components,hooks,pages,routes,services,styles}` | 🔴 **reorganizado nesta tarefa** | Ver seção 11 — a estrutura por tipo de arquivo não escala para as ~7 entidades da Fase 3; baixo custo de mudar agora (poucos arquivos), alto custo depois |

### Specs (`crm-spec`)

| Item | Classificação | Motivo |
|---|---|---|
| `docs/00` a `docs/10` numerados por assunto | 🟢 manter | Já serve bem como fonte de verdade, links funcionam |
| `docs/09-testing/` | 🟡 melhorado nesta tarefa | Ganhou `manual-acceptance/`, `phase-acceptance/`, `evidence/` — estrutura nova, sem nada para "corrigir", só criar |
| `entities.md` (`audit_log` sem `tenant_id`) | 🔴 **corrigido na fase anterior** | Já resolvido antes desta tarefa (ver Decision Register D-060) |

### Workspace (`crm-workspace`)

| Item | Classificação | Motivo |
|---|---|---|
| `docker-compose.yml` + `scripts/` + `README.md` | 🟢 manter | Já testado ponta a ponta nesta sessão (`setup.sh` idempotente, infra sobe limpa) |

## 11. Arquitetura futura do frontend

**Proposta**: organização por feature/domínio (`src/features/<dominio>/{pages,components,hooks,services,types}`), preparando para Customers/Leads/Opportunities/Pipeline/Tasks/Notes/Agenda da Fase 3 sem `pages/` virar uma pasta de dezenas de arquivos soltos.

**Decisão de execução**: a estrutura atual tem poucos arquivos (uma página de status, uma home,
uma 404) — custo de mover agora é baixo; custo de mover depois de Customers/Leads existirem é
alto (mais arquivos, mais import a atualizar, mais risco). Executado nesta tarefa (ver
commits) sem alterar nenhum comportamento: lint, testes e build continuam verdes depois da
reorganização. Detalhe técnico e resultado da validação: seção 12.

Estrutura final:
```
src/
├── app/            providers, App.tsx, contexto de UI
├── features/
│   └── status/      pages/, services/, hooks/ do que hoje é infraestrutura de diagnóstico
├── components/ui/   design system compartilhado (Button, Input, Card, Alert, Spinner, EmptyState)
├── components/layout/  AppShell
├── routes/
├── styles/
└── test/
```
`HomePage`/`NotFoundPage` ficam em `app/` (não são feature de domínio, são a casca do app).
Quando a Fase 3 chegar, `features/leads/`, `features/customers/` etc. entram do lado de
`features/status/`, seguindo o mesmo padrão.

## 12. Decisão sobre UI da Fase 2

**B) Não** — Fase 2 validada por API; UI entra em fase posterior. Análise completa em
[D-063](../../00-governance/decision-register.md#d-063--fase-2-não-exige-interface-mínima-opção-b).

## 13. Resultados dos testes

| Repositório | Lint | Build | Unit | Integration | E2E | MAT |
|---|---|---|---|---|---|---|
| crm-backend | ✅ | ✅ | 23 ✅ | 2 ✅ | 27 ✅ | 8/8 PASSOU |
| crm-frontend | ✅ | ✅ | 4 ✅ | — | — | — (sem UI, D-063) |

Docker: build + `--profile apps up` validado nesta fase (ver `crm-backend/CLAUDE.md`), reconfirmado nesta revisão via ambiente local real (mesma infra) para a execução dos MATs.

## 14. Critérios de aceite

| Critério (roadmap Fase 2) | Automação | MAT | Resultado | Status |
|---|---|---|---|---|
| Testes automatizados de isolamento entre tenants passando | `tenant-isolation.e2e-spec.ts`, 13 casos | MAT-007 | Verde / PASSOU | 🟢 |
| Testes automatizados de permissão por papel passando | `auth`/`tenant-isolation` e2e | MAT-006 | Verde / PASSOU | 🟢 |
| Segundo tenant de teste não lê dado do primeiro em nenhuma rota | Coberto para `users` (único módulo) | MAT-007 | Verde / PASSOU | 🟢 |

Os três critérios formais do roadmap estão satisfeitos. RF-03/RF-07 (seção 4) não são
critérios de aceite *desta fase* segundo o roadmap — são requisitos gerais de produto ainda
não cobertos por nenhuma fase declarada; ficam como pendência, não como reprovação do critério
de aceite específico da Fase 2.

## 15. Pendências

| Pendência | Categoria |
|---|---|
| RF-03 (redefinição de senha) sem implementação nem fase declarada no roadmap | **NÃO BLOQUEADOR** desta fase, mas **sem dono** — recomenda-se decidir explicitamente em que fase entra antes da Fase 3 avançar muito, para não virar uma dívida esquecida |
| RF-07 (provisionamento/suspensão pelo Super Admin) sem atualização de texto refletindo D-059 | NÃO BLOQUEADOR — ajuste de redação pendente em `requirements.md` |
| `crm-backend/test.md` com sobreposição parcial ao `crm-workspace/README.md` | ADIADO — não bloqueia, baixo risco, candidato a limpeza numa fase futura |
| RLS (D-003) | **RESOLVIDO** nesta revisão — não é mais pendência |
| Granularidade por dispositivo em `revoked_reason`/sessões (hoje é por usuário) | FASE FUTURA — mencionado em D-056, sem necessidade real hoje |

## 16. Recomendação final

🟡 **APTA COM RESSALVAS**

Todos os critérios de aceite formais do roadmap estão satisfeitos, com evidência automatizada
e manual convergente (52 testes + 8 MAT, todos verdes). As ressalvas são duas divergências
reais contra `requirements.md` (RF-03, RF-07) que **preexistiam** a esta fase e não foram
inventadas nem escondidas por esta revisão — ficam como pendência explícita, não como bloqueio,
porque nenhuma delas está nos critérios de aceite que o `roadmap.md` define para a Fase 2
especificamente. Recomenda-se que a decisão sobre RF-03 (quando e como implementar
redefinição de senha) seja tomada antes de a Fase 3 avançar o suficiente para que a lacuna
fique mais cara de fechar.

Fase 3 **não foi iniciada** por esta tarefa.
