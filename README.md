# crm-spec

Documentação oficial (fonte da verdade) do **CRM + Call Center SaaS**. Este repositório concentra visão de produto, regras de negócio, arquitetura, modelo de dados, contratos de API, roadmap e ADRs. `crm-backend` e `crm-frontend` implementam a partir daqui — nenhuma decisão de produto ou arquitetura relevante deve ser tomada apenas no código, sem refletir aqui antes ou depois.

## Como este repositório está organizado

| Pasta | Conteúdo |
|---|---|
| [docs/00-governance/](docs/00-governance/) | **Decision Register** — status de toda decisão do projeto e o que bloqueia cada fase |
| [docs/01-product/](docs/01-product/) | Visão, personas, casos de uso, requisitos funcionais/não funcionais |
| [docs/02-business/](docs/02-business/) | Regras de negócio e fluxos de trabalho |
| [docs/03-architecture/](docs/03-architecture/) | Arquitetura geral, segurança, escalabilidade, integrações |
| [docs/04-database/](docs/04-database/) | Modelo de dados, entidades, relacionamentos |
| [docs/05-api/](docs/05-api/) | Diretrizes de API e contrato OpenAPI |
| [docs/06-frontend/](docs/06-frontend/) | Arquitetura de frontend, design system, responsividade |
| [docs/07-backend/](docs/07-backend/) | Arquitetura de backend e padrões de código |
| [docs/08-devops/](docs/08-devops/) | Ambiente local e deployment |
| [docs/09-testing/](docs/09-testing/) | Estratégia de testes |
| [docs/10-roadmap/](docs/10-roadmap/) | Roadmap por fases e definição de MVP |
| [docs/adr/](docs/adr/) | Architecture Decision Records |
| [agents/](agents/) | Instruções para agentes de IA (Claude, Codex, revisor) trabalhando neste projeto |

## Repositórios do projeto

1. **crm-spec** (este repositório) — documentação, contratos, arquitetura e decisões.
2. **crm-backend** — API e regras de negócio (NestJS/TypeScript). Lê este repositório como fonte de verdade.
3. **crm-frontend** — interface Mobile First / PWA (React/TypeScript). Consome apenas os contratos definidos em [docs/05-api/](docs/05-api/).

## Como consumir esta documentação (humanos e agentes de IA)

1. Comece por [docs/01-product/vision.md](docs/01-product/vision.md) para entender o produto.
2. Leia [docs/01-product/personas.md](docs/01-product/personas.md) e [docs/03-architecture/security.md](docs/03-architecture/security.md) para entender RBAC e multi-tenancy antes de tocar em qualquer regra de acesso.
3. Antes de modelar uma entidade nova, consulte [docs/04-database/entities.md](docs/04-database/entities.md) — pode já existir.
4. Antes de criar um endpoint, consulte [docs/05-api/api-guidelines.md](docs/05-api/api-guidelines.md) e o [docs/05-api/openapi.yaml](docs/05-api/openapi.yaml).
5. Toda decisão arquitetural relevante deve virar um ADR em [docs/adr/](docs/adr/), seguindo o formato de [ADR-001](docs/adr/ADR-001.md).
6. Toda decisão do projeto vive no [Decision Register](docs/00-governance/decision-register.md) — comece por ele para saber o que já está decidido, o que está adiado e o que ainda depende de stakeholders. Pontos marcados `[VALIDAÇÃO DE NEGÓCIO NECESSÁRIA]` no texto não devem ser presumidos por nenhum agente.

## Estado do projeto

**FASE 0 (Especificação) concluída — FASE 1 (Fundação técnica) liberada para iniciar.** Não há nenhuma decisão `BLOQUEADOR` aberta. Nenhum código de produção foi escrito ainda. Ver [docs/10-roadmap/roadmap.md](docs/10-roadmap/roadmap.md) e [Decision Register](docs/00-governance/decision-register.md).

## Convenções deste repositório

- Idioma: português (pt-BR) para todo o conteúdo de produto e negócio; nomes de entidades, campos e endpoints em inglês (para consistência com código).
- Toda decisão tem status no [Decision Register](docs/00-governance/decision-register.md): `DECIDIDO`, `PROPOSTO`, `ADIADO`, `VALIDAÇÃO DE NEGÓCIO` ou `BLOQUEADOR`. Um ponto em aberto no texto sempre aponta para a entrada `D-xxx` correspondente — nunca fica solto.
- **Só `BLOQUEADOR` impede trabalho**, e apenas na fase que depende dele. Decisão adiada ou proposta não é motivo para parar uma fase que não depende dela.
- Lacuna que depende de stakeholder humano é marcada `[VALIDAÇÃO DE NEGÓCIO NECESSÁRIA]` — nenhum agente inventa a resposta.
- Mudança de decisão já tomada (registrada em ADR) exige um novo ADR que substitui o anterior — não editar silenciosamente um ADR aceito.
