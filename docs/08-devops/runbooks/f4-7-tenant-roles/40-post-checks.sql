-- F4.7 / runbook de papeis dos tenants existentes — 40: verificacoes DEPOIS (SOMENTE LEITURA).
-- Uso: psql -v ON_ERROR_STOP=1 -v tenant_id=<UUID do tenant> -f 40-post-checks.sql
-- Depois da FASE A (e antes da B), as linhas de `business_hours:restricted` aparecem como
-- "faltando" na secao 1 — e esperado. Depois da FASE B a secao 1 deve voltar vazia.

\echo '== 1. Mapeamento esperado x concedido (esperado depois da FASE B: ZERO linhas)'
WITH expected(role_name, permission_key) AS (VALUES
  ('admin',      'access_exceptions:manage'),
  ('admin',      'business_hours:exempt'),
  ('admin',      'business_hours:restricted'),
  ('diretor',    'business_hours:exempt'),
  ('gerente',    'access_exceptions:manage'),
  ('gerente',    'business_hours:exempt'),
  ('supervisor', 'business_hours:exempt'),
  ('vendedor',   'business_hours:restricted')
), actual AS (
  SELECT r.name AS role_name, p.key AS permission_key
  FROM roles r JOIN role_permissions rp ON rp.role_id = r.id JOIN permissions p ON p.id = rp.permission_id
  WHERE r.tenant_id = :'tenant_id' AND r.is_system AND r.deleted_at IS NULL
    AND p.key IN ('access_exceptions:manage', 'business_hours:restricted', 'business_hours:exempt')
), present_roles AS (
  SELECT DISTINCT name FROM roles WHERE tenant_id = :'tenant_id' AND is_system AND deleted_at IS NULL
)
SELECT e.role_name, e.permission_key, 'faltando' AS situacao
FROM expected e JOIN present_roles pr ON pr.name = e.role_name
WHERE NOT EXISTS (SELECT 1 FROM actual a WHERE a.role_name = e.role_name AND a.permission_key = e.permission_key)
UNION ALL
SELECT a.role_name, a.permission_key, 'inesperado' AS situacao
FROM actual a WHERE NOT EXISTS (SELECT 1 FROM expected e WHERE e.role_name = a.role_name AND e.permission_key = a.permission_key)
ORDER BY 1, 2;

\echo '== 2. Papeis fora do mapeamento (operador, backoffice, leitura e personalizados) com algum marcador (esperado: ZERO linhas)'
SELECT r.name AS papel, r.is_system, p.key
FROM roles r JOIN role_permissions rp ON rp.role_id = r.id JOIN permissions p ON p.id = rp.permission_id
WHERE r.tenant_id = :'tenant_id' AND r.deleted_at IS NULL
  AND p.key IN ('access_exceptions:manage', 'business_hours:restricted', 'business_hours:exempt')
  AND NOT (r.is_system AND r.name IN ('admin', 'diretor', 'gerente', 'supervisor', 'vendedor'));

\echo '== 3. Linhas de role_permissions por tenant — compare com a linha de base (10-pre-checks, secao 7): o tenant alvo so CRESCE; os outros ficam IGUAIS'
SELECT r.tenant_id, count(*) AS role_permissions
FROM role_permissions rp JOIN roles r ON r.id = rp.role_id
GROUP BY r.tenant_id ORDER BY r.tenant_id;

\echo '== 4. Permissoes por papel do tenant: "permissoes_nao_f4_7" deve ser IGUAL ao antes (10-pre-checks, secao 3, menos os marcadores do F4.7)'
SELECT r.name,
       count(p.id) FILTER (WHERE p.key NOT IN ('access_exceptions:manage', 'business_hours:restricted', 'business_hours:exempt')) AS permissoes_nao_f4_7,
       count(p.id) FILTER (WHERE p.key IN ('access_exceptions:manage', 'business_hours:restricted', 'business_hours:exempt')) AS marcadores_f4_7
FROM roles r
LEFT JOIN role_permissions rp ON rp.role_id = r.id
LEFT JOIN permissions p ON p.id = rp.permission_id
WHERE r.tenant_id = :'tenant_id' AND r.deleted_at IS NULL
GROUP BY r.name ORDER BY r.name;

\echo '== 5. Efeito por usuario ativo (sujeito = tem restricao E NAO tem isencao). Compare os sujeitos com a lista de impacto de 10-pre-checks, secao 8'
WITH keys AS (
  SELECT u.id AS user_id, u.name,
         bool_or(p.key = 'business_hours:restricted') AS restricted,
         bool_or(p.key = 'business_hours:exempt') AS exempt
  FROM users u
  JOIN user_roles ur ON ur.user_id = u.id
  JOIN roles r ON r.id = ur.role_id AND r.deleted_at IS NULL AND r.tenant_id = :'tenant_id'
  LEFT JOIN role_permissions rp ON rp.role_id = r.id
  LEFT JOIN permissions p ON p.id = rp.permission_id
  WHERE u.tenant_id = :'tenant_id' AND u.status = 'active' AND u.deleted_at IS NULL
  GROUP BY u.id, u.name
)
SELECT user_id, name,
       COALESCE(restricted, false) AS tem_restricao, COALESCE(exempt, false) AS tem_isencao,
       (COALESCE(restricted, false) AND NOT COALESCE(exempt, false)) AS sujeito_a_restricao
FROM keys ORDER BY sujeito_a_restricao DESC, name;

\echo '== 6. A restricao continua DESLIGADA neste tenant? (esperado: nenhuma linha ou value = false)'
SELECT key, value FROM tenant_settings
WHERE tenant_id = :'tenant_id' AND key = 'crm.business_hours.restriction.enabled';

\echo '== 7. Nenhuma liberacao foi criada pelo runbook (esperado: igual ao antes; normalmente 0)'
SELECT count(*) AS access_exceptions FROM access_exceptions WHERE tenant_id = :'tenant_id';
