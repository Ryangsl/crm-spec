import json, urllib.request, urllib.error, subprocess, datetime, time, os, sys, uuid

BASE = "http://localhost:3101"
DB = "crm_mat_f47"
PWD = "Mat12345!"
RESULTS = []  # (mat, passo, ok)
os.environ["MSYS_NO_PATHCONV"] = "1"


def psql(q):
    r = subprocess.run(["docker", "exec", "crm-backend-postgres-1", "psql", "-U", "crm", "-d", DB, "-Atc", q],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr)
    return r.stdout.strip()


def call(method, path, token=None, body=None):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read().decode()
            return r.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, raw


def short(b, n=260):
    s = json.dumps(b, ensure_ascii=False) if not isinstance(b, str) else b
    return s if len(s) <= n else s[:n] + "...(truncado)"


def step(mat, passo, who, method, path, token=None, body=None, expect=None, code=None, show=True):
    st, b = call(method, path, token, body)
    ec = b.get("error", {}).get("code") if isinstance(b, dict) and isinstance(b.get("error"), dict) else None
    ok = True
    if expect is not None:
        ok = st == expect and (code is None or ec == code)
    RESULTS.append((mat, passo, ok))
    flag = "OK " if ok else "ERRO"
    print(f"[{mat}] {flag} {passo} | {who} {method} {path} -> HTTP {st}" + (f" {ec}" if ec else "") +
          (f" | {short(b)}" if show else ""))
    return st, b


def login(email, pwd=PWD):
    st, b = call("POST", "/v1/auth/login", None, {"email": email, "password": pwd})
    assert st in (200, 201), (email, st, b)
    return b["access_token"]


def hours(kind):
    now = datetime.datetime.now(datetime.timezone.utc)
    today = now.isoweekday()
    days = list(range(1, 8)) if kind == "dentro" else [d for d in range(1, 8) if d != today]
    return {"schema_version": 1, "timezone": "UTC", "weekly": [{"days": days, "start": "00:00", "end": "23:59"}]}


def sql(label, q):
    print(f"[SQL] {label}: {psql(q)}")


print("######## SETUP")
print("inicio UTC:", datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"))
admin = login("admin@exemplo.crm.local", "Admin123!")
st, roles = call("GET", "/v1/roles", admin)
rl = roles["data"] if isinstance(roles, dict) and "data" in roles else roles
rid = {r["name"]: r["id"] for r in rl}
print("papeis de fabrica no tenant A:", sorted(rid))
for name, rs in [("gerente", ["gerente"]), ("supervisor", ["supervisor"]), ("vendedor", ["vendedor"]),
                 ("multi", ["vendedor", "gerente"]), ("operador", ["operador"])]:
    st, b = call("POST", "/v1/users", admin, {"name": f"MAT {name}", "email": f"{name}@a.mat.test", "password": PWD,
                                               "role_ids": [rid[x] for x in rs]})
    print(f"  usuario {name}@a.mat.test -> HTTP {st}")
T = {n: login(f"{n}@a.mat.test") for n in ["gerente", "supervisor", "vendedor", "multi", "operador"]}
T["admin"] = admin
uid = {n: call("GET", "/v1/users/me", T[n])[1]["id"] for n in T}
st, srcs = call("GET", "/v1/lead-sources", admin)
src = (srcs["data"] if isinstance(srcs, dict) and "data" in srcs else srcs)[0]["id"]
st, lead = call("POST", "/v1/leads", T["gerente"], {"source_id": src, "name": "MAT Lead A1", "owner_id": uid["vendedor"]})
LEAD = lead["id"]
st, conv = call("POST", "/v1/conversations", T["gerente"], {"lead_id": LEAD})
CONV = conv["id"]
print("lead e conversa de fixture criados:", LEAD[:8], CONV[:8])

# Tenant B (D-059: sem API de provisionamento) — clone dos papeis do tenant A + admin B
psql("""INSERT INTO tenants (id, name, document, plan_id, status, created_at, updated_at)
SELECT 'tenant-b-mat', 'MAT Tenant B', '00000000000999', plan_id, status, now(), now() FROM tenants WHERE document='00000000000100'""")
import uuid as _u
ROLES_A = [l.split("|") for l in psql("select r.id, r.name, r.is_system from roles r join tenants t on t.id=r.tenant_id where t.document='00000000000100' and r.deleted_at is null").split(chr(10))]
ID_B = {}
for rid_a, rname, rsys in ROLES_A:
    ID_B[rid_a] = str(_u.uuid7())
    psql(f"insert into roles (id, tenant_id, name, is_system, created_at, updated_at) values ('{ID_B[rid_a]}','tenant-b-mat','{rname}',{'true' if rsys=='t' else 'false'},now(),now())")
    psql(f"insert into role_permissions (role_id, permission_id) select '{ID_B[rid_a]}', permission_id from role_permissions where role_id='{rid_a}'")
ADMIN_B_ID = str(_u.uuid7())
ADMIN_ROLE_B = [v for k, v in ID_B.items() if [r for r in ROLES_A if r[0] == k][0][1] == "admin"][0]
psql(f"insert into users (id, tenant_id, name, email, password_hash, status, created_at, updated_at) select '{ADMIN_B_ID}', 'tenant-b-mat', 'MAT admin B', 'admin@b.mat.test', password_hash, 'active', now(), now() from users where email='admin@exemplo.crm.local'")
psql(f"insert into user_roles (user_id, role_id) values ('{ADMIN_B_ID}','{ADMIN_ROLE_B}')")
adminB = login("admin@b.mat.test", "Admin123!")
roles_b = call("GET", "/v1/roles", adminB)[1]
rlb = roles_b["data"] if isinstance(roles_b, dict) and "data" in roles_b else roles_b
ridb = {r["name"]: r["id"] for r in rlb}
for name in ["gerente", "vendedor"]:
    call("POST", "/v1/users", adminB, {"name": f"MAT {name} B", "email": f"{name}@b.mat.test", "password": PWD, "role_ids": [ridb[name]]})
TB = {"admin": adminB, "gerente": login("gerente@b.mat.test"), "vendedor": login("vendedor@b.mat.test")}
uidb = {n: call("GET", "/v1/users/me", TB[n])[1]["id"] for n in TB}
src_b = call("GET", "/v1/lead-sources", adminB)[1]
srcb = (src_b["data"] if isinstance(src_b, dict) and "data" in src_b else src_b)
print("tenant B: papeis", sorted(ridb), "| lead-sources visiveis em B:", len(srcb))

print("\n######## MAT-009 toggle global")
M = "MAT-009"
step(M, "1 ler toggle (ausente = desligado)", "admin", "GET", "/v1/tenant-settings/business-hours-restriction", T["admin"], expect=200)
step(M, "2 ativar sem horario valido", "admin", "PUT", "/v1/tenant-settings/business-hours-restriction", T["admin"], {"enabled": True}, 422, "BUSINESS_HOURS_REQUIRED")
step(M, "3 desligar sem horario e aceito", "admin", "PUT", "/v1/tenant-settings/business-hours-restriction", T["admin"], {"enabled": False}, 200)
step(M, "4 horario invalido (inicio >= fim) e recusado pela API", "admin", "PUT", "/v1/tenant-settings/business-hours", T["admin"],
     {"schema_version": 1, "timezone": "UTC", "weekly": [{"days": [1], "start": "18:00", "end": "09:00"}]}, None)
step(M, "5 definir horario valido", "admin", "PUT", "/v1/tenant-settings/business-hours", T["admin"], hours("dentro"), 200, show=False)
step(M, "6 ativar com horario valido", "admin", "PUT", "/v1/tenant-settings/business-hours-restriction", T["admin"], {"enabled": True}, 200)
step(M, "7 ativar de novo (idempotente)", "admin", "PUT", "/v1/tenant-settings/business-hours-restriction", T["admin"], {"enabled": True}, 200)
step(M, "8 ler toggle ligado", "admin", "GET", "/v1/tenant-settings/business-hours-restriction", T["admin"], expect=200)
step(M, "9 string 'true' e recusada", "admin", "PUT", "/v1/tenant-settings/business-hours-restriction", T["admin"], {"enabled": "true"}, 400)
sql("auditoria do toggle (esperado 2: ligar na 1a vez e desligar? ver nota)", "select count(*) from audit_log where entity_type='tenant_settings' and payload->>'key'='crm.business_hours.restriction.enabled'")
for who in ["gerente", "vendedor", "supervisor", "operador", "multi"]:
    step(M, f"10 {who} le o toggle", who, "GET", "/v1/tenant-settings/business-hours-restriction", T[who], expect=403, code="FORBIDDEN")
    step(M, f"11 {who} altera o toggle", who, "PUT", "/v1/tenant-settings/business-hours-restriction", T[who], {"enabled": False}, 403, "FORBIDDEN")
step(M, "12 sem token", "anonimo", "GET", "/v1/tenant-settings/business-hours-restriction", None, expect=401)
step(M, "13 toggle continua ligado apos as tentativas", "admin", "GET", "/v1/tenant-settings/business-hours-restriction", T["admin"], expect=200)
step(M, "14 desligar", "admin", "PUT", "/v1/tenant-settings/business-hours-restriction", T["admin"], {"enabled": False}, 200)
step(M, "15 ler desligado", "admin", "GET", "/v1/tenant-settings/business-hours-restriction", T["admin"], expect=200)

print("\n######## MAT-010 acesso dentro e fora do horario (usuario sujeito)")
M = "MAT-010"
step(M, "1 horario DENTRO + toggle ligado", "admin", "PUT", "/v1/tenant-settings/business-hours", T["admin"], hours("dentro"), 200, show=False)
step(M, "1b ligar", "admin", "PUT", "/v1/tenant-settings/business-hours-restriction", T["admin"], {"enabled": True}, 200)
step(M, "2 status do vendedor (dentro)", "vendedor", "GET", "/v1/access-status", T["vendedor"], expect=200)
step(M, "3 vendedor lista leads (dentro)", "vendedor", "GET", "/v1/leads", T["vendedor"], expect=200, show=False)
step(M, "4 vendedor lista conversas (dentro)", "vendedor", "GET", "/v1/conversations", T["vendedor"], expect=200, show=False)
step(M, "5 horario FORA", "admin", "PUT", "/v1/tenant-settings/business-hours", T["admin"], hours("fora"), 200, show=False)
step(M, "6 status do vendedor (fora)", "vendedor", "GET", "/v1/access-status", T["vendedor"], expect=200)
n_leads_antes = psql("select count(*) from leads where deleted_at is null")
for passo, method, path, body in [
    ("7 listar leads", "GET", "/v1/leads", None), ("8 ler lead", "GET", f"/v1/leads/{LEAD}", None),
    ("9 criar lead", "POST", "/v1/leads", {"source_id": src, "name": "NAO DEVE CRIAR"}),
    ("10 editar lead", "PATCH", f"/v1/leads/{LEAD}", {"name": "NAO DEVE ALTERAR"}),
    ("11 qualificar lead", "POST", f"/v1/leads/{LEAD}/qualify", None),
    ("12 listar conversas", "GET", "/v1/conversations", None), ("13 ler conversa", "GET", f"/v1/conversations/{CONV}", None),
    ("14 listar mensagens", "GET", f"/v1/conversations/{CONV}/messages", None),
    ("15 enviar mensagem", "POST", f"/v1/conversations/{CONV}/messages", {"content": "NAO DEVE GRAVAR"}),
    ("16 encerrar conversa", "POST", f"/v1/conversations/{CONV}/close", None)]:
    step(M, passo, "vendedor", method, path, T["vendedor"], body, 403, "OUTSIDE_BUSINESS_HOURS", show=False)
sql("leads antes/depois", f"select {n_leads_antes} as antes, count(*) as depois from leads where deleted_at is null")
sql("nome do lead intacto", f"select name from leads where id='{LEAD}'")
sql("mensagens gravadas", "select count(*) from messages")
step(M, "17 operador (sem marcador) acessa fora do horario", "operador", "GET", "/v1/leads", T["operador"], expect=200, show=False)
step(M, "18 rota sem restricao: /users/me do vendedor", "vendedor", "GET", "/v1/users/me", T["vendedor"], expect=200, show=False)
step(M, "19 permissao antes do horario: operador sem conversations:assign", "operador", "POST", f"/v1/conversations/{CONV}/assign", T["operador"], {"user_id": None}, 403, "FORBIDDEN", show=False)
step(M, "20 desligar o toggle libera o vendedor", "admin", "PUT", "/v1/tenant-settings/business-hours-restriction", T["admin"], {"enabled": False}, 200)
step(M, "20b vendedor acessa", "vendedor", "GET", "/v1/leads", T["vendedor"], expect=200, show=False)
step(M, "21 religar", "admin", "PUT", "/v1/tenant-settings/business-hours-restriction", T["admin"], {"enabled": True}, 200)
step(M, "21b vendedor bloqueado de novo", "vendedor", "GET", "/v1/leads", T["vendedor"], expect=403, code="OUTSIDE_BUSINESS_HOURS", show=False)

print("\n######## MAT-011 precedencia das isencoes e multiplos papeis (fora do horario, restricao ligada)")
M = "MAT-011"
st, me = call("GET", "/v1/users/me", T["multi"])
perms = me.get("permissions", []) if isinstance(me, dict) else []
print("[MAT-011] multi: papeis", me.get("roles"), "| marcadores:", [p for p in perms if p.startswith("business_hours:") or p.startswith("access_exceptions:")])
for who in ["admin", "gerente", "supervisor", "multi"]:
    step(M, f"1 {who} (isento) acessa leads", who, "GET", "/v1/leads", T[who], expect=200, show=False)
    step(M, f"2 {who} acessa conversas", who, "GET", "/v1/conversations", T[who], expect=200, show=False)
    step(M, f"3 status de {who}", who, "GET", "/v1/access-status", T[who], expect=200)
step(M, "4 operador (sem marcador)", "operador", "GET", "/v1/leads", T["operador"], expect=200, show=False)
step(M, "5 vendedor puro continua bloqueado", "vendedor", "GET", "/v1/leads", T["vendedor"], expect=403, code="OUTSIDE_BUSINESS_HOURS", show=False)
step(M, "6 conceder excecao ao multi e rejeitado (nao sujeito)", "gerente", "POST", "/v1/access-exceptions", T["gerente"],
     {"user_id": uid["multi"], "scope": "leads", "reason": "teste", "expires_at": (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")}, 422, "ACCESS_EXCEPTION_TARGET_NOT_RESTRICTED")

step(M, "7 PATCH users: multi apenas vendedor", "admin", "PATCH", f"/v1/users/{uid['multi']}", T["admin"], {"role_ids": [rid["vendedor"]]}, 200, show=False)
step(M, "7b multi (so vendedor) bloqueado", "multi", "GET", "/v1/leads", T["multi"], expect=403, code="OUTSIDE_BUSINESS_HOURS", show=False)
step(M, "7c status de multi (so vendedor)", "multi", "GET", "/v1/access-status", T["multi"], expect=200)
step(M, "7d restaurar vendedor+gerente", "admin", "PATCH", f"/v1/users/{uid['multi']}", T["admin"], {"role_ids": [rid["vendedor"], rid["gerente"]]}, 200, show=False)
step(M, "7e multi liberado de novo", "multi", "GET", "/v1/leads", T["multi"], expect=200, show=False)

print("\n######## MAT-012 liberacao excepcional")
M = "MAT-012"
def iso_in(seconds):
    return (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=seconds)).strftime("%Y-%m-%dT%H:%M:%SZ")
def grant(who, scope, reason="Plantao de fim de semana", exp=None, user="vendedor", exp_key="expires_at", extra=None):
    body = {"user_id": uid[user], "scope": scope, "reason": reason, exp_key: exp or iso_in(3600)}
    if extra: body.update(extra)
    return body
step(M, "1 vendedor bloqueado antes", "vendedor", "GET", "/v1/leads", T["vendedor"], expect=403, code="OUTSIDE_BUSINESS_HOURS", show=False)
st, e1 = step(M, "2 gerente concede escopo leads (1h)", "gerente", "POST", "/v1/access-exceptions", T["gerente"], grant("gerente", "leads"), 201)
step(M, "3 vendedor acessa leads", "vendedor", "GET", "/v1/leads", T["vendedor"], expect=200, show=False)
step(M, "4 conversas continuam bloqueadas (escopo leads)", "vendedor", "GET", "/v1/conversations", T["vendedor"], expect=403, code="OUTSIDE_BUSINESS_HOURS", show=False)
st, e2 = step(M, "5 admin concede escopo conversations (1h)", "admin", "POST", "/v1/access-exceptions", T["admin"], grant("admin", "conversations"), 201)
step(M, "6 vendedor acessa conversas", "vendedor", "GET", "/v1/conversations", T["vendedor"], expect=200, show=False)
st, e3 = step(M, "7 concede escopo all (excecao simultanea)", "gerente", "POST", "/v1/access-exceptions", T["gerente"], grant("gerente", "all"), 201)
st, lst = step(M, "8 listar excecoes", "gerente", "GET", "/v1/access-exceptions", T["gerente"], expect=200, show=False)
print("[MAT-012] total =", lst["total"], "| escopos na ordem retornada:", [d["scope"] for d in lst["data"]], "| esperado total 3")
RESULTS.append((M, "8b total == 3", lst["total"] == 3))
step(M, "9 filtro active=true", "gerente", "GET", "/v1/access-exceptions?active=true", T["gerente"], expect=200, show=False)
step(M, "10 filtro user_id + limit", "gerente", "GET", f"/v1/access-exceptions?user_id={uid['vendedor']}&limit=1", T["gerente"], expect=200, show=False)
step(M, "11 revogar a excecao 'all'", "gerente", "DELETE", f"/v1/access-exceptions/{e3['id']}", T["gerente"], expect=200)
step(M, "11b vendedor ainda acessa (as outras seguem valendo)", "vendedor", "GET", "/v1/leads", T["vendedor"], expect=200, show=False)
st, r2 = step(M, "12 revogar de novo preserva revoked_at", "gerente", "DELETE", f"/v1/access-exceptions/{e3['id']}", T["gerente"], expect=200)
print("[MAT-012] revoked_at igual nas duas revogacoes:", r2.get("revoked_at"))
step(M, "13 revogar leads", "gerente", "DELETE", f"/v1/access-exceptions/{e1['id']}", T["gerente"], expect=200, show=False)
step(M, "13b leads bloqueado de novo; conversas ainda liberada", "vendedor", "GET", "/v1/leads", T["vendedor"], expect=403, code="OUTSIDE_BUSINESS_HOURS", show=False)
step(M, "13c conversas liberadas pela excecao do admin", "vendedor", "GET", "/v1/conversations", T["vendedor"], expect=200, show=False)
step(M, "14 revogar conversations", "admin", "DELETE", f"/v1/access-exceptions/{e2['id']}", T["admin"], expect=200, show=False)
step(M, "14b tudo bloqueado de novo", "vendedor", "GET", "/v1/conversations", T["vendedor"], expect=403, code="OUTSIDE_BUSINESS_HOURS", show=False)
step(M, "15 motivo vazio", "gerente", "POST", "/v1/access-exceptions", T["gerente"], grant("gerente", "leads", reason=""), 400)
step(M, "16 motivo so espacos", "gerente", "POST", "/v1/access-exceptions", T["gerente"], grant("gerente", "leads", reason="   "), 400, show=False)
st, e1000 = step(M, "16b motivo com exatamente 1000 caracteres e aceito", "gerente", "POST", "/v1/access-exceptions", T["gerente"], grant("gerente", "leads", reason="a" * 1000), 201, show=False)
step(M, "16c revogar a de 1000 caracteres", "gerente", "DELETE", f"/v1/access-exceptions/{e1000['id']}", T["gerente"], expect=200, show=False)
step(M, "17 motivo com 1001 caracteres", "gerente", "POST", "/v1/access-exceptions", T["gerente"], grant("gerente", "leads", reason="a" * 1001), 400, show=False)
step(M, "18 expiracao no passado", "gerente", "POST", "/v1/access-exceptions", T["gerente"], grant("gerente", "leads", exp=iso_in(-60)), 422, "ACCESS_EXCEPTION_EXPIRY_INVALID")
step(M, "19 expiracao so com data", "gerente", "POST", "/v1/access-exceptions", T["gerente"], grant("gerente", "leads", exp="2099-12-31"), 400)
step(M, "20 expiracao sem fuso", "gerente", "POST", "/v1/access-exceptions", T["gerente"], grant("gerente", "leads", exp="2099-12-31T10:00:00"), 400, show=False)
step(M, "21 escopo invalido", "gerente", "POST", "/v1/access-exceptions", T["gerente"], grant("gerente", "tudo"), 400, show=False)
step(M, "22 campo nao previsto (starts_at)", "gerente", "POST", "/v1/access-exceptions", T["gerente"], grant("gerente", "leads", extra={"starts_at": iso_in(0)}), 400, show=False)
for tgt in ["operador", "gerente", "admin"]:
    step(M, f"23 alvo nao sujeito: {tgt}", "gerente", "POST", "/v1/access-exceptions", T["gerente"], grant("gerente", "leads", user=tgt), 422, "ACCESS_EXCEPTION_TARGET_NOT_RESTRICTED", show=False)
for who in ["vendedor", "supervisor", "operador"]:
    step(M, f"24 {who} sem access_exceptions:manage", who, "POST", "/v1/access-exceptions", T[who], grant("gerente", "leads"), 403, "FORBIDDEN", show=False)
    step(M, f"24b {who} lista", who, "GET", "/v1/access-exceptions", T[who], expect=403, code="FORBIDDEN", show=False)
st, e4 = step(M, "25 concede com expiracao em ~30s", "gerente", "POST", "/v1/access-exceptions", T["gerente"], grant("gerente", "leads", exp=iso_in(30)), 201, show=False)
print("[MAT-012] expires_at da excecao curta:", e4.get("expires_at"))
step(M, "25b vendedor acessa dentro da validade", "vendedor", "GET", "/v1/leads", T["vendedor"], expect=200, show=False)
time.sleep(max(0, (datetime.datetime.fromisoformat(e4["expires_at"].replace("Z", "+00:00")) - datetime.datetime.now(datetime.timezone.utc)).total_seconds()) + 2)
step(M, "25c vendedor bloqueado apos expirar", "vendedor", "GET", "/v1/leads", T["vendedor"], expect=403, code="OUTSIDE_BUSINESS_HOURS", show=False)
sql("auditoria das excecoes", "select action, count(*) from audit_log where entity_type='access_exception' group by 1 order by 1")
sql("excecoes vigentes restantes (limpeza: esperado 0)", "select count(*) from access_exceptions where revoked_at is null and expires_at > now()")

print("\n######## MAT-015 rotas explicitamente excluidas (fora do horario, restricao ligada)")
M = "MAT-015"
csv = "name,email\nMaria MAT,maria@mat.test\n"
open("mat_leads.csv", "w").write(csv)
r = subprocess.run(["curl", "-s", "-w", "\n%{http_code}", "-X", "POST", BASE + "/v1/leads/import", "-H", "Authorization: Bearer " + T["vendedor"],
                    "-F", f"source_id={src}", "-F", "file=@mat_leads.csv;type=text/csv"], capture_output=True, text=True)
body, code = r.stdout.rsplit("\n", 1)
ok = code == "201"
RESULTS.append((M, "1 importar leads (CSV)", ok))
print(f"[{M}] {'OK ' if ok else 'ERRO'} 1 importar leads | vendedor POST /v1/leads/import -> HTTP {code} | {body[:200]}")
st, b = step(M, "2 converter lead em cliente", "vendedor", "POST", f"/v1/leads/{LEAD}/convert", T["vendedor"], {"customer": {"name": "Cliente MAT"}}, None)
RESULTS[-1] = (M, "2 converter lead em cliente", st in (200, 201) and not (isinstance(b, dict) and b.get("error", {}).get("code") == "OUTSIDE_BUSINESS_HOURS"))
step(M, "3a lead-sources com o vendedor de fabrica (sem lead_sources:read)", "vendedor", "GET", "/v1/lead-sources", T["vendedor"], expect=403, code="FORBIDDEN", show=False)
st, role = call("POST", "/v1/roles", admin, {"name": "mat-restrito-fontes", "permission_keys": ["leads:read", "lead_sources:read", "business_hours:restricted"]})
call("POST", "/v1/users", admin, {"name": "MAT restrito fontes", "email": "fontes@a.mat.test", "password": PWD, "role_ids": [role["id"]]})
tf = login("fontes@a.mat.test")
step(M, "3b papel personalizado sujeito: access-status", "fontes", "GET", "/v1/access-status", tf, expect=200)
step(M, "3c papel personalizado: lead-sources", "fontes", "GET", "/v1/lead-sources", tf, expect=200, show=False)
step(M, "3d papel personalizado: leads (contraste)", "fontes", "GET", "/v1/leads", tf, expect=403, code="OUTSIDE_BUSINESS_HOURS", show=False)
step(M, "4 /users/me", "vendedor", "GET", "/v1/users/me", T["vendedor"], expect=200, show=False)
step(M, "5 /access-status", "vendedor", "GET", "/v1/access-status", T["vendedor"], expect=200, show=False)
step(M, "6 clientes (lacuna PN-3)", "vendedor", "GET", "/v1/customers", T["vendedor"], expect=200, show=False)
step(M, "7 oportunidades (lacuna PN-3)", "vendedor", "GET", "/v1/opportunities", T["vendedor"], expect=200, show=False)
step(M, "8 tarefas (lacuna PN-3)", "vendedor", "GET", "/v1/tasks", T["vendedor"], expect=200, show=False)
step(M, "9 notificacoes", "vendedor", "GET", "/v1/notifications/unread-count", T["vendedor"], expect=200, show=False)
step(M, "10 disponibilidade propria", "vendedor", "GET", "/v1/availability/me", T["vendedor"], expect=200, show=False)
step(M, "11 contraste: lead (rota restrita) segue bloqueado", "vendedor", "GET", "/v1/leads", T["vendedor"], expect=403, code="OUTSIDE_BUSINESS_HOURS", show=False)

print("\n######## MAT-016 disponibilidade e distribuicao nao alteradas (fora do horario, restricao ligada)")
M = "MAT-016"
step(M, "1 ligar disponibilidade no tenant", "admin", "PUT", "/v1/tenant-settings/availability", T["admin"], {"enabled": True}, 200)
step(M, "2 vendedor fica DISPONIVEL (rota propria, nao restrita)", "vendedor", "PUT", "/v1/availability/me", T["vendedor"], {"status": "available"}, 200)
sql("estado/historico de disponibilidade antes", f"select (select status from user_availability where user_id='{uid['vendedor']}') as estado, (select count(*) from availability_log) as logs")
step(M, "3 gerente cria lead sem owner (distribuicao)", "gerente", "POST", "/v1/leads", T["gerente"], {"source_id": src, "name": "MAT Lead distribuido"}, 201, show=False)
st, lds = call("GET", "/v1/leads?limit=100", T["gerente"])
lst = lds["data"] if isinstance(lds, dict) and "data" in lds else lds
dist = [l for l in lst if l["name"] == "MAT Lead distribuido"][0]
print("[MAT-016] owner do lead distribuido == vendedor (fora do horario, DISPONIVEL):", dist["owner_id"] == uid["vendedor"])
RESULTS.append((M, "4 distribuicao atribuiu ao vendedor", dist["owner_id"] == uid["vendedor"]))
step(M, "5 vendedor ve a notificacao lead.assigned (rota nao restrita)", "vendedor", "GET", "/v1/notifications/unread-count", T["vendedor"], expect=200)
step(M, "6 mas nao abre o lead (consequencia conhecida)", "vendedor", "GET", f"/v1/leads/{dist['id']}", T["vendedor"], expect=403, code="OUTSIDE_BUSINESS_HOURS", show=False)
step(M, "7 estado de disponibilidade permanece", "vendedor", "GET", "/v1/availability/me", T["vendedor"], expect=200)
sql("estado/historico de disponibilidade depois (iguais ao antes)", f"select (select status from user_availability where user_id='{uid['vendedor']}') as estado, (select count(*) from availability_log) as logs")
step(M, "8 desligar a restricao nao muda o estado", "admin", "PUT", "/v1/tenant-settings/business-hours-restriction", T["admin"], {"enabled": False}, 200, show=False)
sql("apos desligar restricao", f"select (select status from user_availability where user_id='{uid['vendedor']}') as estado, (select count(*) from availability_log) as logs")
step(M, "8b religar", "admin", "PUT", "/v1/tenant-settings/business-hours-restriction", T["admin"], {"enabled": True}, 200, show=False)

print("\n######## MAT-013 isolamento entre tenants")
M = "MAT-013"
# tenant A tem excecao vigente; B nao a enxerga
st, ea = step(M, "1 A: gerente concede excecao ao vendedor A", "gerente(A)", "POST", "/v1/access-exceptions", T["gerente"], grant("gerente", "all"), 201, show=False)
step(M, "2 B: gerente lista (nao ve a de A)", "gerente(B)", "GET", "/v1/access-exceptions", TB["gerente"], expect=200)
step(M, "3 B: revogar excecao de A", "gerente(B)", "DELETE", f"/v1/access-exceptions/{ea['id']}", TB["gerente"], expect=404, show=True)
step(M, "4 B: conceder a usuario de A", "gerente(B)", "POST", "/v1/access-exceptions", TB["gerente"],
     {"user_id": uid["vendedor"], "scope": "all", "reason": "x", "expires_at": iso_in(3600)}, 404)
step(M, "5 B: ler lead de A", "gerente(B)", "GET", f"/v1/leads/{LEAD}", TB["gerente"], expect=404, show=False)
step(M, "6 B: ler conversa de A", "gerente(B)", "GET", f"/v1/conversations/{CONV}", TB["gerente"], expect=404, show=False)
sql("excecao de A intacta (revoked_at nulo)", f"select revoked_at is null from access_exceptions where id='{ea['id']}'")
# toggle e horario sao por tenant
step(M, "7 B: toggle de B independente (desligado)", "admin(B)", "GET", "/v1/tenant-settings/business-hours-restriction", TB["admin"], expect=200)
step(M, "8 B: vendedor B acessa mesmo com A ligado", "vendedor(B)", "GET", "/v1/leads", TB["vendedor"], expect=200, show=False)
step(M, "9 B: horario fora + ligar", "admin(B)", "PUT", "/v1/tenant-settings/business-hours", TB["admin"], hours("fora"), 200, show=False)
step(M, "9b ligar", "admin(B)", "PUT", "/v1/tenant-settings/business-hours-restriction", TB["admin"], {"enabled": True}, 200, show=False)
step(M, "10 B: vendedor B bloqueado (a excecao de A nao vaza)", "vendedor(B)", "GET", "/v1/leads", TB["vendedor"], expect=403, code="OUTSIDE_BUSINESS_HOURS", show=False)
step(M, "11 A: vendedor A segue liberado pela propria excecao", "vendedor(A)", "GET", "/v1/leads", T["vendedor"], expect=200, show=False)
step(M, "12 B: excecao propria de B nao libera A", "gerente(B)", "POST", "/v1/access-exceptions", TB["gerente"],
     {"user_id": uidb["vendedor"], "scope": "leads", "reason": "plantao B", "expires_at": iso_in(3600)}, 201, show=False)
step(M, "13 B: vendedor B liberado", "vendedor(B)", "GET", "/v1/leads", TB["vendedor"], expect=200, show=False)
step(M, "14 A: lista de A so tem excecoes de A", "gerente(A)", "GET", "/v1/access-exceptions?limit=100", T["gerente"], expect=200, show=False)
sql("excecoes por tenant", "select tenant_id, count(*) from access_exceptions group by 1 order by 1")
step(M, "15 limpeza A: revogar excecao", "gerente(A)", "DELETE", f"/v1/access-exceptions/{ea['id']}", T["gerente"], expect=200, show=False)

print("\n######## RESUMO")
from collections import defaultdict
agg = defaultdict(lambda: [0, 0])
for m, p, ok in RESULTS:
    agg[m][0 if ok else 1] += 1
for m in sorted(agg):
    print(f"{m}: {agg[m][0]} passos conforme o esperado, {agg[m][1]} divergentes")
for m, p, ok in RESULTS:
    if not ok:
        print("DIVERGENTE:", m, p)
print("fim UTC:", datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"))
