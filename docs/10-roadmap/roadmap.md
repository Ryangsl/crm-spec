# Roadmap

Cada fase só inicia com a anterior aceita (critérios de aceite cumpridos). Detalhamento do que compõe o MVP (subconjunto das Fases 0-3) está em [mvp.md](mvp.md).

## FASE 0 — Especificação
- **Objetivo**: produzir a documentação completa que permita implementar o sistema com segurança (este repositório).
- **Funcionalidades**: nenhuma (documentação apenas).
- **Dependências**: nenhuma.
- **Critérios de aceite**: vision, personas, requisitos, arquitetura, modelo de dados, contrato de API inicial, roadmap e ADRs iniciais existentes e sem contradição entre si; decisões pendentes explicitamente marcadas.
- **Riscos**: requisitos de negócio presumidos incorretamente por falta de validação com stakeholders reais — mitigado marcando `[DECISÃO PENDENTE]` em vez de inventar.

## FASE 1 — Fundação técnica
- **Objetivo**: esqueleto executável dos três repositórios.
- **Funcionalidades**: setup de `crm-backend` (NestJS, Prisma, estrutura de módulos vazia, health checks, logging), setup de `crm-frontend` (Vite, Tailwind, roteamento, design system inicial), Docker Compose local, CI básico.
- **Dependências**: Fase 0 aceita.
- **Critérios de aceite**: backend e frontend sobem localmente via Docker Compose; health check responde; CI roda lint/test vazio com sucesso.
- **Riscos**: escolha prematura de detalhe de infraestrutura que trave decisão pendente — mitigado adiando o que estiver marcado `[DECISÃO PENDENTE]` até ser necessário.
- **Status — `crm-backend`**: implementado (além do esqueleto mínimo, já inclui base de autenticação, RBAC inicial e isolamento multi-tenant do grupo "Tenancy e Acesso" — itens que originalmente estavam listados na Fase 2, adiantados porque a fundação de auth/tenant é pré-requisito estrutural, ver `crm-backend/README.md` e `ADR-008`). Build, lint e testes unitários passam; testes de integração/E2E (precisam de Postgres+Redis reais) foram escritos mas **não foram executados** no ambiente onde a Fase 1 foi implementada (sem Docker disponível) — validação local pendente antes de considerar a fase formalmente aceita. `crm-frontend` da Fase 1 (Vite/Tailwind/roteamento) ainda não foi iniciado.

## FASE 2 — Autenticação + Usuários + Tenants
- **Objetivo**: multi-tenancy e RBAC funcionando de ponta a ponta.
- **Funcionalidades**: login/refresh/logout, CRUD de usuários, papéis de fábrica, isolamento de tenant, auditoria básica.
- **Nota**: login/refresh/logout, papéis de fábrica e isolamento de tenant já foram entregues como parte da Fase 1 estendida do `crm-backend` (ver nota de status na Fase 1 acima e `ADR-008`). O que resta especificamente para a Fase 2: `update`/`delete` de usuários (Fase 1 só tem `create`/`read`), escopo de dado por equipe/filial no RBAC, e auditoria básica (`audit_log`, ainda não modelado).
- **Dependências**: Fase 1.
- **Critérios de aceite**: testes automatizados de isolamento entre tenants e de permissão por papel passando (ver [../09-testing/testing-strategy.md](../09-testing/testing-strategy.md)); segundo tenant de teste não consegue, em nenhuma rota, ler dado do primeiro.
- **Riscos**: vazamento cross-tenant — risco crítico, tratado com testes obrigatórios antes de prosseguir para dados de negócio reais.

## FASE 3 — CRM
- **Objetivo**: ciclo Lead → Oportunidade → Pipeline funcionando.
- **Funcionalidades**: Clientes, Leads (com distribuição round-robin), Oportunidades, Pipeline configurável, Tarefas, Notas, Agenda básica.
- **Dependências**: Fase 2.
- **Critérios de aceite**: fluxo completo de [../01-product/use-cases.md](../01-product/use-cases.md) UC-01 a UC-04 executável via API e UI.
- **Riscos**: modelo de campos personalizados subdimensionado — mitigado por decisão registrada em [../04-database/database.md](../04-database/database.md) seção 6.

## FASE 4 — Atendimento
- **Objetivo**: histórico unificado de interação por cliente, mesmo antes da telefonia completa.
- **Funcionalidades**: módulo de Interações (registro manual de atendimento), notas de atendimento, primeira versão de Notificações.
- **Dependências**: Fase 3.
- **Critérios de aceite**: histórico de interações de um cliente reflete leads, oportunidades e atendimentos manuais em uma linha do tempo única.
- **Riscos**: baixo — módulo majoritariamente de leitura/agregação.

## FASE 5 — Call Center
- **Objetivo**: telefonia mínima viável.
- **Funcionalidades**: Filas, status de operador, click-to-call/discagem manual, disposição de chamada, painel de supervisão em tempo real (WebSocket com fallback).
- **Dependências**: Fase 4; escolha de provedor de telefonia (`[DECISÃO PENDENTE]`, ver [../03-architecture/integrations.md](../03-architecture/integrations.md)).
- **Critérios de aceite**: fluxo UC-05/UC-06/UC-07 executável; SLA e status de fila visíveis em tempo real; fallback de polling testado com WebSocket desligado.
- **Riscos**: dependência de provedor externo — mitigado pela camada de abstração `ChannelAdapter` (ver [../03-architecture/architecture.md](../03-architecture/architecture.md)).

## FASE 6 — Omnichannel
- **Objetivo**: WhatsApp integrado ao histórico único do cliente.
- **Funcionalidades**: Conversas, Mensagens, Templates, webhooks de canal, idempotência e reprocessamento.
- **Dependências**: Fase 5 (reaproveita filas/atendimento); escolha de provedor de WhatsApp (`[DECISÃO PENDENTE]`).
- **Critérios de aceite**: UC-08 executável ponta a ponta; teste de reentrega de webhook não duplica mensagem (BR-20).
- **Riscos**: bloqueio de número pelo provedor não oficial — mitigado pela recomendação de API oficial como canal primário (ver [integrations.md](../03-architecture/integrations.md)).

## FASE 7 — Dashboard
- **Objetivo**: indicadores confiáveis para gestores e supervisores.
- **Funcionalidades**: Dashboard de vendas (funil, conversão) e de atendimento (volume, SLA, produtividade), Relatórios exportáveis.
- **Dependências**: Fases 3-6 (dados a agregar já existem).
- **Critérios de aceite**: indicadores batem com contagem manual em cenário de teste controlado; performance de consulta não degrada a operação (RNF-01).
- **Riscos**: consulta analítica pesada impactar produção — mitigado por réplica de leitura/materialização quando necessário (ver [../03-architecture/scalability.md](../03-architecture/scalability.md)).

## FASE 8 — Automações
- **Objetivo**: reduzir trabalho manual repetitivo.
- **Funcionalidades**: Campanhas (disparo em massa via canais já integrados), regras simples de automação (ex.: notificar gerente se oportunidade parada há N dias).
- **Dependências**: Fase 6 (canais) e Fase 7 (dados para gatilhos).
- **Critérios de aceite**: campanha de teste executa via fila assíncrona sem impacto perceptível na operação síncrona.
- **Riscos**: uso indevido para spam — mitigado por limites de plano/rate limiting por tenant.

## FASE 9 — Escalabilidade
- **Objetivo**: preparar a operação para volume maior, com evidência real de necessidade.
- **Funcionalidades**: réplica de leitura, particionamento das tabelas de alto volume, adapter Redis para WebSocket multi-instância, revisão de índices com dado real de produção.
- **Dependências**: operação real gerando dado de uso suficiente para decisão informada.
- **Critérios de aceite**: RNF-01/RNF-02 sustentados sob a carga real observada.
- **Riscos**: otimizar prematuramente sem dado real — mitigado por só entrar nesta fase com evidência (ver [../03-architecture/scalability.md](../03-architecture/scalability.md) seção 8).

## FASE 10 — IA como funcionalidade do produto
- **Objetivo**: recursos de IA voltados ao usuário final (não confundir com uso de IA para desenvolver o software, ver [../../agents/](../../agents/)).
- **Funcionalidades candidatas**: sugestão de próxima ação em oportunidade, resumo automático de atendimento, transcrição de chamada. Escopo exato é `[DECISÃO PENDENTE]`, a ser detalhado em documento próprio quando esta fase se aproximar.
- **Dependências**: volume de dado histórico suficiente (interações, chamadas) das fases anteriores.
- **Critérios de aceite**: a definir na especificação da fase.
- **Riscos**: custo de inferência, qualidade/alucinação, privacidade de dado de cliente usado em prompt — a tratar com o mesmo rigor de segurança do restante do sistema.
