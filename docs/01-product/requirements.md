# Requisitos

## 1. Requisitos Funcionais (RF)

### Autenticação e Usuários
- RF-01: O sistema deve permitir login com e-mail/senha, emitindo access token JWT (TTL 15 min) e refresh token (TTL 7 dias, em cookie httpOnly) — ver [ADR-008](../adr/ADR-008.md).
- RF-02: O sistema deve permitir logout com revogação de refresh token, individual (um dispositivo) e global (todos).
- RF-03: O sistema deve permitir redefinição de senha. **Sem fase declarada no roadmap e sem implementação** — achado na revisão de fechamento da Fase 2 ([phase-02.md](../09-testing/phase-acceptance/phase-02.md) seção 4); `[VALIDAÇÃO DE NEGÓCIO NECESSÁRIA]` sobre qual fluxo (admin reseta/usuário troca a própria/"esqueci minha senha" por e-mail — este último depende de D-040, provedor de e-mail, ainda `ADIADO`) e em qual fase entra.
- RF-04: O sistema deve suportar múltiplos usuários por tenant, cada um com um ou mais papéis.

### Multi-tenancy
- RF-05: Todo dado de negócio deve pertencer a exatamente um tenant.
- RF-06: Um usuário autenticado só deve conseguir ler/escrever dados do(s) tenant(s) ao qual pertence.
- RF-07: O Super Admin da plataforma deve conseguir provisionar e suspender tenants sem acessar dados de negócio do tenant. Provisionamento hoje é manual (edição direta de seed/banco — [D-059](../00-governance/decision-register.md#d-059--provisionamento-de-tenant-permanece-manual-fase-2), `DECIDIDO`); nenhuma ferramenta, nem interna, existe ainda para isso — RF-07 fica satisfeito só parcialmente (a restrição de não acessar dado de negócio já vale, por não haver acesso nenhum — ver [D-036](../00-governance/decision-register.md#d-036--acesso-de-suporte-do-super-admin-a-dados-de-tenant)) até D-059 ser revisitado.

### CRM
- RF-08: O sistema deve permitir cadastro, edição, visualização e (soft) exclusão de Clientes, Leads, Contatos e Oportunidades.
- RF-09: O sistema deve permitir configurar um ou mais Pipelines com etapas customizáveis por tenant.
- RF-10: O sistema deve registrar histórico de mudança de etapa de uma oportunidade.
- RF-11: O sistema deve permitir marcar oportunidade como Ganha ou Perdida, exigindo motivo no caso de perda.
- RF-12: O sistema deve permitir distribuição automática de leads (round-robin no MVP).
- RF-13: O sistema deve permitir registrar tarefas, notas e agendamentos vinculados a lead/oportunidade/cliente.
- RF-14: O sistema deve permitir tags e campos personalizados em Clientes/Leads. No MVP, campos personalizados são suportados **estruturalmente** via `JSONB` ([D-008](../00-governance/decision-register.md#d-008--campos-personalizados-mvp), `DECIDIDO`); a gestão visual de campos (criação pelo usuário, permissões por campo, validação configurável) fica fora do MVP ([D-009](../00-governance/decision-register.md#d-009--sistema-completo-de-campos-personalizados), `ADIADO`).

### Atendimento / Call Center
*(RF-15, RF-16, RF-19 e RF-20 são da Fase 5 — fora do MVP, ver [D-015](../00-governance/decision-register.md#d-015--escopo-oficial-do-mvp). RF-17 e RF-18 já valem no MVP, aplicados ao registro manual de atendimento.)*

- RF-15: O sistema deve permitir que um operador entre/saia de uma ou mais filas e altere seu status (Disponível, Ocupado, Pausa, Offline).
- RF-16: O sistema deve distribuir chamadas/atendimentos de uma fila entre operadores disponíveis.
- RF-17: O sistema deve permitir registrar a disposição (resultado) de um atendimento.
- RF-18: O sistema deve manter histórico completo de atendimentos por cliente (chamadas, mensagens, notas), com timestamps.
- RF-19: O sistema deve permitir supervisão em tempo real do status de operadores e filas.
- RF-20: O sistema deve permitir click-to-call (originar chamada a partir da tela de CRM).

### Omnichannel
*(Fase 6 — fora do MVP. A abstração de canal exigida por RF-22 já orienta o desenho desde a Fase 1.)*

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
- RNF-05: Falhas de integração com provedores externos (telefonia/WhatsApp) não devem derrubar o restante do sistema — timeout curto é obrigatório desde a primeira integração; circuit breaker é [D-039](../00-governance/decision-register.md#d-039--circuit-breaker-para-provedores-externos) (`ADIADO` para a Fase 5). Sem integração externa no MVP, este RNF só passa a ser exercitado na Fase 5.
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
