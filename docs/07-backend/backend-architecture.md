# Arquitetura de Backend

Repositório: `crm-backend`. Monólito modular (ADR-003) em NestJS/TypeScript.

## 1. Stack e avaliação de necessidade

| Tecnologia | Papel | Necessária desde o MVP? |
|---|---|---|
| Node.js + TypeScript | Runtime/linguagem | Sim |
| NestJS | Framework (DI, módulos, guards, pipes) | Sim — a estrutura modular exigida pela arquitetura (ADR-003) é o próprio ponto forte do NestJS |
| Prisma | ORM/migrations | Sim — tipagem forte do modelo de dados alinhada ao TypeScript, migrations versionadas |
| PostgreSQL | Banco relacional | Sim (ADR-001) |
| Redis | Cache, filas, pub/sub de WebSocket | Sim a partir do momento em que houver qualquer processamento assíncrono (importação, mensageria) — que já está no MVP (ver [../10-roadmap/mvp.md](../10-roadmap/mvp.md)) |
| BullMQ | Filas assíncronas sobre Redis | Sim, mesma justificativa acima |
| WebSocket (Socket.IO ou `ws` nativo do Nest) | Tempo real | Parcial no MVP — necessário assim que houver painel de supervisão/status de operador (ver roadmap); não bloqueia o MVP mínimo de CRM puro |

## 2. Estrutura de módulos

```
src/
  modules/
    auth/
    tenants/
    users/
    customers/
    leads/
    opportunities/
    pipelines/
    calls/
    queues/
    messaging/
    campaigns/
    reports/
    notifications/
  shared/
    dto/
    decorators/
    filters/
    pipes/
  infrastructure/
    database/        # Prisma client, repositórios base
    queue/            # BullMQ setup, processors
    realtime/         # gateway WebSocket
    channels/         # adapters de canal (ver ../03-architecture/integrations.md)
```

Cada módulo em `modules/` corresponde a um módulo de negócio de [../03-architecture/architecture.md](../03-architecture/architecture.md) seção 2, mantendo nomenclatura consistente com `crm-frontend` (`features/`).

## 3. Camadas dentro de um módulo

- **Controller**: recebe request HTTP, valida via DTO, delega ao Service. Não contém regra de negócio.
- **Service**: contém a regra de negócio do módulo; orquestra repositórios e emite eventos de domínio.
- **Repository**: acesso a dado via Prisma, sempre com `tenant_id` aplicado (ver seção 5); nunca chamado diretamente por outro módulo — apenas pelo Service do próprio módulo.
- **DTO**: contrato de entrada/saída, com `class-validator` (padronizado na Fase 1 — ver [ADR-008](../adr/ADR-008.md#2-validação-de-dto-class-validator)).
- **Guards**: autenticação e resolução de tenant (rodam antes de qualquer handler).
- **Policies**: autorização (permissão do papel + escopo de dado), aplicadas após os Guards, por ação.
- **Events**: módulos emitem eventos de domínio (`lead.qualified`, `opportunity.won`, etc.) para desacoplar side effects (notificação, auditoria) — ver [../03-architecture/architecture.md](../03-architecture/architecture.md) seção 7.
- **Jobs/Workers**: processadores BullMQ para trabalho assíncrono, vivendo em `infrastructure/queue`, mas com regra de negócio delegada ao Service do módulo correspondente (worker não duplica regra).

## 4. Comunicação entre módulos

- Síncrona (mesma request): módulo A injeta o Service público de módulo B apenas quando a dependência é uma leitura simples e estável (ex.: Opportunities lê Customers). Nunca injeta Repository de outro módulo.
- Assíncrona (efeito colateral desacoplado): via eventos internos (event emitter do Nest); evolução natural para fila (BullMQ) se o efeito puder ser processado fora da request.

## 5. Multi-tenancy na camada de dados

- Todo Repository aplica `tenant_id` a partir de um contexto de requisição (`AsyncLocalStorage` ou equivalente do Nest), nunca a partir de parâmetro explícito passado por controller sem validação.
- Nenhuma query crua (`$queryRaw`) é permitida sem revisão explícita que garanta o filtro de tenant.
- Reforço com Row Level Security no PostgreSQL como segunda camada de defesa foi avaliado e adiado para a Fase 2+ (ver [ADR-008](../adr/ADR-008.md#3-row-level-security-rls-adiado-para-a-fase-2) e [../03-architecture/security.md](../03-architecture/security.md)).

## 6. Tratamento de erros

- Exceções de domínio (`LeadAlreadyConvertedException`, etc.) mapeadas por um `ExceptionFilter` global para o formato de erro padronizado do contrato (ver [../05-api/api-guidelines.md](../05-api/api-guidelines.md) seção 6).
- Erros não tratados nunca vazam stack trace/detalhe interno para o cliente em produção.

## 7. Logging

- Logs estruturados (JSON) via Pino (ver [../03-architecture/architecture.md](../03-architecture/architecture.md) e [observabilidade em deployment.md](../08-devops/deployment.md)), incluindo `request_id`, `tenant_id`, `user_id` quando disponível.
- Nunca logar senha, token ou segredo de integração, mesmo em nível debug.

## 8. Validação e segurança de entrada

- Todo DTO de entrada é validado por pipe antes de chegar ao Controller/Service.
- Sanitização de campos de texto livre antes de persistir quando o conteúdo pode ser renderizado como HTML em algum lugar (defesa em profundidade, mesmo com sanitização no frontend).

## 9. Configuração

- Configuração via variáveis de ambiente, validadas na inicialização (falha rápida se faltar configuração obrigatória) — ver [../08-devops/local-development.md](../08-devops/local-development.md).
- Segredos nunca hardcoded nem versionados (ver [../03-architecture/security.md](../03-architecture/security.md)).

## 10. Caminho de extração futura de serviço

Como preparação (não implementação) para uma eventual extração de um módulo para serviço separado (ex.: Call Center sob alta carga própria), cada módulo deve: (a) não depender de transação de banco compartilhada com outro módulo para sua regra central, (b) comunicar-se com outros módulos preferencialmente por evento, (c) ter seu próprio conjunto de DTOs sem reexportar tipos internos de outro módulo. Isso é guiado pelo ADR-003 e não é um trabalho ativo do MVP.
