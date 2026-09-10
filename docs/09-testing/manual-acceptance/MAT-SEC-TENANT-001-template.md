# MAT-SEC-TENANT-001 — Template: isolamento entre tenants para entidade nova

**Isto não é um MAT executável — é o padrão que todo MAT de uma entidade tenant-scoped nova
deve seguir.** Nasceu de [MAT-007](MAT-007-tenant-isolation.md) (usuários). Não criar todos os
MATs futuros agora — criar o MAT correspondente **quando a entidade for implementada**,
copiando esta estrutura e a numeração de seções usada em MAT-001 a MAT-008 (ver
[README.md](README.md) seção "Padrão obrigatório de um MAT").

## Quando usar

Para **toda** entidade nova que tenha `tenant_id` — hoje isso significa, no roadmap: Customers,
Leads, Opportunities, Tasks, Notes, Interactions, Conversations, Messages, Calls, e qualquer
outra que vier depois. Se a entidade tem `tenant_id`, ela precisa de um
`MAT-XXX-<entidade>-isolation.md` seguindo este padrão antes da fase que a introduz ser
fechada.

## Estrutura a copiar

Ao criar o MAT real, usar as 11 seções do padrão (ver README.md): Identificação, Objetivo,
Escopo, Pré-requisitos, Dados de teste, Tutorial de execução manual, Resultado que NÃO deve
acontecer, Resultado da IA — Execução anterior, Validação Manual do Responsável, Critério de
Aceite, Histórico. As seções abaixo dão o conteúdo mínimo obrigatório de cada uma **para o caso
de isolamento entre tenants** especificamente — adaptar os verbos/rotas para a entidade real.

### Tutorial de execução manual — passos obrigatórios

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

Cada um destes 5 pontos vira um ou mais "Passo N" no tutorial real, no formato usado em
MAT-001 a MAT-008 (Ação / Comando / Resultado esperado / O que observar).

### Resultado esperado (padrão)

- ✓ Toda tentativa de leitura/escrita/ação de B contra o recurso de A: `404`.
- ✓ Listagem de B nunca contém o recurso de A.
- ✓ Criação por B sempre cai no tenant de B, mesmo que o payload tente indicar outro `tenant_id`.
- ✓ Nenhuma alteração no recurso de A após qualquer tentativa.

### Resultado que NUNCA deve acontecer (padrão)

- ✗ `200`/`204` em qualquer tentativa cross-tenant.
- ✗ `403` em vez de `404` (vaza a existência do recurso — BR-26).
- ✗ Qualquer campo do recurso de A aparecendo em uma resposta para B.
- ✗ `500` em vez de um código de erro tratado.

### Resultado da IA / Validação Manual / Critério de Aceite

O MAT real, quando criado, começa com a seção "Resultado da IA" **vazia** (ou com a primeira
execução real de quem implementou a entidade) e a seção "Validação Manual do Responsável"
sempre em branco até alguém preencher de fato — nunca herdar ou copiar a execução de outro MAT
para simular uma execução que não aconteceu para aquela entidade especificamente.

### Evidência mínima exigida

Resposta HTTP completa (status + corpo) de cada tentativa do passo 3, e uma consulta ao banco
confirmando que o recurso de A está intacto. Não é preciso screenshot — é tudo API (regra de
evidência proporcional ao risco, ver [README.md](README.md)).

## Referência viva

[MAT-007-tenant-isolation.md](MAT-007-tenant-isolation.md) é a instância já executada deste
padrão para `users`, com evidência real (seção 8) e a estrutura completa das 11 seções — use
como exemplo de formatação ao criar o próximo MAT desta família.
