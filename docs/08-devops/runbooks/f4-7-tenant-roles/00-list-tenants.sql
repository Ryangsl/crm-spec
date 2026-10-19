-- F4.7 / runbook de papeis dos tenants existentes — 00: listar tenants (SOMENTE LEITURA).
-- Uso: psql -v ON_ERROR_STOP=1 -f 00-list-tenants.sql
-- Escolha explicitamente cada tenant a atualizar; os scripts seguintes recebem UM tenant por vez.
SELECT t.id AS tenant_id, t.name, t.status, t.deleted_at,
       (SELECT count(*) FROM roles r WHERE r.tenant_id = t.id AND r.is_system AND r.deleted_at IS NULL) AS papeis_de_sistema,
       (SELECT count(*) FROM users u WHERE u.tenant_id = t.id AND u.deleted_at IS NULL) AS usuarios
FROM tenants t
ORDER BY t.created_at;
