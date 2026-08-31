# MVP

## 1. Objetivo do MVP

Um produto pequeno o suficiente para ser desenvolvido, testado e colocado em produção rapidamente, mas que já entrega o núcleo do diferencial do produto: CRM e atendimento no mesmo lugar, com histórico único do cliente, multi-tenant e Mobile First desde o primeiro dia. Corresponde às **Fases 0 a 4** do roadmap, mais um recorte mínimo de Call Center (parte inicial da Fase 5), suficiente para validar a proposta de valor completa — CRM **e** atendimento — sem esperar pela Fase 5 inteira.

## 2. Entra no MVP

**Plataforma**
- Multi-tenant com isolamento por `tenant_id`, RBAC com papéis de fábrica (ver [../01-product/personas.md](../01-product/personas.md)).
- Autenticação (login, refresh, logout), auditoria básica.

**CRM**
- Clientes, Contatos, Leads (com origem e distribuição round-robin), Oportunidades, um Pipeline configurável por tenant com etapas.
- Notas, Tarefas, Agenda básica.
- Histórico único de interação por cliente (linha do tempo).

**Atendimento (recorte mínimo de Call Center)**
- Registro manual de atendimento (o operador registra que atendeu, por qual canal, com qual resultado) — **sem** integração de telefonia real ainda.
- Click-to-call **é avaliado como stretch goal do MVP**, não bloqueador: `[DECISÃO PENDENTE]` se entra na primeira release ou logo em seguida, dependendo da definição do provedor de telefonia (ver [../03-architecture/integrations.md](../03-architecture/integrations.md)).
- Filas e status de operador ficam para a Fase 5 completa (painel de supervisão em tempo real não é MVP).

**Frontend**
- Mobile First/PWA, com os fluxos acima cobertos em `xs` a `xl` (ver [../06-frontend/responsive.md](../06-frontend/responsive.md)).

**Plataforma técnica**
- Filas assíncronas (BullMQ) para o que já existir de processamento em background (ex.: notificações, importação simples de leads via CSV).
- Observabilidade mínima: logs estruturados + captura de erro (Sentry).

## 3. NÃO entra no MVP

- Telefonia integrada de verdade (chamada originada/recebida via provedor) — fica para Fase 5.
- WhatsApp/omnichannel — Fase 6.
- Dashboard analítico completo e exportação de relatórios — Fase 7.
- Campanhas e automações — Fase 8.
- Particionamento de banco, múltiplas instâncias de backend, Kubernetes — Fase 9 (sem evidência de necessidade ainda).
- IA como funcionalidade de produto — Fase 10.
- Campos personalizados avançados, papéis customizados via UI (papéis de fábrica são suficientes no MVP) — `[DECISÃO PENDENTE]` se entram logo após o MVP ou ficam para quando houver demanda de cliente real.
- Aplicativo nativo de loja (iOS/Android) — PWA cobre o MVP.
- Self-service de criação de tenant — provisionamento inicial é manual/assistido.

## 4. Por que este recorte

- Overengineering é o risco explícito citado no prompt original do produto: um discador preditivo, multi-canal completo e IA no dia 1 adiariam indefinidamente a validação do core (CRM + atendimento unificados), que é o diferencial real do produto (ver [../01-product/vision.md](../01-product/vision.md) seção 6).
- Registro manual de atendimento no MVP já entrega o valor central — "histórico único do cliente" — sem depender da complexidade e do risco de integração de um provedor de telefonia/WhatsApp externo antes de validar o resto do produto.
- Multi-tenant e RBAC entram desde o início porque são estruturais: adicioná-los depois exigiria retrabalho amplo em todo o modelo de dados (ver [../03-architecture/security.md](../03-architecture/security.md)).

## 5. Critério de saída do MVP

O MVP é considerado entregue quando o fluxo `Lead recebido → distribuição → contato → qualificação → oportunidade → negociação → venda/perda`, com histórico de interação e auditoria, funciona de ponta a ponta, multi-tenant, com RBAC aplicado, testado (ver [../09-testing/testing-strategy.md](../09-testing/testing-strategy.md)) e utilizável em um celular de 360px de largura.
