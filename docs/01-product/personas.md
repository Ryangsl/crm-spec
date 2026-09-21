# Personas e Perfis de Acesso (RBAC)

Este documento define os perfis de acesso iniciais do sistema. O RBAC é **extensível**: um tenant poderá criar papéis customizados a partir de um conjunto de permissões atômicas (ver seção 9). Os perfis abaixo são os papéis "de fábrica" (system roles).

## 1. Modelo de RBAC

- Permissões são atômicas, no formato `recurso:ação` (ex.: `leads:create`, `calls:listen`, `reports:export`).
- Um **Papel (Role)** é uma coleção nomeada de permissões, associada a um tenant (papéis customizados) ou global/system (papéis de fábrica, somente leitura para o tenant).
- Um usuário pode ter um ou mais papéis dentro de um tenant.
- Escopo de dado (quais registros um usuário vê, não apenas quais telas) é resolvido por uma combinação de papel + hierarquia (equipe/filial) + regra "dono do registro" — detalhado em [../03-architecture/security.md](../03-architecture/security.md).
- `Super Admin da plataforma` não é um papel de tenant: é um papel global, fora do escopo de qualquer tenant, usado pela equipe operadora do SaaS.

## 2. Perfis

### 2.1 Super Admin da plataforma
- **Objetivo**: operar a plataforma SaaS (não a operação comercial de nenhum tenant específico).
- **Responsabilidades**: provisionar/suspender tenants, monitorar saúde da plataforma, suporte de segundo nível, gestão de planos.
- **Funcionalidades**: painel de administração da plataforma (fora do produto principal do tenant).
- **Visualiza**: metadados de todos os tenants (nome, plano, uso, status); **não** acessa dados de clientes/leads de um tenant. O fluxo de exceção para suporte (consentimento, janela temporal, auditoria) é `[VALIDAÇÃO DE NEGÓCIO NECESSÁRIA]` — [D-036](../00-governance/decision-register.md#d-036--acesso-de-suporte-do-super-admin-a-dados-de-tenant), a definir antes do painel de plataforma (pós-MVP). Enquanto não definido, o acesso simplesmente não existe.
- **Cria/edita/exclui**: tenants, planos, limites.
- **Restrições**: **nenhum** acesso operacional aos dados de negócio do tenant — não existe hoje um caminho autorizado, nem com auditoria. Um eventual "Support Access Controlado" (motivo obrigatório, acesso temporário, auditoria, expiração automática, preferência por read-only) só existirá se e quando [D-036](../00-governance/decision-register.md#d-036--acesso-de-suporte-do-super-admin-a-dados-de-tenant) for aprovada, com ADR próprio.

### 2.2 Administrador da empresa (tenant admin)
- **Objetivo**: configurar e administrar a conta da empresa no sistema.
- **Responsabilidades**: gerenciar usuários, papéis, filas, filiais, equipes, integrações, configurações gerais.
- **Funcionalidades**: todos os módulos administrativos + acesso amplo aos módulos operacionais.
- **Visualiza**: todos os dados do tenant.
- **Cria**: usuários, papéis customizados, filas, filiais, equipes, campanhas, configurações.
- **Edita**: qualquer registro do tenant.
- **Exclui**: usuários (desativação lógica), registros administrativos; exclusão de dados de negócio (clientes/leads) segue [../02-business/business-rules.md](../02-business/business-rules.md) (soft delete).
- **Restrições**: não acessa dados de outros tenants; ações administrativas críticas (ex.: exportar toda a base) são auditadas.

### 2.3 Diretor
- **Objetivo**: visão estratégica do negócio.
- **Responsabilidades**: acompanhar indicadores globais, aprovar metas e políticas comerciais.
- **Funcionalidades**: dashboards executivos, relatórios, pipeline (leitura ampla).
- **Visualiza**: todos os dados comerciais e de atendimento do tenant (todas as equipes/filiais).
- **Cria**: metas, opcionalmente campanhas.
- **Edita**: metas e configurações comerciais de alto nível.
- **Exclui**: normalmente não exclui registros operacionais.
- **Restrições**: sem acesso a configurações técnicas/administrativas de sistema (papéis, integrações).

### 2.4 Gerente
- **Objetivo**: gerir uma ou mais equipes/filiais.
- **Responsabilidades**: distribuir leads, acompanhar metas da equipe, aprovar exceções (ex.: reabrir oportunidade perdida).
- **Funcionalidades**: pipeline, relatórios da própria equipe/filial, gestão de tarefas da equipe.
- **Visualiza**: dados das equipes/filiais sob sua gestão.
- **Cria**: oportunidades, tarefas, campanhas locais.
- **Edita**: registros das equipes sob sua gestão.
- **Exclui**: registros das equipes sob sua gestão, conforme regras de negócio.
- **Restrições**: não visualiza dados de equipes/filiais fora de seu escopo; sem acesso a configurações globais do tenant.

### 2.5 Supervisor (Call Center — nome legado)
> Nota ([D-070](../00-governance/decision-register.md#d-070--definição-de-produto-crm-comercial--atendimentoconversas--whatsapp-sem-call-center-telefônico)): o produto não é um Call Center telefônico; leia como **supervisor de atendimento/conversas**. Renomear o papel exige mudança de seed e permanece pendente. Itens de chamada/escuta ficam fora de escopo.
- **Objetivo**: gerir a operação de atendimento em tempo real.
- **Responsabilidades**: monitorar status de operadores e filas, intervir em atendimentos (escuta/assumir), gerenciar pausas e SLA.
- **Funcionalidades**: painel de monitoramento em tempo real, filas, relatórios de call center, gestão de disposições de chamada.
- **Visualiza**: operadores e filas sob sua supervisão; histórico de atendimento da equipe.
- **Cria**: filas (se permitido), escalas/pausas, motivos de disposição.
- **Edita**: status de fila, reatribuição de atendimentos.
- **Exclui**: normalmente não exclui histórico de atendimento (auditoria).
- **Restrições**: sem acesso a dados comerciais fora de call center, salvo se acumular outro papel.

### 2.6 Vendedor / Consultor
- **Objetivo**: converter leads em vendas.
- **Responsabilidades**: qualificar leads, conduzir oportunidades pelo pipeline, agendar follow-ups.
- **Funcionalidades**: CRM (leads, clientes, oportunidades, pipeline, agenda, tarefas), atendimento ativo.
- **Visualiza**: seus próprios leads/oportunidades/clientes e, se configurado, os da equipe.
- **Cria**: leads, oportunidades, clientes, tarefas, notas, agendamentos.
- **Edita**: os registros dos quais é responsável (dono).
- **Exclui**: nada — vendedor/consultora não tem permissão de exclusão sobre Leads/Clientes/Oportunidades; toda exclusão (sempre soft delete) fica restrita a Gerente/Admin, sem fluxo de aprovação nesta fase ([D-035](../00-governance/decision-register.md#d-035--regra-de-aprovação-para-exclusão-por-vendedor), `DECIDIDO`).
- **Restrições**: sem acesso a registros de outros vendedores fora de sua equipe, salvo liberação do gerente; sem acesso a configurações administrativas.

### 2.7 Operador de Call Center (nome legado)
> Nota ([D-070](../00-governance/decision-register.md#d-070--definição-de-produto-crm-comercial--atendimentoconversas--whatsapp-sem-call-center-telefônico)): leia como **atendente/consultor de atendimento**; atende conversas (WhatsApp), não chamadas. Sua disponibilidade governa a distribuição (BR-14, [D-071](../00-governance/decision-register.md#d-071--disponibilidade-de-consultoratendente-para-distribuição-automática)). Renomear o papel exige mudança de seed e permanece pendente.
- **Objetivo**: realizar atendimento receptivo/ativo dentro de filas.
- **Responsabilidades**: atender chamadas/mensagens da fila, registrar disposição, escalar quando necessário.
- **Funcionalidades**: tela de atendimento (histórico do cliente, discador/soft-phone, WhatsApp), status de disponibilidade.
- **Visualiza**: o cliente/contato do atendimento em curso e seu histórico; fila em que está logado.
- **Cria**: registros de atendimento, notas, tarefas de follow-up, leads a partir de atendimento receptivo.
- **Edita**: o atendimento em curso.
- **Exclui**: não exclui histórico de atendimento.
- **Restrições**: sem acesso a dados fora da fila/equipe; sem acesso a relatórios gerenciais completos (apenas os próprios).

### 2.8 Backoffice
- **Objetivo**: suporte administrativo à operação comercial/atendimento (cadastro, conferência, pós-venda).
- **Responsabilidades**: validar dados de clientes, processar documentação, dar apoio pós-venda.
- **Funcionalidades**: CRM (edição de dados cadastrais), tarefas, anexos.
- **Visualiza**: clientes/oportunidades conforme escopo definido pelo admin.
- **Cria/edita**: dados cadastrais, anexos, notas.
- **Exclui**: normalmente não.
- **Restrições**: sem acesso a métricas de call center ou configurações administrativas.

### 2.9 Usuário somente leitura
- **Objetivo**: consulta (ex.: auditor, sócio, integração externa via usuário técnico de leitura).
- **Responsabilidades**: nenhuma responsabilidade de execução.
- **Funcionalidades**: dashboards e relatórios, visualização de registros conforme escopo liberado.
- **Visualiza**: conforme escopo explicitamente concedido.
- **Cria/edita/exclui**: nada.
- **Restrições**: acesso 100% de leitura, sem exceções.

## 3. Matriz-resumo de permissões por módulo

`C` = Create, `R` = Read, `U` = Update, `D` = Delete, `-` = sem acesso. Escopo de "quais registros" (próprio/equipe/filial/tenant) é tratado à parte, ver seção 4.

| Módulo | Super Admin | Admin Empresa | Diretor | Gerente | Supervisor | Vendedor | Operador | Backoffice | Leitura |
|---|---|---|---|---|---|---|---|---|---|
| Usuários/Papéis | - (só plataforma) | CRUD | R | R (equipe) | R (equipe) | - | - | - | R |
| Leads | - | CRUD | R | CRUD (equipe) | R | CRU (próprio) | C (de atendimento) | RU | R |
| Clientes | - | CRUD | R | CRUD (equipe) | R | CRU (próprio) | R | RU | R |
| Oportunidades/Pipeline | - | CRUD | R | CRUD (equipe) | R | CRU (próprio) | - | R | R |
| Atendimentos/Call Center | - | CRUD | R | R (equipe) | CRUD (fila) | R (próprio) | CRUD (próprio) | R | R |
| Filas/Telefonia (config) | - | CRUD | - | R | RU | - | - | - | - |
| Campanhas | - | CRUD | R | CU (equipe) | R | R | - | - | R |
| Relatórios/Dashboard | Plataforma | R (tenant) | R (tenant) | R (equipe) | R (call center) | R (próprio) | R (próprio) | R (limitado) | R (escopo liberado) |
| Configurações do tenant | - | CRUD | - | - | - | - | - | - | - |
| Auditoria | R (plataforma) | R (tenant) | R (tenant) | - | - | - | - | - | - |

`CRU (próprio)` do Vendedor em Leads/Clientes/Oportunidades — sem `D` — reflete [D-035](../00-governance/decision-register.md#d-035--regra-de-aprovação-para-exclusão-por-vendedor) (`DECIDIDO`): vendedor não exclui, apenas Gerente/Admin.

Esta matriz é o ponto de partida; o detalhamento operação-a-operação vive no código como *policies* versionadas (ver [../03-architecture/security.md](../03-architecture/security.md) e [../07-backend/backend-architecture.md](../07-backend/backend-architecture.md)).

## 4. Escopo de dados (data scoping)

Além do papel (o que a tela permite fazer), todo acesso a um registro passa por um filtro de escopo:

- **Próprio** — apenas registros onde o usuário é o responsável (`owner_id`).
- **Equipe** — registros de usuários que reportam ao gerente/supervisor dentro da mesma equipe.
- **Filial** — registros de qualquer equipe dentro da mesma filial.
- **Tenant** — todos os registros do tenant.

[D-016](../00-governance/decision-register.md#d-016--escopo-de-dados-por-equipefilial) (`DECIDIDO`, Fase 2): o escopo é resolvido por **atribuição estática** usuário → equipe → filial. Hierarquia dinâmica (árvore de gerência com profundidade arbitrária) fica adiada até haver necessidade real validada — o modelo de dados suporta a evolução sem migração destrutiva.

**Fronteira de implementação explícita** ([D-058](../00-governance/decision-register.md#d-058--escopo-de-rbac-na-fase-2-e-na-fase-3-apenas-tenant), `DECIDIDO`, reafirmado para a Fase 3 em 2026-09-16):
- **Fase 2 e Fase 3**: RBAC aplicado apenas no escopo **Tenant** — uma permissão concedida (ex.: `users:read`) dá acesso a todos os registros do tenant, sem filtro adicional. As colunas "R (equipe)"/"CRUD (equipe)" da matriz acima (Gerente, Supervisor) **ainda não são aplicadas** nesta fase; na prática, esses papéis leem/gerenciam o tenant inteiro também na Fase 3.
- **Fase futura (a definir)**: filtro por Equipe e Filial só passa a valer de fato quando os módulos `Team`/`Branch` tiverem CRUD e regra de negócio ativa — o Decision Gate da Fase 3 confirmou que essa ativação **não** acontece na Fase 3.
- Não simular escopo de equipe/filial parcialmente antes dessa fase futura — a ausência do filtro é deliberada e documentada, não um bug a mascarar.

## 5. Papéis customizados (extensibilidade)

O modelo de dados (`roles` + `permissions`, ver [../04-database/entities.md](../04-database/entities.md)) suporta papéis customizados desde o início, mas a **UI de criação de papéis fica fora do MVP** ([D-050](../00-governance/decision-register.md#d-050--papéis-customizados-via-ui), `ADIADO` — pós-MVP, mediante demanda real): os papéis de fábrica atendem o MVP. Criar novas *permissões atômicas* nunca é feito via UI — isso é definido no backend a cada módulo novo.
