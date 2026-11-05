# Runbook — Trial comercial (D-085)

Operações administrativas do Trial. Não há self-service nem checkout (D-037, D-059). Em ambiente real, execute só com autorização explícita e backup recente. **Nenhum destes passos foi executado em ambiente real.**

## 1. Aplicar a migration

`prisma migrate deploy` aplica `20261105120000_trial_plans_entitlements`. Ela é aditiva: cria as colunas e a linha do plano Trial. Nenhum tenant existente muda de plano ou de status; planos existentes ficam sem `code` e seguem sem restrição.

**Atenção:** tenants que já estejam com `status = 'trial'` deixam de ser recusados no login e entram em modo de consulta (`trial_not_started`). Antes de aplicar, confira quais existem:

```sql
SELECT id, name, status, plan_id FROM tenants WHERE status = 'trial' AND deleted_at IS NULL;
```

## 2. Conceder as permissões aos tenants existentes

O seed só afeta tenants novos. Tenants existentes precisam receber `plan:read` (Admin, Diretor, Gerente) e `plan:manage` (Admin) para ver o consumo e iniciar a avaliação. **Não** use o `seed.ts` completo em ambiente real. Sem essas permissões o tenant continua funcionando; só não vê a tela de consumo.

```sql
INSERT INTO permissions (id, key, module) VALUES
  ('<uuid-v7>', 'plan:read', 'plan'),
  ('<uuid-v7>', 'plan:manage', 'plan'),
  ('<uuid-v7>', 'plan:convert', 'plan')
ON CONFLICT (key) DO NOTHING;

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r JOIN permissions p ON p.key = 'plan:read'
WHERE r.name IN ('admin', 'diretor', 'gerente') AND r.deleted_at IS NULL
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r JOIN permissions p ON p.key = 'plan:manage'
WHERE r.name = 'admin' AND r.deleted_at IS NULL
ON CONFLICT DO NOTHING;
```

SQL conferido só em banco descartável. `plan:convert` não entra em nenhum papel de fábrica.

## 3. Provisionar uma empresa em avaliação

```bash
TRIAL_ADMIN_PASSWORD='...' npm run tenant:provision-trial -- \
  --name "Empresa" --document 00000000000000 \
  --admin-name "Nome" --admin-email email@empresa.com
```

A senha vem do ambiente, nunca da linha de comando, e não é impressa. O script cria a empresa com `status = 'trial'` e o plano Trial, sem iniciar a contagem, os papéis de fábrica e o primeiro Admin. Recusa documento já cadastrado e e-mail já usado em outra empresa, sem alterar nada: repetir a avaliação pela mesma empresa não é possível por aqui. Quem inicia os 14 dias é o Admin, no CRM.

## 4. Alterar os valores do Trial

```sql
UPDATE plans SET limits = jsonb_set(limits, '{leads}', '200') WHERE code = 'trial';
```

Vale na próxima requisição, para todos os tenants nesse plano. `trial_days` só afeta avaliações ainda não iniciadas: quem já iniciou mantém a data gravada.

## 5. Converter uma empresa para um plano pago

Não há gateway: a conversão é uma operação administrativa, depois da contratação fora do sistema.

1. Garanta que o plano de destino existe, com `code` e sem `trial_days`:
   ```sql
   INSERT INTO plans (id, code, name, limits, features, created_at, updated_at)
   VALUES ('<uuid-v7>', 'starter', 'Starter',
     '{"users": 10, "leads": 1000, "customers": 1000, "opportunities": 500, "storage_bytes": 1073741824}',
     '{"dashboard_basic": true, "customers": true, "leads": true, "lead_distribution": true, "pipeline": true, "opportunities": true, "follow_ups": true, "conversations": true}',
     now(), now());
   ```
   Os valores acima são só um exemplo de formato: **planos pagos e seus limites ainda não foram definidos pelo negócio**.
2. Conceda `plan:convert` a um operador, em um papel próprio dentro do tenant que vai ser convertido. A API de papéis recusa essa permissão de propósito; a concessão é por dados e deve ser removida depois.
3. O operador chama `POST /v1/plan/conversion` com `{ "plan_code": "starter", "reason": "referência do contrato" }`.

O efeito é trocar o plano e o status para `active`, em uma transação, com registro `plan.converted` no `audit_log` (plano de origem e destino, status anterior, motivo e autor). Nenhum dado é alterado e as datas do trial ficam como histórico. Limite menor que o consumo atual não apaga nada: só impede novos registros daquele recurso.

## 6. Suspender e reativar

A suspensão continua manual (`status = 'suspended'`) e é independente do trial. Reativar um tenant em avaliação é devolver `status = 'trial'`: as datas continuam valendo, então o tempo suspenso não é devolvido. Limitações de sessão na suspensão: ver D-084. Regras do Trial: D-085.
