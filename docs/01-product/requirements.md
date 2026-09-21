# Requisitos

## 1. Requisitos Funcionais (RF)

### Autenticação e Usuários
- RF-01: O sistema deve permitir login com e-mail/senha, emitindo access token JWT (TTL 15 min) e refresh token (TTL 7 dias, em cookie httpOnly) — ver [ADR-008](../adr/ADR-008.md).
- RF-02: O sistema deve permitir logout com revogação de refresh token, individual (um dispositivo) e global (todos).
- RF-03: O sistema deve permitir redefinição de senha. **Sem fase declarada no roadmap e sem implementação** — achado na revisão de fechamento da Fase 2 ([phase-02.md](../09-testing/phase-acceptance/phase-02.md) seção 4), registrado formalmente como [D-064](../00-governance/decision-register.md#d-064--rf-03-redefinição-de-senha-fase-e-fluxo-indefinidos) (`VALIDAÇÃO DE NEGÓCIO`, prazo: antes do primeiro cliente em produção). `[VALIDAÇÃO DE NEGÓCIO NECESSÁRIA]` sobre qual fluxo (admin reseta/usuário troca a própria/"esqueci minha senha" por e-mail — este último depende de D-040, provedor de e-mail, ainda `ADIADO`) e em qual fase entra. Não é critério de aceite de nenhuma fase declarada hoje — não bloqueia a Fase 2 nem o início da Fase 3.
- RF-04: O sistema deve suportar múltiplos usuários por tenant, cada um com um ou mais papéis.

### Multi-tenancy
- RF-05: Todo dado de negócio deve pertencer a exatamente um tenant.
- RF-06: Um usuário autenticado só deve conseguir ler/escrever dados do(s) tenant(s) ao qual pertence.
- RF-07: O Super Admin da plataforma deve conseguir provisionar e suspender tenants sem acessar dados de negócio do tenant. **Escopo atual (Fase 2), alinhado a [D-059](../00-governance/decision-register.md#d-059--provisionamento-de-tenant-permanece-manual-fase-2) `DECIDIDO`**: provisionamento é manual/assistido (edição direta de seed/banco), sem painel administrativo, self-service, API pública ou CLI dedicada — não há obrigação de construir essa ferramenta nesta fase, e isso **não bloqueia** o aceite técnico da Fase 2. A restrição de não acessar dado de negócio do tenant já vale hoje, por não existir esse acesso ([D-036](../00-governance/decision-register.md#d-036--acesso-de-suporte-do-super-admin-a-dados-de-tenant)). Suspensão de tenant (o outro verbo do requisito) já está implementada e coberta por [MAT-008](../09-testing/manual-acceptance/MAT-008-tenant-suspended.md). Automatizar o provisionamento é evolução futura em aberto, a decidir se/quando houver necessidade real (ex.: volume de onboarding que justifique — ver D-059).

### CRM
- RF-08: O sistema deve permitir cadastro, edição, visualização e (soft) exclusão de Clientes, Leads, Contatos e Oportunidades.
- RF-09: O sistema deve permitir configurar um ou mais Pipelines com etapas customizáveis por tenant.
- RF-10: O sistema deve registrar histórico de mudança de etapa de uma oportunidade.
- RF-11: O sistema deve permitir marcar oportunidade como Ganha ou Perdida, exigindo motivo no caso de perda.
- RF-12: O sistema deve permitir distribuição automática de leads (round-robin no MVP).
- RF-13: O sistema deve permitir registrar tarefas, notas e agendamentos vinculados a lead/oportunidade/cliente.
- RF-14: O sistema deve permitir tags e campos personalizados em Clientes/Leads. No MVP, campos personalizados são suportados **estruturalmente** via `JSONB` ([D-008](../00-governance/decision-register.md#d-008--campos-personalizados-mvp), `DECIDIDO`); a gestão visual de campos (criação pelo usuário, permissões por campo, validação configurável) fica fora do MVP ([D-009](../00-governance/decision-register.md#d-009--sistema-completo-de-campos-personalizados), `ADIADO`).

### Atendimento / Conversas e disponibilidade
*(O produto é CRM Comercial + Atendimento/Conversas + WhatsApp, **não** um Call Center telefônico — [D-070](../00-governance/decision-register.md#d-070--definição-de-produto-crm-comercial--atendimentoconversas--whatsapp-sem-call-center-telefônico). RF-15 (disponibilidade) é da Fase 4, com modelagem pendente em [D-071](../00-governance/decision-register.md#d-071--disponibilidade-de-consultoratendente-para-distribuição-automática); RF-16 na parte de conversas e RF-19 são da Fase 5 — fora do MVP, ver [D-015](../00-governance/decision-register.md#d-015--escopo-oficial-do-mvp). RF-17 e RF-18 já valem no MVP, aplicados ao registro manual de atendimento.)*

- RF-15: O sistema deve permitir que um consultor/atendente altere seu status de disponibilidade (Disponível, Ocupado, Pausa, Offline — conjunto e semântica sujeitos a [D-071](../00-governance/decision-register.md#d-071--disponibilidade-de-consultoratendente-para-distribuição-automática)) e, quando houver filas de atendimento, entre/saia delas.
- RF-16: O sistema deve distribuir novos leads/conversas/atendimentos apenas entre consultores/atendentes **ativos e disponíveis** (BR-14). Para leads o round-robin já existe (RF-12, Fase 3.4) e ainda não aplica disponibilidade.
- RF-17: O sistema deve permitir registrar a disposição (resultado) de um atendimento/conversa (BR-15).
- RF-18: O sistema deve manter histórico completo de atendimentos por cliente (interações, conversas, mensagens, notas), com timestamps.
- RF-19: O sistema deve permitir supervisão em tempo real do status de disponibilidade dos atendentes e das filas de atendimento.
- ~~RF-20~~: **removido** ([D-070](../00-governance/decision-register.md#d-070--definição-de-produto-crm-comercial--atendimentoconversas--whatsapp-sem-call-center-telefônico)) — click-to-call é telefonia, fora do escopo do produto.

### Conversas / WhatsApp / Omnichannel
*(WhatsApp/Conversas — RF-21 e RF-23 — na Fase 5; canais adicionais e caixa de entrada unificada na Fase 6; tudo fora do MVP. A abstração de canal exigida por RF-22 já orienta o desenho desde a Fase 1.)*

- RF-21: O sistema deve permitir receber e enviar mensagens via WhatsApp associadas ao histórico do cliente.
- RF-22: O sistema deve suportar múltiplos canais de comunicação através de uma camada de abstração, sem acoplamento direto do CRM a um provedor específico.
- RF-23: O sistema deve tratar webhooks de canais de forma idempotente.

### Relatórios e Dashboard
*(Fase 7 — fora do MVP.)*

- RF-24: O sistema deve fornecer dashboard com indicadores de vendas (funil, conversão) e de atendimento (volume, SLA, produtividade), filtrável por período/equipe.
- RF-25: O sistema deve permitir exportação de relatórios (Fase 7; formatos suportados: [D-038](../00-governance/decision-register.md#d-038--formatos-de-exportação-de-relatórios), `ADIADO` até lá).

### Notificações
*(Primeira versão na Fase 4, dentro do MVP; regras de gatilho mais elaboradas só na Fase 8.)*

- RF-26: O sistema deve notificar usuários sobre eventos relevantes (lead atribuído, tarefa vencendo, oportunidade parada há X dias).

### Auditoria
- RF-27: O sistema deve registrar log de auditoria (quem, o quê, quando) para criação/edição/exclusão de dados sensíveis e ações administrativas.

## 2. Requisitos Não Funcionais (RNF)

### Desempenho e Escalabilidade
- RNF-01: Endpoints de leitura de listagens devem responder em até 300ms sob carga nominal (p95), com paginação obrigatória.
- RNF-02: O sistema deve suportar crescimento horizontal do backend (stateless, sessão fora do processo) — ver [../03-architecture/scalability.md](../03-architecture/scalability.md).
- RNF-03: Processos pesados (importação, relatórios, envio em massa) devem ser assíncronos, nunca bloquear a requisição HTTP.

### Disponibilidade e Confiabilidade
- RNF-04: Falha de WebSocket não deve impedir o uso do sistema — deve haver fallback (polling) para dados críticos.
- RNF-05: Falhas de integração com provedores externos (WhatsApp/outros canais) não devem derrubar o restante do sistema — timeout curto é obrigatório desde a primeira integração; circuit breaker é [D-039](../00-governance/decision-register.md#d-039--circuit-breaker-para-provedores-externos) (`ADIADO` para a Fase 5). Sem integração externa no MVP, este RNF só passa a ser exercitado na Fase 5.
- RNF-06: Filas assíncronas devem ter retry com backoff e dead-letter queue.

### Segurança
- RNF-07: Toda comunicação deve ocorrer via HTTPS/WSS.
- RNF-08: Senhas devem ser armazenadas com hash forte (bcrypt/argon2), nunca em texto puro.
- RNF-09: Todo endpoint deve validar tenant e permissão antes de qualquer acesso a dado.
- RNF-10: Uploads devem ser validados (tipo, tamanho) e armazenados fora do alcance de execução direta.
- RNF-11: O sistema deve estar apto a atender solicitações de titular de dados compatíveis com a LGPD (acesso, correção, exclusão) — ver [../03-architecture/security.md](../03-architecture/security.md).

### Usabilidade
- RNF-12: Toda tela principal deve ser utilizável em viewport de celular (≥360px) sem perda de funcionalidade crítica.
- RNF-13: Tempo de aprendizado para um operador realizar seu primeiro atendimento não deve exceder um treinamento de 15 minutos (heurística de simplicidade de UI).

### Observabilidade
- RNF-14: Toda requisição deve gerar log estruturado com correlação (request id) e tenant id.
- RNF-15: O sistema deve expor health checks para orquestração (liveness/readiness).

### Manutenibilidade
- RNF-16: Backend e frontend evoluem por contratos de API versionados — mudança incompatível exige nova versão, nunca quebra de contrato existente silenciosa.
- RNF-17: Toda decisão arquitetural relevante deve ser registrada como ADR antes ou junto da implementação.

## 3. Fora de escopo nesta etapa

Requisitos de IA como funcionalidade de produto (sugestões, transcrição, resumo automático) são tratados apenas como visão de roadmap (Fase 10) e não são detalhados aqui.
