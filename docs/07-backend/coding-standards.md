# Padrões de Código — Backend

## 1. Linguagem e estilo

- TypeScript estrito (`strict: true`); `any` proibido salvo exceção justificada em comentário.
- Nomenclatura: `camelCase` para variáveis/funções, `PascalCase` para classes/tipos, `snake_case` apenas em nomes de coluna/tabela de banco (mapeados via Prisma para `camelCase` no código).
- Um módulo de negócio = um diretório em `src/modules/<nome>`, nunca lógica de módulo espalhada em `shared/`.

## 2. Convenção de commits e branches

Ver estratégia de Git completa em [../adr/](../adr/) (a definir em ADR específico) e no fluxo geral do projeto — resumo:
- Branches: `feature/*`, `fix/*`, `refactor/*`, a partir de `main` (ou `develop`, se adotado — `[DECISÃO PENDENTE]`).
- Commits descrevem o "porquê", não apenas o "o quê".

## 3. Regras específicas do domínio (obrigatórias em code review)

- Nenhum Controller contém lógica de negócio — apenas validação de entrada (via DTO) e delegação ao Service.
- Nenhum Service de um módulo importa Repository de outro módulo (ver [backend-architecture.md](backend-architecture.md) seção 4).
- Toda query de listagem é paginada (nunca `findMany` sem `take`/cursor) — proteção contra RNF-01.
- Toda operação de escrita relevante passa pela checagem de tenant + permissão + escopo antes de tocar o banco (BR-25).
- Nenhuma exclusão física de dado de negócio via código de aplicação (soft delete apenas — BR-22).
- Toda mudança de estado relevante (conversão de lead, mudança de etapa, disposição de chamada) emite o evento de domínio correspondente (ver [../03-architecture/architecture.md](../03-architecture/architecture.md) seção 7) — não é opcional, é o mecanismo de auditoria/notificação.
- Segredos de integração nunca em código-fonte, apenas via configuração de ambiente/cofre.

## 4. O que nunca fazer

- Nunca desabilitar validação de tenant "temporariamente" para debugar — usar dado de seed local em vez disso (ver [../08-devops/local-development.md](../08-devops/local-development.md)).
- Nunca fazer `console.log` em código de produção — usar o logger estruturado.
- Nunca capturar exceção genérica silenciosamente (`catch {}` vazio) — sempre logar ou relançar.
- Nunca acoplar regra de negócio a um provedor externo específico de telefonia/WhatsApp fora da camada de adapter (ver [../03-architecture/integrations.md](../03-architecture/integrations.md)).
- Nunca versionar `.env` com segredos reais — apenas `.env.example` (ver [../08-devops/local-development.md](../08-devops/local-development.md)).

## 5. Testes exigidos por tipo de mudança

Ver detalhamento completo em [../09-testing/testing-strategy.md](../09-testing/testing-strategy.md). Regra mínima: nenhuma regra de negócio (BR-xx) é mesclada sem teste automatizado cobrindo o caminho feliz e ao menos uma violação da regra.

## 6. Revisão de código

- Toda mudança que introduz ou altera uma regra de negócio deve referenciar a regra correspondente em [../02-business/business-rules.md](../02-business/business-rules.md) (ou propor sua criação/atualização).
- Toda mudança de contrato de API deve atualizar [../05-api/openapi.yaml](../05-api/openapi.yaml) no mesmo PR.
- Decisão arquitetural nova ou revisada exige ADR (ver [../adr/](../adr/)) antes ou junto do PR de implementação.
