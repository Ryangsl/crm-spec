# MAT-SEC-TENANT-001 — Template: isolamento entre tenants para entidade nova

**Isto não é um MAT executável — é o padrão que todo MAT de uma entidade tenant-scoped nova
deve seguir.** Nasceu de [MAT-007](MAT-007-tenant-isolation.md) (usuários). Não criar todos os
MATs futuros agora — criar o MAT correspondente **quando a entidade for implementada**,
copiando esta estrutura.

## Quando usar

Para **toda** entidade nova que tenha `tenant_id` — hoje isso significa, no roadmap: Customers,
Leads, Opportunities, Tasks, Notes, Interactions, Conversations, Messages, Calls, e qualquer
outra que vier depois. Se a entidade tem `tenant_id`, ela precisa de um
`MAT-XXX-<entidade>-isolation.md` seguindo este padrão antes da fase que a introduz ser
fechada.

## Passos obrigatórios (adaptar para os verbos que a entidade realmente expõe)

1. Criar o recurso no **Tenant A** (via usuário autenticado de A, nunca inserção direta no
   banco — a criação em si também precisa ser exercitada pela API).
2. Autenticar como usuário do **Tenant B** (com a permissão equivalente concedida — o teste é
   sobre isolamento de tenant, não sobre RBAC; garantir que B *teria* permissão se o recurso
   fosse dele).
3. Tentar, com o token de B, contra o recurso criado por A:
   - `GET /recurso/{id}` (leitura direta por id)
   - `GET /recurso` (listagem — confirmar que o recurso de A não aparece)
   - `PATCH /recurso/{id}` (ou o verbo de atualização equivalente)
   - `DELETE /recurso/{id}` (ou o verbo de exclusão/desativação equivalente)
   - Qualquer rota de **ação de negócio** específica da entidade (ex.: `POST
     /opportunities/{id}/win`, `POST /leads/{id}/convert`) — toda ação, não só CRUD genérico.
4. Conferir no banco que nenhuma tentativa alterou o recurso de A.
5. Tentar **criar** um recurso novo com o token de B forjando o `tenant_id` de A no corpo
   (campo não deve existir no DTO — a requisição deve ser rejeitada pela validação, não
   silenciosamente ignorada).

## Resultado esperado (padrão)

- ✓ Toda tentativa de leitura/escrita/ação de B contra o recurso de A: `404`.
- ✓ Listagem de B nunca contém o recurso de A.
- ✓ Criação por B sempre cai no tenant de B, mesmo que o payload tente indicar outro `tenant_id`.
- ✓ Nenhuma alteração no recurso de A após qualquer tentativa.

## Resultado que NUNCA deve acontecer (padrão)

- ✗ `200`/`204` em qualquer tentativa cross-tenant.
- ✗ `403` em vez de `404` (vaza a existência do recurso — BR-26).
- ✗ Qualquer campo do recurso de A aparecendo em uma resposta para B.
- ✗ `500` em vez de um código de erro tratado.

## Evidência mínima exigida

Resposta HTTP completa (status + corpo) de cada tentativa do passo 3, e uma consulta ao banco
confirmando que o recurso de A está intacto. Não é preciso screenshot — é tudo API.

## Referência viva

[MAT-007-tenant-isolation.md](MAT-007-tenant-isolation.md) é a instância já executada deste
padrão para `users`, com evidência real — use como exemplo de formatação ao criar o próximo.
