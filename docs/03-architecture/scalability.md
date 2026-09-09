# Escalabilidade

## 1. Princípio

O sistema deve poder crescer de uma operação pequena para uma operação grande **sem redesenho de arquitetura**, mesmo que a infraestrutura do dia 1 seja modesta (um único servidor, Docker Compose). Isso é alcançado evitando decisões que criem armadilhas, não construindo para escala máxima prematuramente.

## 2. Backend stateless

- Nenhum estado de sessão/negócio vive na memória do processo do backend (sessão via JWT/refresh token no banco/Redis, não em memória local).
- Isso permite rodar múltiplas instâncias do backend atrás de um load balancer sem sticky session, exceto para conexões WebSocket, que exigem afinidade ou um adaptador compartilhado ([D-046](../00-governance/decision-register.md#d-046--adapter-redis-para-websocket-multi-instância), `ADIADO`: adapter Redis só é necessário quando houver mais de uma instância **e** WebSocket em uso — ou seja, não antes da Fase 5).

## 3. Banco de dados

- PostgreSQL único, sem réplica, é o suficiente para o crescimento inicial — escalabilidade vertical (mais CPU/RAM) é o primeiro recurso. Réplica de leitura para relatórios/dashboard é um mecanismo **previsto para a Fase 9**, não para agora ([D-014](../00-governance/decision-register.md#d-014--escalabilidade-avançada), ver seção 8).
- Índices desde o modelo inicial em `tenant_id` + colunas de filtro comuns (ver [../04-database/database.md](../04-database/database.md)).
- Particionamento (ex.: por `tenant_id` ou por período em tabelas de alto volume como `interactions`/`messages`/`audit_log`) é um mecanismo previsto, mas **não implementado no MVP** — a modelagem deve evitar decisões que impeçam particionar depois (ex.: chave primária compatível, evitar FKs que dificultem partição).
- Tenants com volume desproporcional podem, no futuro, migrar para schema/banco dedicado sem mudança de aplicação, graças ao uso consistente de `tenant_id` (ver [security.md](security.md)).

## 4. Cache e filas

- Redis cobre: cache de leitura de dados de configuração/pouco mutáveis, filas assíncronas (BullMQ) e pub/sub para WebSocket entre instâncias.
- Filas assíncronas absorvem picos de carga (ex.: importação de milhares de leads, campanhas em massa) sem degradar a API síncrona.

## 5. Tempo real

- WebSocket é escalado via adaptador compartilhado (Redis pub/sub) quando há múltiplas instâncias, para que um evento gerado por uma instância chegue a clientes conectados em outra.
- Fallback via polling garante degradação graciosa sob alta carga ou indisponibilidade momentânea do canal de tempo real (RNF-04).

## 6. Call Center e Omnichannel

- A camada de abstração de canais (adapters) permite trocar de provedor ou adicionar múltiplos provedores do mesmo tipo (ex.: dois números de WhatsApp, dois troncos de voz) para distribuir carga sem mudar regra de negócio.
- Processamento de webhooks é assíncrono (enfileirado) para não travar sob rajada de eventos de um provedor.

## 7. Observabilidade como pré-requisito de escala

Não é possível escalar com segurança sem visibilidade — ver [../03-architecture/architecture.md](architecture.md) seção 6 e [../08-devops/deployment.md](../08-devops/deployment.md)). Métricas de fila, latência de API e saturação de banco são o sinal primário de quando escalar (vertical, réplicas, particionamento).

## 8. O que é explicitamente adiado

[D-014](../00-governance/decision-register.md#d-014--escalabilidade-avançada) (`DECIDIDO`: não implementar agora). A arquitetura inicial é monólito modular + NestJS + PostgreSQL + Redis + BullMQ. Ficam de fora até haver evidência real:

- Kubernetes/orquestração avançada — Docker Compose/VPS cobre a fase inicial.
- Microsserviços — permanece monólito modular até haver evidência de necessidade de escalar um módulo isoladamente ([ADR-003](../adr/ADR-003.md)).
- Réplicas de leitura, particionamento de banco e sharding — adiados até o volume real justificar.
- Multi-região e sistemas distribuídos — fora de escopo inicial.

"Evidência real" significa métrica observada de volume, gargalo ou necessidade operacional — não suposição, não antecipação. Cada uma dessas decisões, quando revisitada, exige um novo ADR.
