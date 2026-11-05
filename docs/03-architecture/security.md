# Segurança

## 1. Multi-tenancy: estratégia de isolamento

### 1.1 Opções avaliadas

| Estratégia | Isolamento | Custo operacional | Escalabilidade de onboarding | Complexidade inicial |
|---|---|---|---|---|
| Banco compartilhado + `tenant_id` | Lógico (aplicação) | Baixo | Alta (novo tenant = uma linha) | Baixa |
| Schema por tenant | Médio (banco) | Médio/Alto (migração roda N vezes) | Média (limite prático de schemas) | Média |
| Banco por tenant | Alto (banco/infra) | Alto | Baixa (provisionamento por tenant) | Alta |

### 1.2 Decisão

**Banco compartilhado com `tenant_id`** em todas as tabelas de negócio (ADR-004). Justificativa: menor complexidade operacional para o estágio atual do produto (permite lançar e crescer sem provisionar infraestrutura por cliente), custo de onboarding de novo tenant é trivial, e o modelo é compatível com migração futura para schema/banco por tenant para clientes específicos (ex.: grandes contas com exigência contratual de isolamento físico), caso necessário — extração fica mais fácil justamente por já existir `tenant_id` bem aplicado.

Isso exige tratar isolamento entre tenants como **requisito crítico de segurança**, não um detalhe de implementação.

### 1.3 Mecanismos de isolamento

- Toda tabela de negócio tem coluna `tenant_id` (NOT NULL, indexada, FK para `tenants`).
- Toda query de leitura/escrita passa por uma camada obrigatória que injeta o filtro de `tenant_id` a partir do contexto autenticado — **nunca** a partir de parâmetro vindo do cliente. A cadeia é fixa:

```
Request → JWT → Auth Guard → Tenant Context → Service → Repository/Prisma → filtro obrigatório por tenant_id
```

- **Proibido**: qualquer rota em que o usuário escolha o tenant acessado (ex.: `GET /customers?tenant_id=123`). O `tenant_id` recebido do frontend nunca é fonte confiável.
- **Antes do login**, a empresa é identificada pelo endereço de acesso (cabeçalho `Host`, domínio verificado em `tenant_domains`), nunca por valor enviado pelo cliente; o e-mail é procurado só nessa empresa e não existe busca global por e-mail ([D-088](../00-governance/decision-register.md#d-088--identificação-da-empresa-pelo-endereço-de-acesso), [ADR-012](../adr/ADR-012.md)). Domínio desconhecido, pendente ou desativado não seleciona empresa.
- Row Level Security (RLS) do PostgreSQL foi avaliado formalmente e **não adotado**: [D-003](../00-governance/decision-register.md#d-003--postgresql-row-level-security) (`DECIDIDO — opção B`). Com Prisma (pool de conexões), RLS seguro exigiria envolver toda leitura tenant-scoped em transação — custo de arquitetura e risco de implementação incorreta maiores que o ganho, dado que o filtro obrigatório abaixo já é testado. Reabrir só com evidência nova (ver critério de reavaliação em D-003).
- Testes automatizados obrigatórios de "vazamento entre tenants" fazem parte da definição de pronto de qualquer endpoint (ver [../09-testing/testing-strategy.md](../09-testing/testing-strategy.md)).
- Identificadores de recurso não devem ser previsíveis/sequenciais expostos publicamente sem checagem de tenant (usar UUID — ver [../04-database/database.md](../04-database/database.md)).

## 2. Autenticação e sessão

Decisão completa em [ADR-008](../adr/ADR-008.md) ([D-004](../00-governance/decision-register.md#d-004--estratégia-de-jwt) e [D-005](../00-governance/decision-register.md#d-005--armazenamento-do-refresh-token), `DECIDIDO`).

- **Access token**: JWT com TTL de **15 minutos**, mantido apenas em memória pelo frontend — nunca em `localStorage`/`sessionStorage`.
- **Refresh token**: TTL de **7 dias**, opaco, entregue em **cookie httpOnly** (`Secure: true` em produção) e armazenado com hash no banco (nunca em texto puro).
- **Rotação**: cada uso emite um novo refresh token e invalida o anterior; reuso de um token já rotacionado é tratado como indício de comprometimento e revoga a família de tokens daquele dispositivo.
- **Revogação**: individual (logout de um dispositivo) e global (logout de todos os dispositivos). **Desativar um usuário revoga todas as sessões dele na mesma transação** e a reativação não as restaura ([D-084](../00-governance/decision-register.md#d-084--ciclo-de-vida-da-sessão-usuário-e-tenant-ativos-a-cada-requisição-revogação-na-desativação-e-redação-de-cookies-nos-logs)).
- **Usuário e tenant ativos a cada requisição** ([D-084](../00-governance/decision-register.md#d-084--ciclo-de-vida-da-sessão-usuário-e-tenant-ativos-a-cada-requisição-revogação-na-desativação-e-redação-de-cookies-nos-logs)): a assinatura válida do access token não basta; o `JwtAuthGuard` confirma que o usuário está ativo e que o tenant pode autenticar (`active` ou `trial`, inclusive trial expirado), e o refresh recusa os demais com o mesmo `401` de um token inválido (quais status autenticam: [D-085](../00-governance/decision-register.md#d-085--trial-comercial-modalidade-de-avaliação-por-empresa)). Desativação de usuário e suspensão de tenant bloqueiam o acesso na requisição seguinte, sem esperar os 15 minutos do access token.
- **Suspensão de tenant — o que existe e o que não existe** ([D-084](../00-governance/decision-register.md#d-084--ciclo-de-vida-da-sessão-usuário-e-tenant-ativos-a-cada-requisição-revogação-na-desativação-e-redação-de-cookies-nos-logs), limitações aceitas):
  - A suspensão bloqueia o acesso **enquanto o status do tenant for `suspended`** (login, refresh e acesso por token). `trial` não é suspensão: ver "Trial comercial" abaixo.
  - Durante a suspensão o `JwtAuthGuard` recusa os access tokens (`401`).
  - Um refresh token **apresentado** durante a suspensão é recusado e **revoga as sessões daquele usuário** no banco.
  - A suspensão **manual** (direto no banco, D-059) **não revoga imediatamente todas as sessões do tenant**: não há revogação global por tenant, e **não se promete revogação imediata global**. Sessões de usuários que não tentaram renovar durante a suspensão continuam sem revogação e **podem continuar válidas após a reativação**, por no máximo 7 dias desde a emissão ou a última rotação do refresh token.
  - **Limitação residual de até 15 minutos:** um access token emitido antes de uma desativação de usuário ou de uma suspensão de tenant volta a ser aceito se o usuário/tenant for reativado dentro da validade do token. O refresh token revogado pela desativação do usuário não volta.
  - Melhorias futuras, **não implementadas**: invalidação de access tokens por usuário (`session_version`/`sessions_invalid_before`), `revokeAllForTenant` e rotina/endpoint de suspensão e reativação de tenant.
- **Identidade visual por tenant** ([D-086](../00-governance/decision-register.md#d-086--identidade-visual-executive-e-personalização-visual-por-tenant), [ADR-011](../adr/ADR-011.md)): o backend valida formato (`#RRGGBB`, tema da lista, nome em texto puro) e contraste antes de gravar; nenhum campo aceita CSS, HTML, JavaScript ou URL, e campo não previsto devolve 400. A identidade é do tenant do token; o frontend limpa as variáveis ao fim de cada sessão. Aplicar é operação da plataforma (`branding:manage`, reservada, como `plan:convert`); o Admin do tenant só solicita (`branding:request`, exclusiva do papel Admin) e a API de papéis não concede nenhuma das duas. Logotipo e favicon dependem de upload seguro, que não existe.
- **Trial comercial** ([D-085](../00-governance/decision-register.md#d-085--trial-comercial-modalidade-de-avaliação-por-empresa), [ADR-010](../adr/ADR-010.md)): trial expirado autentica e consulta, mas não escreve. O bloqueio é do backend (`403 TRIAL_EXPIRED`, `TRIAL_NOT_STARTED`, `PLAN_LIMIT_REACHED`, `FEATURE_NOT_AVAILABLE`), não encerra a sessão e é fechado por padrão: todo método que não é GET é escrita, salvo isenção explícita. Limites são validados sob lock na transação da criação. Situação e consumo são sempre do tenant do token; nenhuma rota aceita outro tenant. `plan:convert` é reservada: nenhum papel de fábrica a recebe e a API de papéis não a concede, para que o Admin do tenant não troque o próprio plano. Ocultar botões é só UX.
- **Sessão presa ao endereço da empresa** ([D-088](../00-governance/decision-register.md#d-088--identificação-da-empresa-pelo-endereço-de-acesso)): o refresh só renova no endereço da própria empresa; um access token apresentado no endereço de outra empresa recebe `401`; o cookie do refresh é host-only. E-mail inexistente e senha errada têm a mesma resposta e o mesmo custo de verificação.
- Senhas com hash **bcrypt** ou **argon2** (custo configurável), nunca reversível.
- Rate limiting específico em endpoints de autenticação (login, reset de senha) para mitigar força bruta.

## 3. Autorização (RBAC)

- Toda ação de escrita e leitura sensível passa pela cadeia: autenticação → tenant do recurso == tenant do usuário → permissão do papel → escopo de dado (ver [../02-business/business-rules.md](../02-business/business-rules.md) BR-25).
- Implementado no backend via **Guards** (autenticação/tenant) + **Policies** (permissão/escopo) — ver [../07-backend/backend-architecture.md](../07-backend/backend-architecture.md).
- Falha de permissão em recurso que o usuário não pode nem saber que existe retorna 404 (não 403), para não vazar existência de dado (BR-26).
- **Concessão de acesso** ([D-087](../00-governance/decision-register.md#d-087--concessão-de-papéis-privilegiados-e-proteção-do-último-admin)): ninguém concede papel com permissão que não tem, nem define papel acima do próprio acesso; conceder ou retirar o papel de fábrica `admin` exige ser Admin (`users:update` e `roles:manage` não bastam); alterar ou desativar um usuário exige cobrir as permissões dele. As permissões reservadas à plataforma nunca são concedidas pelo tenant, mas podem ser retiradas por ele.
- **Último Admin** ([D-087](../00-governance/decision-register.md#d-087--concessão-de-papéis-privilegiados-e-proteção-do-último-admin)): o tenant mantém sempre ao menos um Admin ativo (`409 LAST_ADMIN`). Mudanças de papéis e de situação de usuário e definições de papel correm sob lock por tenant, com as verificações na mesma transação da gravação.

## 4. Transporte e API

- HTTPS/WSS obrigatório em todos os ambientes exceto desenvolvimento local (RNF-07).
- CORS restrito às origens conhecidas do `crm-frontend` (por ambiente).
- CSRF: as chamadas de API autenticadas usam Bearer token (não cookie), o que mantém o risco de CSRF baixo na maior parte da superfície. O refresh token vai em cookie httpOnly ([D-005](../00-governance/decision-register.md#d-005--armazenamento-do-refresh-token)), então `/auth/refresh` é a única rota exposta a CSRF — coberta com `SameSite=Lax` e sem token anti-CSRF adicional, justificado pela topologia same-site já definida em [deployment.md](../08-devops/deployment.md) ([D-006](../00-governance/decision-register.md#d-006--topologia-de-domínio-samesite-e-csrf), `DECIDIDO`). Se o deploy migrar para cross-site no futuro, essa decisão precisa ser reaberta e proteção CSRF explícita passa a ser **obrigatória**.
- Validação de entrada em 100% dos endpoints (DTO + schema, ver [../05-api/api-guidelines.md](../05-api/api-guidelines.md)); sanitização de campos livres (notas, mensagens) antes de renderização no frontend (proteção XSS).
- Rate limiting geral por tenant/usuário/IP para proteger contra abuso.

## 5. Dados sensíveis e criptografia

- Segredos (credenciais de provedores de telefonia/WhatsApp, chaves) nunca em texto puro no banco — criptografados em repouso ou armazenados em cofre de segredos ([D-025](../00-governance/decision-register.md#d-025--secrets-management-em-produção), `PROPOSTO`: variáveis de ambiente da plataforma de deploy no início, cofre dedicado quando as integrações crescerem — resolver antes da Fase 5, ver [../08-devops/deployment.md](../08-devops/deployment.md)).
- Dados pessoais sensíveis (quando aplicável) tratados conforme LGPD — ver seção 7.
- Backups seguem a mesma política de isolamento e criptografia dos dados originais.

## 6. Upload de arquivos

- Validação de tipo (allowlist de MIME types) e tamanho máximo antes de aceitar upload.
- Armazenamento fora da árvore servida diretamente pela aplicação; acesso via URL assinada de curta duração, nunca path direto no disco público.
- Nenhum arquivo enviado por usuário é executável/interpretável pelo servidor.

## 7. Webhooks

- Todo webhook recebido de provedor externo é validado por assinatura/segredo compartilhado antes de processado.
- Processamento idempotente por identificador externo do evento (BR-20).
- Payload de webhook é persistido bruto antes do processamento, permitindo reprocessamento em caso de falha de parsing/regra.

## 8. Auditoria

- Toda criação/edição/exclusão de dado sensível e toda ação administrativa (mudança de papel, configuração de integração) gera registro de auditoria imutável (BR-23/BR-24).
- Log de auditoria inclui: tenant, usuário, ação, entidade/id, timestamp, e contexto relevante (não senha/segredo).

## 9. LGPD

- O sistema deve ser capaz de, por titular de dado (contato/cliente): consultar quais dados existem, corrigir, e processar solicitação de exclusão (respeitando obrigações legais de retenção, ex. fiscais).
- Exclusão de titular é sempre auditada e, quando não puder ser física por obrigação legal, é anonimizada.
- O fluxo operacional de atendimento a solicitações de titular (self-service vs. processo manual assistido) é `[VALIDAÇÃO DE NEGÓCIO NECESSÁRIA]` — [D-047](../00-governance/decision-register.md#d-047--fluxo-operacional-de-lgpd-titular-de-dados), a resolver antes do primeiro cliente em produção. Não bloqueia o MVP: o modelo de dados (soft delete + auditoria) já suporta ambos os caminhos.

## 10. Princípio geral

Nenhum mecanismo inseguro deve ser implementado "para facilitar o desenvolvimento" (ex.: desabilitar checagem de tenant em ambiente de dev de forma que vaze para produção, guardar segredo em `.env` versionado). Qualquer atalho de segurança usado apenas localmente deve estar claramente isolado por configuração de ambiente e nunca ser o padrão.
