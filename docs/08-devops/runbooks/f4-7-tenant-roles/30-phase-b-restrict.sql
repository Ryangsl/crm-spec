-- F4.7 / runbook de papeis dos tenants existentes — 30: FASE B, marcador de restricao.
-- Uso: psql -v ON_ERROR_STOP=1 -v tenant_id=<UUID do tenant> -f 30-phase-b-restrict.sql
--
-- SO RODE DEPOIS DA FASE A (20) E DA SUA VERIFICACAO. Concede business_hours:restricted ao
-- vendedor (e ao admin, que recebe todas as permissoes do catalogo no seed; a isencao do admin
-- prevalece). Mesmo assim ninguem e bloqueado enquanto o Admin nao LIGAR a restricao do tenant
-- (desligada por padrao) e houver um horario comercial valido. So INSERE; idempotente.
\set ON_ERROR_STOP on

SELECT EXISTS (SELECT 1 FROM tenants WHERE id = :'tenant_id' AND deleted_at IS NULL) AS tenant_ok \gset
\if :tenant_ok
\else
  \echo 'ABORTADO: tenant nao encontrado (ou excluido). Nada foi alterado.'
  \quit
\endif

-- Guarda da ordem segura: toda isencao da FASE A precisa existir antes de qualquer restricao.
SELECT (
  NOT EXISTS (
    SELECT 1 FROM roles r
    WHERE r.tenant_id = :'tenant_id' AND r.is_system AND r.deleted_at IS NULL
      AND r.name IN ('admin', 'diretor', 'gerente', 'supervisor')
      AND NOT EXISTS (
        SELECT 1 FROM role_permissions rp JOIN permissions p ON p.id = rp.permission_id
        WHERE rp.role_id = r.id AND p.key = 'business_hours:exempt')
  )
  AND EXISTS (SELECT 1 FROM permissions WHERE key = 'business_hours:restricted')
) AS phase_a_ok \gset
\if :phase_a_ok
\else
  \echo 'ABORTADO: a FASE A (20-phase-a-exempt.sql) nao esta completa neste tenant. Nada foi alterado.'
  \quit
\endif

BEGIN;

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
JOIN (VALUES
  ('admin',    'business_hours:restricted'),
  ('vendedor', 'business_hours:restricted')
) AS g(role_name, permission_key) ON g.role_name = r.name
JOIN permissions p ON p.key = g.permission_key
WHERE r.tenant_id = :'tenant_id' AND r.is_system AND r.deleted_at IS NULL
ON CONFLICT (role_id, permission_id) DO NOTHING;

COMMIT;
\echo 'FASE B concluida. Rode 40-post-checks.sql.'
