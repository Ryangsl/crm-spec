# Runbook — Identidade visual administrada pela plataforma (D-086)

A identidade visual é um **serviço do CRM Universal**: a empresa cliente vê e solicita; a equipe da plataforma aplica. Não existe Super Admin, login global nem painel da plataforma: a operação é feita por um **operador da plataforma** com a permissão reservada `branding:manage`, concedida por operação de dados, como `plan:convert` (D-085). Quando existir o painel administrativo da plataforma, é ele quem recebe essa permissão. **Nenhum destes passos foi executado em ambiente real.**

## 1. Permissões

| Permissão | Quem tem | Para quê |
|---|---|---|
| `branding:read` | Admin e Diretor (papéis de fábrica) | Ver a identidade atual e a solicitação pendente |
| `branding:request` | Só o papel Admin de fábrica | Solicitar alteração |
| `branding:manage` | Ninguém por padrão; operador da plataforma | Aplicar, restaurar e encerrar solicitações |

A API de papéis do tenant **não oferece nem aceita** `branding:manage` e `branding:request`: o Admin da empresa não concede a si mesmo aplicar a identidade nem repassa a solicitação a outro papel. O `GET /v1/branding` que desenha a interface continua aberto a todo usuário do tenant, porque toda tela precisa das cores.

## 2. Tenants existentes

O seed só afeta tenants novos. Em ambiente real, com autorização e backup:

```sql
INSERT INTO permissions (id, key, module) VALUES
  ('<uuid-v7>', 'branding:read', 'branding'),
  ('<uuid-v7>', 'branding:request', 'branding'),
  ('<uuid-v7>', 'branding:manage', 'branding')
ON CONFLICT (key) DO NOTHING;

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r JOIN permissions p ON p.key = 'branding:read'
WHERE r.name IN ('admin', 'diretor') AND r.deleted_at IS NULL
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r JOIN permissions p ON p.key = 'branding:request'
WHERE r.name = 'admin' AND r.deleted_at IS NULL
ON CONFLICT DO NOTHING;
```

Até lá, a identidade segue aplicada normalmente; só a tela de Identidade Visual e a solicitação ficam indisponíveis para esses tenants.

## 3. Atender uma solicitação

Desde a revisão de 2026-11-05 da D-086, a solicitação pode trazer uma **proposta** (nome, tema e cores, já validados) além da mensagem. Na tela de Identidade Visual, o operador vê a proposta com as cores e a pré-visualização e usa **Carregar proposta no editor**; revisar e **Salvar alterações** aplica e encerra a solicitação.

**Desenvolvimento local:** `npm run dev:platform-operator` (no `crm-backend`, com a trava `db:check`) cria ou atualiza o usuário `operador@plataforma.local` com o papel `operador-plataforma` (`branding:manage`, `branding:read`) na empresa de `exemplo.localhost` (outra: `-- --host trial.localhost`). Nunca use esse comando fora da sua máquina.

1. Ver as solicitações pendentes: linhas `crm.branding.request` em `tenant_settings` (ou a tela de Identidade Visual do tenant, com o operador logado nele). Cada pedido também fica no `audit_log` (`branding.change_requested`).
2. O operador precisa de um usuário no tenant com um papel próprio contendo `branding:manage` e `branding:read`, concedido por dados. Remova a concessão depois.
3. Na tela de Identidade Visual: ajustar nome, cores e tema e **Salvar alterações**. Aplicar encerra a solicitação. Para não aplicar, use **Encerrar sem aplicar**.
4. Tudo fica auditado: `branding.updated`, `branding.reset`, `branding.request_dismissed`.

O backend recusa cores fora de `#RRGGBB` e combinações abaixo de WCAG AA, informando o campo.
