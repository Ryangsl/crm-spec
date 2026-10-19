-- F4.7 / runbook de papeis dos tenants existentes — 20: FASE A, isencoes e gestao de liberacoes.
-- Uso: psql -v ON_ERROR_STOP=1 -v tenant_id=<UUID do tenant> -f 20-phase-a-exempt.sql
--
-- So INSERE (nada e atualizado nem removido) e e idempotente (ON CONFLICT DO NOTHING). Uma unica
-- transacao. Nao liga a restricao e nao restringe ninguem: esta fase so concede
--   * ao catalogo global de permissoes: access_exceptions:manage, business_hours:restricted,
--     business_hours:exempt (o catalogo e compartilhado entre tenants; a linha sozinha nao da
--     acesso a ninguem);
--   * aos papeis de sistema do tenant: business_hours:exempt (admin, diretor, gerente,
--     supervisor) e access_exceptions:manage (admin, gerente) — mesmo mapeamento de prisma/seed.ts.
-- O marcador de RESTRICAO (business_hours:restricted) so e concedido na FASE B (30).
\set ON_ERROR_STOP on

SELECT EXISTS (SELECT 1 FROM tenants WHERE id = :'tenant_id' AND deleted_at IS NULL) AS tenant_ok \gset
\if :tenant_ok
\else
  \echo 'ABORTADO: tenant nao encontrado (ou excluido). Nada foi alterado.'
  \quit
\endif

BEGIN;

-- UUID v7 (D-001 / ADR-009) para as linhas novas de `permissions`. O Prisma gera o id no cliente
-- e o banco nao tem default; a funcao e TEMPORARIA (some ao fechar a sessao) e nao altera o schema.
CREATE FUNCTION pg_temp.uuid_v7() RETURNS text LANGUAGE sql VOLATILE AS $$
  SELECT encode(
    set_bit(set_bit(
      overlay(uuid_send(gen_random_uuid())
              PLACING substring(int8send((extract(epoch FROM clock_timestamp()) * 1000)::bigint) FROM 3)
              FROM 1 FOR 6),
      52, 1), 53, 1),
    'hex')::uuid::text
$$;

-- 1. Catalogo global de permissoes.
INSERT INTO permissions (id, key, module)
SELECT pg_temp.uuid_v7(), v.key, v.module
FROM (VALUES
  ('access_exceptions:manage',  'access_exceptions'),
  ('business_hours:restricted', 'business_hours'),
  ('business_hours:exempt',     'business_hours')
) AS v(key, module)
ON CONFLICT (key) DO NOTHING;

-- 2. Isencoes e gestao de liberacoes nos papeis de sistema do tenant.
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
JOIN (VALUES
  ('admin',      'access_exceptions:manage'),
  ('admin',      'business_hours:exempt'),
  ('diretor',    'business_hours:exempt'),
  ('gerente',    'access_exceptions:manage'),
  ('gerente',    'business_hours:exempt'),
  ('supervisor', 'business_hours:exempt')
) AS g(role_name, permission_key) ON g.role_name = r.name
JOIN permissions p ON p.key = g.permission_key
WHERE r.tenant_id = :'tenant_id' AND r.is_system AND r.deleted_at IS NULL
ON CONFLICT (role_id, permission_id) DO NOTHING;

COMMIT;
\echo 'FASE A concluida. Rode 40-post-checks.sql e confira antes da FASE B.'
