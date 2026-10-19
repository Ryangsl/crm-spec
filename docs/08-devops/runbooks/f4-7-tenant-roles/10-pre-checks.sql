-- F4.7 / runbook de papeis dos tenants existentes — 10: verificacoes ANTES (SOMENTE LEITURA).
-- Uso: psql -v ON_ERROR_STOP=1 -v tenant_id=<UUID do tenant> -f 10-pre-checks.sql
-- Guarde a saida: ela e a linha de base para comparar com 40-post-checks.sql.
\echo '== 1. Tenant alvo'
SELECT id AS tenant_id, name, status, deleted_at FROM tenants WHERE id = :'tenant_id';

\echo '== 2. Migration do F4.7 aplicada? (esperado: 1 linha com finished_at preenchido e rolled_back_at vazio)'
SELECT migration_name, finished_at, rolled_back_at
FROM _prisma_migrations WHERE migration_name = '20261014120000_f4_7_access_exceptions';
SELECT to_regclass('public.access_exceptions') AS tabela_access_exceptions;

\echo '== 3. Papeis do tenant (esperado: admin, diretor, gerente, supervisor e vendedor presentes e is_system = true)'
SELECT r.name, r.is_system, r.deleted_at,
       (SELECT count(*) FROM role_permissions rp WHERE rp.role_id = r.id) AS permissoes
FROM roles r WHERE r.tenant_id = :'tenant_id' ORDER BY r.name;

\echo '== 4. Papeis com nome de fabrica que NAO sao de sistema (esperado: nenhuma linha; se houver, revisar antes: o runbook so atua em papeis de sistema)'
SELECT r.name, r.is_system, r.deleted_at FROM roles r
WHERE r.tenant_id = :'tenant_id' AND NOT r.is_system
  AND r.name IN ('admin', 'diretor', 'gerente', 'supervisor', 'vendedor');

\echo '== 5. Pre-requisito do toggle (F4.1): admin tem tenant_settings:update? (esperado: 1 linha)'
SELECT r.name, p.key FROM roles r
JOIN role_permissions rp ON rp.role_id = r.id
JOIN permissions p ON p.id = rp.permission_id
WHERE r.tenant_id = :'tenant_id' AND r.name = 'admin' AND r.is_system AND r.deleted_at IS NULL
  AND p.key = 'tenant_settings:update';

\echo '== 6. Marcadores/permissoes do F4.7 hoje, por papel (antes: normalmente vazio)'
SELECT r.name AS papel, p.key
FROM roles r
JOIN role_permissions rp ON rp.role_id = r.id
JOIN permissions p ON p.id = rp.permission_id
WHERE r.tenant_id = :'tenant_id' AND r.deleted_at IS NULL
  AND p.key IN ('access_exceptions:manage', 'business_hours:restricted', 'business_hours:exempt')
ORDER BY r.name, p.key;

\echo '== 7. Linha de base: total de role_permissions por tenant (o tenant alvo so pode crescer; os OUTROS nao podem mudar)'
SELECT r.tenant_id, count(*) AS role_permissions
FROM role_permissions rp JOIN roles r ON r.id = rp.role_id
GROUP BY r.tenant_id ORDER BY r.tenant_id;

\echo '== 8. IMPACTO: usuarios ativos que passarao a ser SUJEITOS a restricao (tem o papel vendedor e nenhum papel isento: admin, diretor, gerente ou supervisor de sistema, ou papel que ja tenha business_hours:exempt)'
SELECT u.id AS user_id, u.name, u.email,
       array_agg(DISTINCT r2.name ORDER BY r2.name) AS papeis
FROM users u
JOIN user_roles ur ON ur.user_id = u.id
JOIN roles rv ON rv.id = ur.role_id AND rv.name = 'vendedor' AND rv.is_system AND rv.deleted_at IS NULL
JOIN user_roles ur2 ON ur2.user_id = u.id
JOIN roles r2 ON r2.id = ur2.role_id AND r2.deleted_at IS NULL
WHERE u.tenant_id = :'tenant_id' AND rv.tenant_id = :'tenant_id' AND r2.tenant_id = :'tenant_id'
  AND u.status = 'active' AND u.deleted_at IS NULL
  AND NOT EXISTS (
    SELECT 1 FROM user_roles ur3
    JOIN roles r3 ON r3.id = ur3.role_id AND r3.deleted_at IS NULL AND r3.tenant_id = :'tenant_id'
    WHERE ur3.user_id = u.id
      AND (
        (r3.is_system AND r3.name IN ('admin', 'diretor', 'gerente', 'supervisor'))
        OR EXISTS (SELECT 1 FROM role_permissions rp3 JOIN permissions p3 ON p3.id = rp3.permission_id
                   WHERE rp3.role_id = r3.id AND p3.key = 'business_hours:exempt')
      )
  )
GROUP BY u.id, u.name, u.email ORDER BY u.name;

\echo '== 9. REVISAO: usuarios com o papel vendedor E outros papeis (a isencao so vem dos papeis do mapeamento; decidir caso a caso se algum papel personalizado deve ser isento)'
SELECT u.id AS user_id, u.name, array_agg(DISTINCT r2.name ORDER BY r2.name) AS papeis
FROM users u
JOIN user_roles ur ON ur.user_id = u.id
JOIN roles rv ON rv.id = ur.role_id AND rv.name = 'vendedor' AND rv.is_system AND rv.deleted_at IS NULL
JOIN user_roles ur2 ON ur2.user_id = u.id
JOIN roles r2 ON r2.id = ur2.role_id AND r2.deleted_at IS NULL
WHERE u.tenant_id = :'tenant_id' AND rv.tenant_id = :'tenant_id' AND r2.tenant_id = :'tenant_id'
  AND u.deleted_at IS NULL
GROUP BY u.id, u.name HAVING count(DISTINCT r2.id) > 1 ORDER BY u.name;

\echo '== 10. Restricao ja ligada neste tenant? (esperado: nenhuma linha ou false; o runbook NAO liga a restricao)'
SELECT key, value FROM tenant_settings
WHERE tenant_id = :'tenant_id' AND key = 'crm.business_hours.restriction.enabled';
