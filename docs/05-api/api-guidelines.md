# Diretrizes de API

Este documento define o contrato entre `crm-frontend` e `crm-backend`. O frontend **não** acessa banco de dados e **não** implementa regra de negócio crítica — toda autoridade de regra é do backend (ver [../03-architecture/architecture.md](../03-architecture/architecture.md)).

## 1. Estilo e versionamento

- **REST** sobre HTTPS, payloads JSON.
- Especificação formal em [openapi.yaml](openapi.yaml) (OpenAPI 3.0) — fonte da verdade do contrato, deve ser mantida atualizada junto com qualquer mudança de endpoint.
- Versionamento por prefixo de URL: `/v1/...`. Uma mudança **incompatível** (remoção de campo, mudança de tipo, mudança de comportamento) exige `/v2`; uma mudança **aditiva** (novo campo opcional) não exige nova versão.
- Nenhum endpoint em produção é alterado de forma incompatível sem nova versão convivendo com a anterior por um período de transição (`[DECISÃO PENDENTE]`: política formal de deprecação/tempo mínimo de convivência).

## 2. Autenticação

- `Authorization: Bearer <access_token>` em toda rota autenticada.
- Renovação via `POST /v1/auth/refresh` com o refresh token.
- Rotas de autenticação (`/v1/auth/*`) não exigem token de acesso, mas têm rate limiting dedicado.

## 3. Multi-tenancy no contrato

- O `tenant_id` **nunca** é enviado como parâmetro pelo cliente — é resolvido no backend a partir do token autenticado. Isso evita que um cliente malicioso tente forjar acesso a outro tenant via parâmetro.
- Qualquer tentativa de acessar recurso de outro tenant retorna 404.

## 4. Paginação, filtros e ordenação

- Listagens usam paginação por cursor: query params `?cursor=<opaco>&limit=<n>` (limit padrão e máximo definidos por endpoint). Resposta inclui `next_cursor` (null quando não há mais páginas).
- Filtros via query params nomeados (`?status=open&owner_id=...`); múltiplos filtros são combinados com AND.
- Ordenação via `?sort=field` / `?sort=-field` (prefixo `-` = descendente); campos ordenáveis são explícitos por endpoint (não qualquer campo).

## 5. Códigos HTTP

| Código | Uso |
|---|---|
| 200 | Sucesso (leitura/atualização) |
| 201 | Criação com sucesso |
| 204 | Sucesso sem corpo (ex.: exclusão lógica) |
| 400 | Erro de validação de entrada |
| 401 | Não autenticado / token inválido ou expirado |
| 403 | Autenticado, mas sem permissão para uma ação sobre um recurso cuja existência é conhecida ao usuário |
| 404 | Recurso não encontrado **ou** pertence a outro tenant/escopo (ver seção 3 e BR-26) |
| 409 | Conflito (ex.: violação de regra de estado, duplicidade) |
| 422 | Entidade válida sintaticamente, mas viola regra de negócio |
| 429 | Rate limit excedido |
| 500 | Erro interno não tratado |

## 6. Formato de erro padronizado

```json
{
  "error": {
    "code": "LEAD_ALREADY_CONVERTED",
    "message": "Este lead já foi convertido em oportunidade.",
    "details": []
  }
}
```

- `code`: string estável, machine-readable, usada pelo frontend para tratamento específico quando necessário.
- `message`: mensagem amigável (pt-BR), não é a fonte de verdade para lógica do frontend.
- `details`: opcional, lista de erros de campo em validações (`[{ "field": "email", "issue": "invalid_format" }]`).

## 7. DTOs e schemas

- Todo endpoint tem um DTO de entrada validado (schema, ver [../07-backend/backend-architecture.md](../07-backend/backend-architecture.md)) e um schema de saída documentado no OpenAPI.
- Campos de saída nunca incluem dados internos sensíveis (hash de senha, segredos de integração).
- Datas em ISO 8601 UTC; o frontend converte para o timezone do usuário.

## 8. Idempotência

- Endpoints de efeito colateral externo relevante (ex.: originar chamada, enviar mensagem) aceitam um header `Idempotency-Key` opcional; reenvio com a mesma chave não duplica o efeito.

## 9. Exemplos de contrato (ilustrativos — ver detalhamento completo em [openapi.yaml](openapi.yaml))

### Login
`POST /v1/auth/login`
```json
// Request
{ "email": "user@empresa.com", "password": "•••••" }
// Response 200
{ "access_token": "...", "refresh_token": "...", "expires_in": 900 }
```

### Usuários
`GET /v1/users?cursor=...&limit=20`
`POST /v1/users` → 201 com o usuário criado.

### Clientes
`GET /v1/customers/{id}`
`POST /v1/customers`

### Leads
`POST /v1/leads`
`POST /v1/leads/{id}/qualify`
`POST /v1/leads/{id}/disqualify` `{ "reason": "..." }`
`POST /v1/leads/{id}/convert` → cria/retorna a Oportunidade vinculada.

### Oportunidades / Pipeline
`GET /v1/pipelines/{id}/opportunities?stage_id=...`
`POST /v1/opportunities/{id}/move` `{ "stage_id": "..." }`
`POST /v1/opportunities/{id}/win`
`POST /v1/opportunities/{id}/lose` `{ "reason": "..." }`

### Atendimentos / Ligações
`POST /v1/calls/click-to-call` `{ "customer_id": "...", "phone": "..." }`
`POST /v1/calls/{id}/disposition` `{ "disposition_id": "..." }`
`GET /v1/customers/{id}/interactions?cursor=...`

## 10. O que o frontend nunca faz

- Nunca calcula regra de negócio que decide estado (ex.: se um lead pode ser convertido, se uma oportunidade pode mudar de etapa) — apenas envia a intenção e trata a resposta (sucesso ou erro de regra, 409/422).
- Nunca monta query SQL ou acessa qualquer armazenamento além do que a API expõe.
- Nunca confia em dado sensível vindo apenas do estado local sem revalidação do backend (ex.: permissão de um botão aparecer é UX, a ação em si é sempre revalidada no servidor).
