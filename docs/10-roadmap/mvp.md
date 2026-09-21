# MVP

## 1. Objetivo do MVP

Um produto pequeno o suficiente para ser desenvolvido, testado e colocado em produção rapidamente, mas que já entrega o núcleo do diferencial: CRM e atendimento no mesmo lugar, com histórico único do cliente, multi-tenant e Mobile First desde o primeiro dia. Corresponde às **Fases 0 a 4** do roadmap ([D-015](../00-governance/decision-register.md#d-015--escopo-oficial-do-mvp), `DECIDIDO`). Nada da Fase 5 entra no MVP — o atendimento é registrado manualmente, sem telefonia integrada.

## 2. Entra no MVP

**Plataforma**
- Multi-tenant com isolamento por `tenant_id`, RBAC com papéis de fábrica (ver [../01-product/personas.md](../01-product/personas.md)).
- Autenticação (login, refresh, logout), auditoria básica.

**CRM**
- Clientes, Contatos, Leads (com origem e distribuição round-robin), Oportunidades, um Pipeline configurável por tenant com etapas.
- Notas, Tarefas, Agenda básica.
- Histórico único de interação por cliente (linha do tempo).

**Atendimento**
- Registro manual de atendimento (o operador registra que atendeu, por qual canal, com qual resultado) alimentando o histórico unificado do cliente — **sem** integração de telefonia.
- Telefonia (click-to-call, chamadas) **não faz parte do produto** ([D-070](../00-governance/decision-register.md#d-070--definição-de-produto-crm-comercial--atendimentoconversas--whatsapp-sem-call-center-telefônico): o produto é CRM Comercial + Atendimento/Conversas + WhatsApp, não um Call Center telefônico). O provedor de telefonia ([D-010](../00-governance/decision-register.md#d-010--provedor-de-telefonia)) está sem fase.
- Disponibilidade de consultor/atendente ([D-071](../00-governance/decision-register.md#d-071--disponibilidade-de-consultoratendente-para-distribuição-automática)) entra na Fase 4; filas de conversa, distribuição de conversas por disponibilidade e painel de supervisão em tempo real são Fase 5 (WhatsApp/Conversas).

**Frontend**
- Mobile First/PWA, com os fluxos acima cobertos em `xs` a `xl` (ver [../06-frontend/responsive.md](../06-frontend/responsive.md)).

**Plataforma técnica**
- Redis + BullMQ disponíveis como infraestrutura, mas **sem criar filas desnecessárias** ([D-012](../00-governance/decision-register.md#d-012--redis--bullmq)): no MVP, a única fila justificada é a importação de leads em lote (CSV). O restante permanece síncrono até haver necessidade real.
- Observabilidade mínima: logs estruturados (Pino) + captura de erro (Sentry).
- **Sem WebSocket** ([D-013](../00-governance/decision-register.md#d-013--websocket)) — nenhuma funcionalidade do MVP depende de tempo real.

## 3. NÃO entra no MVP

- Telefonia integrada (chamada originada/recebida via provedor) — fora do escopo do produto ([D-070](../00-governance/decision-register.md#d-070--definição-de-produto-crm-comercial--atendimentoconversas--whatsapp-sem-call-center-telefônico)).
- WhatsApp/Conversas — Fase 5; Omnichannel (canais adicionais e caixa de entrada unificada) — Fase 6.
- Dashboard analítico completo e exportação de relatórios — Fase 7.
- Campanhas e automações — Fase 8.
- Particionamento de banco, múltiplas instâncias de backend, Kubernetes — Fase 9 (sem evidência de necessidade ainda).
- IA como funcionalidade de produto — Fase 10.
- Sistema completo de campos personalizados — criação visual, permissões por campo, validação configurável, engine EAV ([D-009](../00-governance/decision-register.md#d-009--sistema-completo-de-campos-personalizados), `ADIADO`). O suporte estrutural via `JSONB` ([D-008](../00-governance/decision-register.md#d-008--campos-personalizados-mvp)) entra; a plataforma de customização, não.
- Papéis customizados via UI ([D-050](../00-governance/decision-register.md#d-050--papéis-customizados-via-ui), `ADIADO`) — papéis de fábrica são suficientes no MVP; o modelo de dados já suporta a evolução.
- Aplicativo nativo de loja (iOS/Android) — PWA cobre o MVP.
- Self-service de criação de tenant — provisionamento inicial é manual/assistido.

## 4. Por que este recorte

- Overengineering é o risco explícito citado no prompt original do produto: um discador preditivo, multi-canal completo e IA no dia 1 adiariam indefinidamente a validação do core (CRM + atendimento unificados), que é o diferencial real do produto (ver [../01-product/vision.md](../01-product/vision.md) seção 6).
- Registro manual de atendimento no MVP já entrega o valor central — "histórico único do cliente" — sem depender da complexidade e do risco de integração de um provedor de telefonia/WhatsApp externo antes de validar o resto do produto.
- Multi-tenant e RBAC entram desde o início porque são estruturais: adicioná-los depois exigiria retrabalho amplo em todo o modelo de dados (ver [../03-architecture/security.md](../03-architecture/security.md)).

## 5. Critério de saída do MVP

O MVP é considerado entregue quando o fluxo `Lead recebido → distribuição → contato → qualificação → oportunidade → negociação → venda/perda`, com histórico de interação e auditoria, funciona de ponta a ponta, multi-tenant, com RBAC aplicado, testado (ver [../09-testing/testing-strategy.md](../09-testing/testing-strategy.md)) e utilizável em um celular de 360px de largura.
