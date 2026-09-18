# Diretrizes de API

Este documento define o contrato entre `crm-frontend` e `crm-backend`. O frontend **não** acessa banco de dados e **não** implementa regra de negócio crítica — toda autoridade de regra é do backend (ver [../03-architecture/architecture.md](../03-architecture/architecture.md)).

## 1. Estilo e versionamento

- **REST** sobre HTTPS, payloads JSON.
- Especificação formal em [openapi.yaml](openapi.yaml) (OpenAPI 3.0) — fonte da verdade do contrato, deve ser mantida atualizada junto com qualquer mudança de endpoint.
- Versionamento por prefixo de URL: `/v1/...`. Uma mudança **incompatível** (remoção de campo, mudança de tipo, mudança de comportamento) exige `/v2`; uma mudança **aditiva** (novo campo opcional) não exige nova versão.
- Nenhum endpoint em produção é alterado de forma incompatível sem nova versão convivendo com a anterior por um período de transição ([D-030](../00-governance/decision-register.md#d-030--política-de-deprecação-de-versão-de-api), `ADIADO`: o tempo mínimo formal de convivência se define antes da primeira `/v2`; não há consumidor externo nem segunda versão no horizonte).

## 2. Autenticação

Ver [ADR-008](../adr/ADR-008.md) para a decisão completa.

- `Authorization: Bearer <access_token>` em toda rota autenticada. Access token com TTL de **15 minutos**, mantido apenas em memória pelo frontend — nunca em `localStorage`.
- Renovação via `POST /v1/auth/refresh`: o refresh token trafega em **cookie httpOnly** (`Path=/v1/auth`, `Secure` em produção), não no corpo da requisição. TTL de 7 dias, com rotação a cada uso. Reapresentar um token já rotacionado revoga todas as sessões do usuário (D-056).
- `POST /v1/auth/logout` encerra só a sessão atual; `POST /v1/auth/logout-all` encerra todas (D-057). Nenhum dos dois exige access token válido — identificam o usuário pelo próprio refresh token do cookie.
- Rotas de autenticação (`/v1/auth/*`) não exigem token de acesso, mas têm rate limiting dedicado.
- Topologia de deploy é same-site (proxy único na frente de API e frontend — [deployment.md](../08-devops/deployment.md) §2), então `SameSite=Lax` já mitiga CSRF sem token adicional ([D-006](../00-governance/decision-register.md#d-006--topologia-de-domínio-samesite-e-csrf), `DECIDIDO`).

## 3. Multi-tenancy no contrato

- O `tenant_id` **nunca** é enviado como parâmetro pelo cliente — é resolvido no backend a partir do token autenticado. Isso evita que um cliente malicioso tente forjar acesso a outro tenant via parâmetro.
- Qualquer tentativa de acessar recurso de outro tenant retorna 404.

## 4. Paginação, filtros e ordenação

Paginação **híbrida** ([D-007](../00-governance/decision-register.md#d-007--estratégia-de-paginação), `DECIDIDO`) — a estratégia é escolhida por recurso, não por endpoint individual:

| Estratégia | Recursos | Contrato |
|---|---|---|
| **Offset** | Administrativos de volume moderado: usuários, clientes, leads, oportunidades, pipelines, configurações | `?page=1&limit=20` → resposta com `data`, `page`, `limit`, `total` |
| **Cursor** | Cronológicos ou potencialmente volumosos: mensagens, interações, eventos, chamadas, logs, histórico de atividades | `?cursor=<uuid>&limit=20` → resposta com `data` e `next_cursor` (null na última página) |

O cursor é o UUID v7 do último item da página ([D-001](../00-governance/decision-register.md#d-001--estratégia-de-identificador-primário)), que é monotonicamente crescente e dispensa cursor opaco codificado. `limit` tem padrão 20 e máximo 100. Não construir abstração genérica que unifique as duas estratégias antes de haver necessidade real.
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
// Response 200 — refresh token vai em cookie httpOnly, nunca no corpo
{ "access_token": "...", "expires_in": 900 }
```

### Usuários (offset — recurso administrativo)
`GET /v1/users?page=1&limit=20`
`GET /v1/users/{id}` · `GET /v1/users/me`
`POST /v1/users` → 201 com o usuário criado.
`PATCH /v1/users/{id}` → nome e/ou `role_ids` (ausente = não mexe; presente = substitui o conjunto inteiro).
`DELETE /v1/users/{id}` → 204, desativação lógica (`status=inactive`), não remove o registro.

### Clientes (offset)
`GET /v1/customers?page=1&limit=20`
`GET /v1/customers/{id}`
`POST /v1/customers`
`GET/POST /v1/customers/{id}/contacts` — Contacts é sub-recurso de Customer, sem módulo próprio ([D-065](../00-governance/decision-register.md#d-065--contacts-sub-recurso-de-customer-não-módulo-próprio), `DECIDIDO`).

### Leads (offset)
`GET /v1/leads?page=1&limit=20` · `GET /v1/leads/{id}` · `PATCH /v1/leads/{id}` · `DELETE /v1/leads/{id}`
`POST /v1/leads`
`POST /v1/leads/{id}/qualify`
`POST /v1/leads/{id}/disqualify` `{ "reason": "..." }`
`POST /v1/leads/{id}/reopen` — D-033: só a partir de `disqualified`, reabre o mesmo registro.
`POST /v1/leads/{id}/convert` `{ "customer_id": "..." }` ou `{ "customer": { ... } }` → vincula/cria o Cliente (BR-04/BR-08) e marca o lead `converted`. **Fase 3.4**: não cria Oportunidade — fica para a Fase 3.5.

### Lead Sources (offset)
`GET /v1/lead-sources?page=1&limit=20` · `GET/POST /v1/lead-sources` · `PATCH/DELETE /v1/lead-sources/{id}`

### Oportunidades / Pipeline
`GET /v1/pipelines/{id}/opportunities?stage_id=...`
`POST /v1/opportunities/{id}/move` `{ "stage_id": "...", "justification": "..." }` — `justification` é obrigatório quando a movimentação pula uma ou mais etapas ([D-032](../00-governance/decision-register.md#d-032--ordem-de-movimentação-entre-etapas-do-pipeline), `DECIDIDO`).
`POST /v1/opportunities/{id}/win`
`POST /v1/opportunities/{id}/lose` `{ "reason": "..." }`

### Atendimentos / Ligações
`GET /v1/customers/{id}/interactions?cursor=...&limit=20` (cursor — recurso cronológico)
`POST /v1/calls/{id}/disposition` `{ "disposition_id": "..." }`
`POST /v1/calls/click-to-call` `{ "customer_id": "...", "phone": "..." }` — **Fase 5**, depende do provedor de telefonia ([D-010](../00-governance/decision-register.md#d-010--provedor-de-telefonia), `ADIADO`); não faz parte do MVP.

## 10. O que o frontend nunca faz

- Nunca calcula regra de negócio que decide estado (ex.: se um lead pode ser convertido, se uma oportunidade pode mudar de etapa) — apenas envia a intenção e trata a resposta (sucesso ou erro de regra, 409/422).
- Nunca monta query SQL ou acessa qualquer armazenamento além do que a API expõe.
- Nunca confia em dado sensível vindo apenas do estado local sem revalidação do backend (ex.: permissão de um botão aparecer é UX, a ação em si é sempre revalidada no servidor).
