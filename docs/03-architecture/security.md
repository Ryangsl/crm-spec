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
- Toda query de leitura/escrita passa por uma camada obrigatória que injeta o filtro de `tenant_id` a partir do contexto autenticado — nunca a partir de parâmetro vindo do cliente.
- `[DECISÃO PENDENTE]`: uso de Row Level Security (RLS) do PostgreSQL como camada adicional de defesa (defesa em profundidade) além do filtro na aplicação — recomendado para produção, a confirmar com `crm-backend` na Fase 1/2.
- Testes automatizados obrigatórios de "vazamento entre tenants" fazem parte da definição de pronto de qualquer endpoint (ver [../09-testing/testing-strategy.md](../09-testing/testing-strategy.md)).
- Identificadores de recurso não devem ser previsíveis/sequenciais expostos publicamente sem checagem de tenant (usar UUID — ver [../04-database/database.md](../04-database/database.md)).

## 2. Autenticação e sessão

- **JWT de acesso** de curta duração (`[DECISÃO PENDENTE]`: TTL exato, sugestão inicial 15 min) + **refresh token** de vida mais longa, armazenado com possibilidade de revogação (lista de refresh tokens ativos por usuário/dispositivo).
- Refresh token é opaco e armazenado com hash no banco (nunca em texto puro), permitindo revogação individual (logout de um dispositivo) e global (logout de todos os dispositivos).
- Senhas com hash **bcrypt** ou **argon2** (custo configurável), nunca reversível.
- Rate limiting específico em endpoints de autenticação (login, reset de senha) para mitigar força bruta.

## 3. Autorização (RBAC)

- Toda ação de escrita e leitura sensível passa pela cadeia: autenticação → tenant do recurso == tenant do usuário → permissão do papel → escopo de dado (ver [../02-business/business-rules.md](../02-business/business-rules.md) BR-25).
- Implementado no backend via **Guards** (autenticação/tenant) + **Policies** (permissão/escopo) — ver [../07-backend/backend-architecture.md](../07-backend/backend-architecture.md).
- Falha de permissão em recurso que o usuário não pode nem saber que existe retorna 404 (não 403), para não vazar existência de dado (BR-26).

## 4. Transporte e API

- HTTPS/WSS obrigatório em todos os ambientes exceto desenvolvimento local (RNF-07).
- CORS restrito às origens conhecidas do `crm-frontend` (por ambiente).
- CSRF: como a API é stateless via Bearer token (não cookie de sessão), o risco de CSRF clássico é reduzido; se refresh token for entregue via cookie httpOnly (`[DECISÃO PENDENTE]`), proteção CSRF (SameSite + token) passa a ser obrigatória.
- Validação de entrada em 100% dos endpoints (DTO + schema, ver [../05-api/api-guidelines.md](../05-api/api-guidelines.md)); sanitização de campos livres (notas, mensagens) antes de renderização no frontend (proteção XSS).
- Rate limiting geral por tenant/usuário/IP para proteger contra abuso.

## 5. Dados sensíveis e criptografia

- Segredos (credenciais de provedores de telefonia/WhatsApp, chaves) nunca em texto puro no banco — criptografados em repouso ou armazenados em cofre de segredos (`[DECISÃO PENDENTE]`: solução de secrets management por ambiente, ver [../08-devops/deployment.md](../08-devops/deployment.md)).
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
- `[DECISÃO PENDENTE]`: fluxo operacional completo de atendimento a solicitações LGPD (self-service vs. processo manual assistido) fica para uma fase específica, não bloqueia o MVP, mas o modelo de dados já deve suportar (soft delete + auditoria cobrem a base).

## 10. Princípio geral

Nenhum mecanismo inseguro deve ser implementado "para facilitar o desenvolvimento" (ex.: desabilitar checagem de tenant em ambiente de dev de forma que vaze para produção, guardar segredo em `.env` versionado). Qualquer atalho de segurança usado apenas localmente deve estar claramente isolado por configuração de ambiente e nunca ser o padrão.
