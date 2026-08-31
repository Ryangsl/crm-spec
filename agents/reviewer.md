# Divisão de agentes e papel do revisor

## 1. Princípio

Nenhuma ferramenta de IA é "sempre melhor" — a divisão abaixo é por tipo de tarefa, não por preferência fixa de marca. Revisitar esta divisão se a evidência de uso mostrar que ela não está funcionando (registrar a mudança aqui, com o porquê).

## 2. Divisão sugerida

### Claude
- Product discovery e arquitetura (manutenção deste repositório, `crm-spec`).
- Backend (`crm-backend`): módulos, regras de negócio, integrações, banco de dados.
- Documentação.
- Code review complexo: regra de negócio, segurança, multi-tenancy, decisões arquiteturais.

Motivo: tarefas com alto custo de erro (isolamento entre tenants, regra de negócio, decisão que vira ADR) se beneficiam de um agente operando com o contexto completo da documentação de produto/arquitetura, não apenas do código local.

### Codex (ou agente equivalente de execução)
- Frontend (`crm-frontend`): componentes, telas, integrações com a API já definida.
- Testes (unit, component, E2E).
- Refatorações dentro de um módulo já definido.
- Code review de frontend (aderência ao design system, responsividade, tratamento de estados).

Motivo: tarefas de execução dentro de um contrato já bem definido (a API já existe, o design system já existe) se beneficiam de um agente focado em produzir/iterar código rapidamente dentro de fronteiras claras.

### Outros agentes de programação (Gemini e demais)
Podem ser usados para tarefas específicas (ex.: geração de testes em lote, exploração de alternativas de implementação) desde que sigam as mesmas regras deste repositório — nenhuma tarefa está reservada por marca de agente, apenas pelo tipo de responsabilidade acima.

## 3. Papel do revisor (qualquer agente atuando como reviewer)

Antes de aprovar qualquer mudança, o agente revisor confere:

1. **Regra de negócio**: a mudança referencia a regra correspondente em [../docs/02-business/business-rules.md](../docs/02-business/business-rules.md)? Se introduz regra nova, ela foi documentada?
2. **Contrato**: mudança de API atualiza [../docs/05-api/openapi.yaml](../docs/05-api/openapi.yaml) no mesmo PR?
3. **Multi-tenancy**: todo acesso a dado novo aplica `tenant_id` a partir do contexto autenticado? Existe teste de vazamento cross-tenant para endpoint novo?
4. **Permissão**: a ação passou pela checagem de papel + escopo (BR-25)? Está coerente com [../docs/01-product/personas.md](../docs/01-product/personas.md)?
5. **Decisão arquitetural**: a mudança introduz uma tecnologia, padrão ou estratégia nova? Se sim, existe ADR em [../docs/adr/](../docs/adr/)?
6. **Testes**: cobertura mínima obrigatória de [../docs/09-testing/testing-strategy.md](../docs/09-testing/testing-strategy.md) foi atendida?
7. **Consistência de documentação**: a mudança deixou algum documento desatualizado (entidade nova sem entrada em [../docs/04-database/entities.md](../docs/04-database/entities.md), módulo novo sem entrada em [../docs/03-architecture/architecture.md](../docs/03-architecture/architecture.md))?

Uma mudança que falha em qualquer um dos pontos acima não deve ser aprovada apenas por "funcionar" — funcionar não é o critério de qualidade deste projeto (ver [../README.md](../README.md) critério de qualidade).

## 4. Quando o revisor deve marcar `[DECISÃO PENDENTE]` em vez de decidir sozinho

Se a mudança expõe uma lacuna de decisão de produto/negócio ainda não definida na documentação (não uma decisão técnica de implementação), o revisor não deve inventar a resposta — deve pausar a aprovação, registrar a lacuna como `[DECISÃO PENDENTE]` no documento relevante, e sinalizar explicitamente para decisão humana.
