# Runbook — acesso das empresas existentes a Disponibilidade, Interações e Conversas

> **Estado**: escrito e **testado só em banco descartável local** (13/11/2026). **Nunca foi executado em ambiente real.** A aplicação em empresa real exige autorização explícita do responsável, backup recente com restore testado e janela combinada. Regras de política adotadas aqui: [D-100](../00-governance/decision-register.md#d-100--regularização-de-acesso-das-empresas-existentes-regras-do-passo) (`PROPOSTO`).

Cobre o que o [runbook do F4.7](runbook-f4-7-tenant-roles.md) deixou de fora: `availability` (F4.2), `interactions` (F4.4) e `conversations` (F4.6) nas empresas criadas antes desses incrementos. Mesmo princípio dos outros passos manuais de dados ([D-059](../00-governance/decision-register.md#d-059--provisionamento-de-tenant-permanece-manual-fase-2)): nunca o `seed.ts` completo em ambiente real.

## 1. O que cada recurso é (levantado no código em 13/11/2026)

| Recurso | Como é registrado | Como a aplicação verifica | Plano | Configuração da empresa |
|---|---|---|---|---|
| `availability` | 3 permissões de papel (`availability:read`, `:update`, `:manage`) | `@RequirePermissions` e, em `PUT /availability/me`, `update` **ou** `manage` no service | não controla | `crm.availability.enabled` em `tenant_settings`: ausente ou `false` = mecanismo desligado ([D-071](../00-governance/decision-register.md#d-071--disponibilidade-de-consultoratendente-para-distribuição-automática)). Só o Admin altera, pela tela |
| `interactions` | 3 permissões (`interactions:create`, `:read`, `:delete`) | `@RequirePermissions` | não controla | nenhuma |
| `conversations` | 4 permissões (`conversations:create`, `:read`, `:update`, `:assign`) | `@RequirePermissions` **e** `@RequiresFeature('conversations')` | funcionalidade `conversations` do plano: desligada, bloqueia a **escrita** (`403 FEATURE_NOT_AVAILABLE`); a leitura continua | nenhuma |

- **Empresa nova** recebe as 10 permissões nos papéis de fábrica por `seedTenantRoles` (`npm run tenant:provision-trial` e seed de desenvolvimento). O catálogo global `permissions` só é preenchido por esse mesmo caminho: nenhuma migration insere permissão.
- **Empresa existente** nunca recebeu as concessões (o seed só afeta empresas novas) e, se nenhuma empresa foi provisionada depois do F4.6 naquele banco, o catálogo global também não tem as 10 chaves.
- **Plano ≠ papel**: Trial tem `conversations` ligada; plano legado (sem `code`) libera tudo o que existe; plano com `code` e sem a funcionalidade bloqueia a escrita em Conversas. O provisionamento concede os papéis sem olhar o plano, e este passo faz o mesmo: **lê e relata** o plano, nunca o altera.
- **`crm.availability.enabled`**: o provisionamento de empresa nova (`tenant:provision-trial`) **não** grava a chave (só o seed de desenvolvimento liga a "Empresa Exemplo"). Este passo **lê e relata**, nunca grava: ligar a disponibilidade é decisão do Admin (Configurações > Disponibilidade).

## 2. O que é concedido

Só as permissões do escopo que `FACTORY_ROLES` (`crm-backend/prisma/tenant-roles.ts`, fonte única) prevê para cada papel de fábrica e que estiverem faltando. Numa empresa sem nenhuma delas: **42 concessões em 8 papéis**.

| Papel de fábrica | `conversations` | `interactions` | `availability` | Total |
|---|---|---|---|:---:|
| `admin` | create, read, update, assign | create, read, delete | read, update, manage | 10 |
| `diretor` | read | read | read | 3 |
| `gerente` | create, read, update, assign | create, read, delete | read, manage | 9 |
| `supervisor` | read | read | read | 3 |
| `vendedor` | create, read, update | create, read | update | 6 |
| `operador` | create, read, update | create, read | — | 5 |
| `backoffice` | read | create, read | update | 4 |
| `leitura` | read | read | — | 2 |

Regras do passo:

- **Só acrescenta.** Nunca remove concessão, nunca altera papel personalizado, usuário, plano, configuração ou situação da empresa.
- Papel de fábrica que diverge da fábrica **fora do escopo** (permissão a mais, ou a menos, por edição manual ou por outro runbook ainda não executado, como o do F4.7) é **preservado como está**: recebe só o que falta no escopo e aparece no relatório como "personalizado/divergente".
- Nenhuma permissão reservada à plataforma (`plan:convert`, `branding:manage`) está no escopo; nenhum papel recebe mais do que a fábrica define para ele.
- Depois de aplicar numa empresa "antiga" sem divergências, os papéis de fábrica ficam com o mesmo conjunto do escopo de uma empresa nova.

## 3. Comando

```bash
# Simulação (padrão): não grava nada
npm run tenant:regularize-access -- --database-url-env DATABASE_URL
npm run tenant:regularize-access -- --database-url-env DATABASE_URL --tenant <id-da-empresa> --json

# Aplicação
npm run tenant:regularize-access -- --database-url-env DATABASE_URL --apply \
  --confirm-database <nome-do-banco> --operator "<quem executa>"
```

| Opção | Efeito |
|---|---|
| `--database-url-env <NOME>` | **Obrigatória.** Nome da variável de ambiente com a URL do banco. Nenhum banco é escolhido por padrão; o cabeçalho mostra host, porta e banco, nunca usuário ou senha |
| `--tenant <id>` | Restringe a uma empresa (id inexistente = erro, nada gravado) |
| `--json` | Relatório completo em JSON (inclui `database`), para guardar como evidência |
| `--apply` | Grava. Sem ela, é sempre simulação |
| `--confirm-database <nome>` | Obrigatória com `--apply`: precisa ser igual ao nome do banco da URL |
| `--operator "<nome>"` | Obrigatória com `--apply`: vai para a auditoria |
| `--include-suspended` | Inclui empresas suspensas na aplicação (seção 5) |
| `--create-missing-permissions` | Cria no catálogo global as permissões do escopo que faltarem (seção 5) |
| `--i-have-a-backup --allow-remote-host <host>` | As duas são obrigatórias para aplicar em banco fora da máquina; o host precisa ser igual ao da URL |

Argumento desconhecido é erro (um `--aply` digitado errado não vira simulação silenciosa de outra coisa).

## 4. Simulação e leitura do relatório

A simulação roda inteira numa transação `REPEATABLE READ` **somente leitura** (`SET TRANSACTION READ ONLY`): o próprio PostgreSQL recusa qualquer escrita. Ela usa a mesma função de avaliação da aplicação e as mesmas opções, então mostra exatamente o que a aplicação faria.

- **Catálogo global**: permissões do escopo ausentes de `permissions` e se seriam criadas.
- **Resumo**: empresas avaliadas; já conformes; a atualizar; ignoradas; inconsistências; alterações estimadas (pares papel × permissão, só das empresas "a atualizar"); papéis de fábrica divergentes preservados; empresas com `crm.availability.enabled` definido (preservado).
- **Por empresa**: situação, plano (e se inclui Conversas), valor de `crm.availability.enabled`, papéis personalizados intocados, motivos (`MOTIVO [código]`), avisos (`AVISO [código]`) e, por papel, o que será concedido e o que foi preservado.

| Resultado | Significado |
|---|---|
| conforme | nada a conceder |
| a atualizar / atualizada | receberá / recebeu as concessões listadas |
| ignorada | `tenant_deleted` (excluída logicamente: nunca avaliada nem alterada) ou `tenant_suspended` (seção 5) |
| inconsistência | **nada é gravado na empresa**: `duplicate_factory_role` (dois papéis de sistema com o mesmo nome de fábrica, ex.: `gerente` e `Gerente`), `no_factory_roles` (papéis não são criados aqui), `catalog_permission_missing` (seção 5) |
| falhou | erro durante a aplicação; a transação da empresa foi desfeita inteira, as outras seguem; o comando sai com código 1 |

Avisos não impedem a regularização dos demais papéis: `factory_role_missing`, `factory_role_deleted` (não é restaurado), `factory_name_on_custom_role`, `factory_role_name_variant`, `unknown_system_role` (papel de sistema que não é de fábrica: intocado), `unknown_permission_on_role` (chave fora do catálogo do código: preservada).

## 5. Regras de política ([D-100](../00-governance/decision-register.md#d-100--regularização-de-acesso-das-empresas-existentes-regras-do-passo), `PROPOSTO`)

- **Empresa suspensa**: simulada e listada com o que falta, mas **ignorada** na aplicação sem `--include-suspended`. Motivo: ninguém dela autentica enquanto suspensa, então não há urgência, e alterar dado de empresa suspensa deve ser um ato deliberado. Suspensa e já conforme conta como conforme. Trial (inclusive expirado) é tratado como ativa, porque autentica.
- **Catálogo global incompleto**: sem `--create-missing-permissions`, a empresa que depende de uma chave ausente é inconsistência. Com a opção, as chaves são criadas antes das empresas (linhas sem empresa, que sozinhas não dão acesso a ninguém; UUID v7). É a única escrita que não é por empresa e a única sem linha de auditoria (`audit_log` exige empresa); fica registrada no relatório (`catalog.created`).
- **Inconsistência estrutural** nunca é corrigida aqui: é resolvida manualmente, caso a caso, e o passo é executado de novo.

## 6. Aplicação: pré-requisitos e garantias

Pré-requisitos (ambiente real):

1. Autorização explícita do responsável para o ambiente e para a lista de empresas; **backup recente e restore testado** (D-028/D-029); janela fora do horário de uso.
2. `prisma migrate deploy` já aplicado (etapa separada; este passo não cria nem altera tabela).
3. Simulação com `--json` guardada como linha de base e **revisada**: empresas a atualizar, divergências, inconsistências, e o plano de quem não inclui Conversas.
4. Execução de uma estação de operação, com a URL numa variável de ambiente (nunca em arquivo versionado, nota ou histórico compartilhado). Recomenda-se uma empresa por vez (`--tenant`) na primeira execução real.

Travas e garantias:

| Garantia | Como |
|---|---|
| Nunca grava por engano | simulação é o padrão; `--apply` exige `--confirm-database` igual ao banco e `--operator` |
| Nunca roda de dentro da aplicação em produção | `--apply` recusa `NODE_ENV=production` |
| Host remoto é deliberado | exige `--i-have-a-backup` **e** `--allow-remote-host <host>` igual ao da URL |
| Tudo ou nada por empresa | uma transação por empresa; erro desfaz as concessões e a auditoria dela |
| Sem corrida com a aplicação | mesmo advisory lock das mudanças de papel ([D-087](../00-governance/decision-register.md#d-087--concessão-de-papéis-privilegiados-e-proteção-do-último-admin)); a avaliação é refeita dentro da transação, sob o lock |
| Auditável | uma linha em `audit_log` por papel alterado (`role.permissions_regularized`, `entity_type = role`, sem usuário; `payload` com `operator`, `role` e `granted_permission_keys`), na mesma transação |
| Idempotente | a segunda execução não encontra o que conceder: zero concessões, zero auditoria |
| Isolada | `--tenant A` não lê nem grava nada da empresa B |

Depois de aplicar: rodar a simulação de novo (esperado: empresa conforme, 0 alterações) e validar por API com uma conta de teste da empresa (`GET /v1/conversations` e `GET /v1/availability` com o Gerente: `200`). As permissões valem na requisição seguinte; quem já está logado não precisa sair. O frontend mostra os itens de menu conforme as permissões.

## 7. Como reverter

As concessões são aditivas e não tiram acesso de ninguém; a reversão só faz sentido se a empresa não devia ter recebido. Com autorização, remove **exatamente** o que a auditoria registra para a empresa (concessão que já existia antes não é tocada):

```sql
BEGIN;
DELETE FROM role_permissions rp
USING audit_log a, permissions p
WHERE a.tenant_id = :'tenant_id'
  AND a.action = 'role.permissions_regularized'
  AND rp.role_id = a.entity_id
  AND p.id = rp.permission_id
  AND a.payload->'granted_permission_keys' ? p.key;
-- conferir a contagem com "Alterações gravadas" do relatório antes do COMMIT
COMMIT;
```

O catálogo global não precisa ser revertido. As linhas de `audit_log` não são apagadas. Se a mesma permissão tiver sido concedida depois por outro caminho, avalie antes: o SQL a removeria.

## 8. Como foi testado (13/11/2026, banco descartável local `crm_ci_test`)

`test/e2e/tenant-access-regularization.e2e-spec.ts` no crm-backend (roda no job de e2e do CI): **33 testes, 33 aprovados**.

- **Estado × esperado**: empresa nova pelo caminho normal sai conforme (0 alterações, 8 papéis, sem avisos); empresa sem nada: 42 concessões, por papel iguais à fábrica; com um ou dois recursos: só o que falta.
- **Aplicação**: concede exatamente o que a simulação mostrou (42 linhas, 8 de auditoria); segunda execução com contagem e hash das tabelas idênticos; papel de fábrica personalizado preserva extras e ausências fora do escopo; papel personalizado e `user_roles` intocados; nenhuma linha removida; `--tenant A` não muda B; falha forçada na auditoria de uma empresa desfaz só a dela; espera o lock de mudança de papéis; pela API, o Gerente passa de `403` para `200` em Conversas e Disponibilidade; o SQL de reversão da seção 7 devolve `role_permissions` ao hash anterior.
- **Não corrigidas em silêncio**: suspensa (ignorada; com a opção, atualizada e continua suspensa), suspensa conforme, excluída logicamente, trial expirado, papel de fábrica duplicado, sem papéis de fábrica, papel ausente/excluído/nome de fábrica em papel personalizado/papel de sistema desconhecido, catálogo incompleto (com e sem a opção; UUID v7), chave fora do catálogo do código.
- **Plano e configuração**: Trial, legado sem código e pago sem Conversas recebem o mesmo plano de concessões; tabela `plans` com hash idêntico; `crm.availability.enabled` ligado, desligado e ausente preservados.
- **A simulação não escreve**: contagem e hash de `role_permissions`, `permissions`, `roles`, `user_roles`, `users`, `audit_log`, `tenant_settings`, `tenants` e `plans` iguais antes e depois, com todos os tipos de empresa e com todas as opções; escrita tentada dentro da transação da simulação é recusada pelo banco.
- **Linha de comando**: recusa sem `--database-url-env`, variável ausente, argumento desconhecido, `NODE_ENV=production`, sem confirmação, confirmação errada, sem operador e host remoto sem as duas confirmações, sempre sem abrir conexão; saída sem usuário nem senha; `--json`; aplicação confirmada no banco de teste e repetição sem alteração.
- Áreas vizinhas: `rbac-tenant-domains` e `tenant-catalogs` continuam verdes (63/63 com a suíte nova na primeira execução); unitários 460/460; lint e `tsc` OK. A CLI real foi executada localmente **só em simulação**, contra `crm_ci_test` e `crm_dev` (2 empresas do seed: conformes, 0 alterações).

**Não testado**: execução em ambiente real ou com dados reais; volume grande de empresas (a simulação lê empresa por empresa numa transação com limite de 10 min); a suíte e2e completa (roda no CI); a CLI com o motor padrão do Prisma (localmente o motor não baixa: os testes usam o cliente da aplicação e a execução manual usou um adaptador local, fora do repositório); validação funcional manual e MATs.
