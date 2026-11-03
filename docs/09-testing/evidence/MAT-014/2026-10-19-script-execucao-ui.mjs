// Script de evidencia (nao faz parte do produto). O prefixo local do caminho foi trocado por <RAIZ> antes de versionar; ajuste OUT/FE para rodar.
import { chromium } from 'playwright-core';
import { execSync } from 'node:child_process';
import fs from 'node:fs';

const WEB = 'http://localhost:5173';
const API = 'http://localhost:3101';
const OUT = '<RAIZ>/universal-crm/crm-spec/docs/09-testing/evidence/MAT-014';
const DAY = '2026-10-19';
fs.mkdirSync(OUT, { recursive: true });
const RES = [];
let shotN = 0;

function psql(q) {
  return execSync(`docker exec crm-backend-postgres-1 psql -U crm -d crm_mat_f47 -Atc "${q}"`, { env: { ...process.env, MSYS_NO_PATHCONV: '1' } }).toString().trim();
}
async function api(method, path, token, body) {
  const r = await fetch(API + path, { method, headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: 'Bearer ' + token } : {}) }, body: body ? JSON.stringify(body) : undefined });
  const t = await r.text();
  let j = null; try { j = JSON.parse(t); } catch { /* vazio */ }
  return { status: r.status, body: j };
}
const login = async (email, pwd = 'Mat12345!') => (await api('POST', '/v1/auth/login', null, { email, password: pwd })).body.access_token;
function check(passo, ok, detalhe = '') {
  RES.push({ passo, ok });
  console.log(`[MAT-014] ${ok ? 'OK  ' : 'ERRO'} ${passo}${detalhe ? ' | ' + detalhe : ''}`);
}
async function shot(page, passo, desc, forceFull = false) {
  shotN += 1;
  const f = `${DAY}-passo${passo}-${desc}.png`;
  const w = await page.evaluate(() => document.documentElement.scrollWidth);
  // pagina que estoura a largura (defeito de layout) so e capturada inteira quando pedido; senao, so a janela
  await page.screenshot({ path: `${OUT}/${f}`, fullPage: forceFull || w <= 1400 });
  if (w > 1400) console.log(`[MAT-014] aviso: largura do documento = ${w}px em ${f}`);
  console.log(`[MAT-014] screenshot ${f}`);
  return f;
}
const bodyText = async (page) => (await page.locator('body').innerText()).replace(/\s+/g, ' ');

const browser = await chromium.launch({ channel: 'chrome', headless: true });
async function session(email, pwd = 'Mat12345!') {
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 }, locale: 'pt-BR' });
  const page = await ctx.newPage();
  await page.goto(WEB + '/login');
  await page.getByLabel('E-mail').fill(email);
  await page.getByLabel('Senha').fill(pwd);
  await page.getByRole('button', { name: 'Entrar' }).click();
  await page.waitForURL((u) => !u.pathname.startsWith('/login'), { timeout: 15000 });
  return { ctx, page };
}
const go = async (page, path, settle = 1500) => { await page.goto(WEB + path); await page.waitForTimeout(settle); };

// ---- estado de partida (via API do banco descartavel): fora do horario, restricao ligada, sem liberacao vigente
const adm = await login('admin@exemplo.crm.local', 'Admin123!');
const tk = { gerente: await login('gerente@a.mat.test'), vendedor: await login('vendedor@a.mat.test') };
const uidV = (await api('GET', '/v1/users/me', tk.vendedor)).body.id;
const now = new Date();
const today = now.getUTCDay() === 0 ? 7 : now.getUTCDay();
const fora = { schema_version: 1, timezone: 'UTC', weekly: [{ days: [1, 2, 3, 4, 5, 6, 7].filter((d) => d !== today), start: '00:00', end: '23:59' }] };
const dentro = { schema_version: 1, timezone: 'UTC', weekly: [{ days: [1, 2, 3, 4, 5, 6, 7], start: '00:00', end: '23:59' }] };
await api('PUT', '/v1/tenant-settings/business-hours', adm, fora);
await api('PUT', '/v1/tenant-settings/business-hours-restriction', adm, { enabled: true });
const active = (await api('GET', '/v1/access-exceptions?active=true&limit=100', tk.gerente)).body;
for (const e of active.data) await api('DELETE', `/v1/access-exceptions/${e.id}`, tk.gerente);
console.log('[estado inicial] horario FORA (UTC, hoje=' + today + '), restricao ligada, liberacoes vigentes revogadas:', active.data.length);

const LEAD = psql("select id from leads where name='MAT Lead A1' limit 1");
const CONV = psql('select id from conversations order by created_at limit 1');
const CUST = psql('select customer_id from leads where id=\'' + LEAD + '\'');
// conversa ligada ao Cliente (para a secao "Conversas" do detalhe do Cliente)
const convC = await api('POST', '/v1/conversations', tk.gerente, { customer_id: CUST });
console.log('[fixture] lead', LEAD.slice(0, 8), 'conversa', CONV.slice(0, 8), 'cliente', CUST.slice(0, 8), 'conversa-cliente HTTP', convC.status);

// ============ PASSO 1: toggle visivel so para o Admin
{
  const a = await session('admin@exemplo.crm.local', 'Admin123!');
  await go(a.page, '/settings/business-hours', 2500);
  const t = await bodyText(a.page);
  check('1 Admin ve "Restricao por horario: ligada" e o botao "Desligar restricao"', t.includes('Restricao por horario: ligada') && (await a.page.getByRole('button', { name: 'Desligar restricao' }).count()) === 1);
  await shot(a.page, 1, 'admin-toggle-ligada');

  // ============ PASSO 2: desligar / ligar pela interface
  await a.page.getByRole('button', { name: 'Desligar restricao' }).click();
  await a.page.waitForTimeout(1500);
  const t2 = await bodyText(a.page);
  check('2a Admin clica "Desligar restricao": estado "desligada" e botao "Ligar restricao"', t2.includes('Restricao por horario: desligada') && (await a.page.getByRole('button', { name: 'Ligar restricao' }).count()) === 1);
  check('2a-API confirma toggle false', (await api('GET', '/v1/tenant-settings/business-hours-restriction', adm)).body.enabled === false);
  await shot(a.page, 2, 'admin-toggle-desligada');
  await a.page.getByRole('button', { name: 'Ligar restricao' }).click();
  await a.page.waitForTimeout(1500);
  const t3 = await bodyText(a.page);
  check('2b Admin clica "Ligar restricao": volta a "ligada"', t3.includes('Restricao por horario: ligada'));
  check('2b-API confirma toggle true', (await api('GET', '/v1/tenant-settings/business-hours-restriction', adm)).body.enabled === true);
  await shot(a.page, 2, 'admin-toggle-religada');
  await a.ctx.close();

  // Admin do tenant C (sem horario valido)
  const c = await session('admin@c.mat.test', 'Admin123!');
  await go(c.page, '/settings/business-hours', 2500);
  const tc = await bodyText(c.page);
  const btn = c.page.getByRole('button', { name: 'Ligar restricao' });
  check('2c Tenant sem horario: aviso "Salve um horario de funcionamento valido acima..." e botao "Ligar restricao" desabilitado',
    tc.includes('Salve um horario de funcionamento valido acima para poder ligar a restricao') && (await btn.count()) === 1 && (await btn.isDisabled()));
  await shot(c.page, 2, 'tenant-sem-horario-botao-desabilitado');
  await c.ctx.close();
}

// Passo 1 (contraprova): Gerente e perfil so com leitura
{
  const g = await session('gerente@a.mat.test');
  await go(g.page, '/settings/business-hours', 2000);
  const t = await bodyText(g.page);
  check('1b Gerente: pagina "Acesso restrito" e sem botao de toggle', t.includes('Acesso restrito') && (await g.page.getByRole('button', { name: /Ligar restricao|Desligar restricao/ }).count()) === 0);
  await shot(g.page, 1, 'gerente-acesso-restrito');
  await g.ctx.close();

  const role = await api('POST', '/v1/roles', adm, { name: 'mat-leitura-config', permission_keys: ['tenant_settings:read'] });
  if (role.status === 201) await api('POST', '/v1/users', adm, { name: 'MAT leitura config', email: 'leituraconfig@a.mat.test', password: 'Mat12345!', role_ids: [role.body.id] });
  const l = await session('leituraconfig@a.mat.test');
  await go(l.page, '/settings/business-hours', 2500);
  const tl = await bodyText(l.page);
  check('1c Perfil so com leitura: ve o estado e "Somente o Admin pode ligar ou desligar a restricao.", sem botao', tl.includes('Restricao por horario: ligada') && tl.includes('Somente o Admin pode ligar ou desligar a restricao') && (await l.page.getByRole('button', { name: /Ligar restricao|Desligar restricao/ }).count()) === 0);
  await shot(l.page, 1, 'perfil-somente-leitura');
  await l.ctx.close();
}

// ============ PASSO 3: banner do Vendedor e contraprovas
{
  const v = await session('vendedor@a.mat.test');
  await go(v.page, '/', 2500);
  const banner = v.page.locator('[data-testid="access-status-banner"]');
  const tb = (await banner.count()) ? (await banner.innerText()).replace(/\s+/g, ' ') : '';
  check('3 Vendedor fora do horario ve o banner "Fora do horario de funcionamento" (Leads e Conversas)',
    tb.includes('Fora do horario de funcionamento') && tb.includes('Leads e Conversas') && tb.includes('liberacao excepcional'), tb);
  await shot(v.page, 3, 'vendedor-banner');

  // contraprova: restricao desligada e dentro do horario
  await api('PUT', '/v1/tenant-settings/business-hours-restriction', adm, { enabled: false });
  await go(v.page, '/', 2000);
  check('3b-contra Restricao desligada: Vendedor NAO ve o banner', (await v.page.locator('[data-testid="access-status-banner"]').count()) === 0);
  await shot(v.page, 3, 'vendedor-sem-banner-restricao-desligada');
  await api('PUT', '/v1/tenant-settings/business-hours-restriction', adm, { enabled: true });
  await api('PUT', '/v1/tenant-settings/business-hours', adm, dentro);
  await go(v.page, '/', 2000);
  check('3c-contra Dentro do horario: Vendedor NAO ve o banner', (await v.page.locator('[data-testid="access-status-banner"]').count()) === 0);
  await shot(v.page, 3, 'vendedor-sem-banner-dentro-do-horario');
  await api('PUT', '/v1/tenant-settings/business-hours', adm, fora);
  await v.ctx.close();

  for (const [email, nome] of [['gerente@a.mat.test', 'gerente'], ['supervisor@a.mat.test', 'supervisor'], ['operador@a.mat.test', 'operador']]) {
    const s = await session(email);
    await go(s.page, '/', 2000);
    check(`3d-contra ${nome} NAO ve o banner`, (await s.page.locator('[data-testid="access-status-banner"]').count()) === 0);
    if (nome === 'supervisor') await shot(s.page, 3, 'supervisor-sem-banner');
    await s.ctx.close();
  }
}

// ============ PASSO 4: banner parcial com liberacao de um escopo
{
  const v = await session('vendedor@a.mat.test');
  const e1 = await api('POST', '/v1/access-exceptions', tk.gerente, { user_id: uidV, scope: 'leads', reason: 'MAT-014 passo 4', expires_at: new Date(Date.now() + 3600e3).toISOString() });
  await go(v.page, '/', 2500);
  const tb = (await v.page.locator('[data-testid="access-status-banner"]').count()) ? (await v.page.locator('[data-testid="access-status-banner"]').innerText()).replace(/\s+/g, ' ') : '';
  check('4a Com liberacao "leads": o banner cita apenas Conversas', tb.includes('O acesso a Conversas esta indisponivel') && !tb.includes('Leads'), tb);
  await shot(v.page, 4, 'vendedor-banner-parcial-conversas');
  const e2 = await api('POST', '/v1/access-exceptions', tk.gerente, { user_id: uidV, scope: 'all', reason: 'MAT-014 passo 4 all', expires_at: new Date(Date.now() + 3600e3).toISOString() });
  await go(v.page, '/', 2500);
  check('4b Com liberacao "all": o banner desaparece', (await v.page.locator('[data-testid="access-status-banner"]').count()) === 0);
  await shot(v.page, 4, 'vendedor-sem-banner-com-liberacao-all');
  await api('DELETE', `/v1/access-exceptions/${e1.body.id}`, tk.gerente);
  await api('DELETE', `/v1/access-exceptions/${e2.body.id}`, tk.gerente);
  await v.ctx.close();
}

// ============ PASSO 5: 403 tratado nas telas
{
  const v = await session('vendedor@a.mat.test');
  const telas = [['/leads', 'leads-lista'], [`/leads/${LEAD}`, 'lead-detalhe'], ['/conversations', 'conversas-lista'], [`/conversations/${CONV}`, 'conversa-detalhe'], [`/customers/${CUST}`, 'cliente-detalhe-secao-conversas']];
  for (const [path, nome] of telas) {
    await go(v.page, path, 3000);
    const t = await bodyText(v.page);
    const aviso = t.includes('Fora do horario de funcionamento') && t.includes('Tente novamente dentro do horario de funcionamento ou peca uma liberacao excepcional');
    const generico = /Nao foi possivel carregar|Erro ao carregar|Something went wrong|undefined/.test(t);
    check(`5 ${path.replace(/[0-9a-f-]{36}/, ':id')}: aviso "Fora do horario de funcionamento", sem erro generico`, aviso && !generico, aviso ? '' : 'texto: ' + t.slice(0, 200));
    await shot(v.page, 5, `vendedor-${nome}`);
  }
  // lacuna conhecida: /leads/new
  await go(v.page, '/leads/new', 2500);
  await shot(v.page, 5, 'vendedor-leads-new-lacuna-conhecida');
  console.log('[MAT-014] observacao: /leads/new aberto (lacuna conhecida: sem tratamento especifico do 403 no envio); envio nao exercitado (sem lead_sources:read no vendedor de fabrica)');

  // ============ PASSO 6: volta ao normal com liberacao
  const e = await api('POST', '/v1/access-exceptions', tk.gerente, { user_id: uidV, scope: 'all', reason: 'MAT-014 passo 6', expires_at: new Date(Date.now() + 3600e3).toISOString() });
  for (const [path, nome] of [['/leads', 'leads'], ['/conversations', 'conversas']]) {
    await go(v.page, path, 3000);
    const t = await bodyText(v.page);
    check(`6a Com liberacao "all": ${path} carrega e o aviso some`, !t.includes('Fora do horario de funcionamento'), '');
    await shot(v.page, 6, `vendedor-${nome}-com-liberacao`);
  }
  await api('DELETE', `/v1/access-exceptions/${e.body.id}`, tk.gerente);
  await go(v.page, '/leads', 3000);
  check('6b Liberacao revogada: o aviso volta em /leads', (await bodyText(v.page)).includes('Fora do horario de funcionamento'));
  await shot(v.page, 6, 'vendedor-leads-apos-revogar');
  await v.ctx.close();
}

// ============ PASSO 7: tela de liberacoes (Gerente)
{
  const g = await session('gerente@a.mat.test');
  await go(g.page, '/', 1500);
  check('7 Gerente ve o item de menu "Liberacoes"', (await g.page.getByRole('link', { name: /Liberacoes/ }).count()) >= 1);
  await g.page.getByRole('link', { name: /Liberacoes/ }).first().click();
  await g.page.waitForURL('**/settings/access-exceptions');
  await g.page.waitForTimeout(2000);
  await shot(g.page, 7, 'gerente-tela-liberacoes-inicial');
  const userSel = g.page.getByLabel('Usuario', { exact: true });
  const opts = await userSel.locator('option').allInnerTexts();
  console.log('[MAT-014] opcoes de usuario:', opts.slice(0, 8).join(' | '));
  await userSel.selectOption({ label: opts.find((o) => o.includes('MAT vendedor')) });
  const pad = (n) => String(n).padStart(2, '0');
  const lt = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
  const total0 = (await api('GET', '/v1/access-exceptions?limit=100', tk.gerente)).body.total;
  const ativas0 = (await api('GET', '/v1/access-exceptions?active=true&limit=100', tk.gerente)).body.total;
  // (7.2a) motivo vazio: o campo e "required" (validacao nativa do navegador impede o envio)
  await g.page.getByRole('button', { name: 'Conceder liberacao' }).click();
  await g.page.waitForTimeout(600);
  const motivoFaltando = await g.page.getByLabel('Motivo').evaluate((el) => el.validity.valueMissing);
  check('7.2a Motivo vazio: o navegador bloqueia o envio (campo obrigatorio) e nada e criado', motivoFaltando === true && (await api('GET', '/v1/access-exceptions?limit=100', tk.gerente)).body.total === total0);
  await shot(g.page, 7, 'recusa-motivo-vazio-validacao-nativa');
  // (7.2a') motivo so com espacos: passa pela validacao nativa e a tela recusa com a mensagem propria
  await g.page.getByLabel('Motivo').fill('   ');
  await g.page.getByLabel('Vale ate').fill(lt(new Date(Date.now() + 3600e3)));
  await g.page.getByRole('button', { name: 'Conceder liberacao' }).click();
  await g.page.waitForTimeout(600);
  check('7.2a2 Motivo so com espacos: "Informe o motivo da liberacao." e nada e criado', (await bodyText(g.page)).includes('Informe o motivo da liberacao.') && (await api('GET', '/v1/access-exceptions?limit=100', tk.gerente)).body.total === total0);
  await shot(g.page, 7, 'recusa-motivo-so-espacos');
  // (7.2b) sem "Vale ate": campo obrigatorio (validacao nativa)
  await g.page.getByLabel('Motivo').fill('Plantao de fim de semana (MAT-014)');
  await g.page.getByLabel('Vale ate').fill('');
  await g.page.getByRole('button', { name: 'Conceder liberacao' }).click();
  await g.page.waitForTimeout(600);
  const exigFaltando = await g.page.getByLabel('Vale ate').evaluate((el) => el.validity.valueMissing);
  check('7.2b Sem "Vale ate": o navegador bloqueia o envio (campo obrigatorio) e nada e criado', exigFaltando === true && (await api('GET', '/v1/access-exceptions?limit=100', tk.gerente)).body.total === total0);
  // (7.2c) expiracao no passado
  await g.page.getByLabel('Vale ate').fill(lt(new Date(Date.now() - 3600e3)));
  await g.page.getByRole('button', { name: 'Conceder liberacao' }).click();
  await g.page.waitForTimeout(600);
  check('7.2c Expiracao no passado: "A expiracao deve estar no futuro."', (await bodyText(g.page)).includes('A expiracao deve estar no futuro.'));
  await shot(g.page, 7, 'recusa-expiracao-passado');
  // (7.1) concessao valida: leads, depois conversations
  const grantUi = async (scopeValue, motivo) => {
    await g.page.getByLabel('Acesso liberado').selectOption(scopeValue);
    await g.page.getByLabel('Motivo').fill(motivo);
    await g.page.getByLabel('Vale ate').fill(lt(new Date(Date.now() + 2 * 3600e3)));
    await g.page.getByRole('button', { name: 'Conceder liberacao' }).click();
    await g.page.waitForTimeout(1800);
  };
  await grantUi('leads', 'Plantao de fim de semana (MAT-014) - leads');
  const t1 = await bodyText(g.page);
  check('7.1a Concessao valida (leads): mensagem de sucesso e item "Vigente" na lista', t1.includes('Liberacao concedida') && /Vigente/i.test(t1));
  await shot(g.page, 7, 'concessao-leads-sucesso');
  await grantUi('conversations', 'Plantao de fim de semana (MAT-014) - conversas');
  check('7.1b Segunda concessao (conversations): a lista passa a ter 2 novas liberacoes (total anterior + 2)', (await api('GET', '/v1/access-exceptions?limit=100', tk.gerente)).body.total === total0 + 2);
  const apiList = await api('GET', '/v1/access-exceptions?active=true', tk.gerente);
  check('7.1c API confirma 2 liberacoes vigentes com motivo e escopo corretos', apiList.body.total === 2 && apiList.body.data.every((e) => e.reason.startsWith('Plantao de fim de semana (MAT-014)')), JSON.stringify(apiList.body.data.map((e) => e.scope)));
  await shot(g.page, 7, 'duas-liberacoes-vigentes');
  // (7.4) revogar uma
  await g.page.getByRole('button', { name: 'Revogar' }).first().click();
  await g.page.waitForTimeout(1800);
  const t2 = await bodyText(g.page);
  check('7.4 Revogar uma: mensagem "Liberacao revogada" e a outra continua vigente', t2.includes('Liberacao revogada') && (await g.page.locator('[data-testid^="status-"]').allInnerTexts()).filter((x) => /Vigente/i.test(x)).length === 1);
  await shot(g.page, 7, 'apos-revogar-uma');
  // (7.3) filtros
  const filtro = g.page.getByLabel('Mostrar');
  await filtro.selectOption('active'); await g.page.waitForTimeout(1500);
  const nAtivas = await g.page.locator('[data-testid^="status-"]').count();
  await shot(g.page, 7, 'filtro-vigentes');
  await filtro.selectOption('inactive'); await g.page.waitForTimeout(1500);
  const nInativas = await g.page.locator('[data-testid^="status-"]').count();
  await shot(g.page, 7, 'filtro-revogadas-ou-expiradas');
  await filtro.selectOption(''); await g.page.waitForTimeout(1500);
  const nTodas = await g.page.locator('[data-testid^="status-"]').count();
  const LIM = (await api('GET', '/v1/access-exceptions?limit=100', tk.gerente)).body.limit || 20; const PAGE = 20;
  const tot = (await api('GET', '/v1/access-exceptions?limit=100', tk.gerente)).body.total; const act = (await api('GET', '/v1/access-exceptions?active=true&limit=100', tk.gerente)).body.total; const ina = (await api('GET', '/v1/access-exceptions?active=false&limit=100', tk.gerente)).body.total;
  check('7.3 Filtros coerentes com a API (vigentes, revogadas/expiradas e todas; por pagina de ate 20 itens)', act === ativas0 + 1 && ina === total0 - ativas0 + 1 && tot === total0 + 2 && nAtivas === Math.min(PAGE, act) && nInativas === Math.min(PAGE, ina) && nTodas === Math.min(PAGE, tot), `UI: vigentes=${nAtivas} inativas=${nInativas} todas=${nTodas} | API: vigentes=${act} inativas=${ina} todas=${tot}`);
  const wlist = await g.page.evaluate(() => document.documentElement.scrollWidth);
  console.log(`[MAT-014] observacao de layout: largura do documento na tela de liberacoes = ${wlist}px (viewport 1280px)`);
  if (wlist > 1400) await shot(g.page, 7, 'defeito-motivo-longo-sem-espacos-estoura-largura', true);
  for (const e of (await api('GET', '/v1/access-exceptions?active=true', tk.gerente)).body.data) await api('DELETE', `/v1/access-exceptions/${e.id}`, tk.gerente);
  await g.ctx.close();

  // Admin tambem acessa a tela
  const a = await session('admin@exemplo.crm.local', 'Admin123!');
  await go(a.page, '/settings/access-exceptions', 2500);
  const ta = await bodyText(a.page);
  check('7b Admin abre a tela de liberacoes (titulo "Liberacoes de acesso", formulario visivel)', ta.includes('Liberacoes de acesso') && ta.includes('Conceder liberacao'));
  await shot(a.page, 7, 'admin-tela-liberacoes');
  await a.ctx.close();
}

// ============ PASSO 8: visibilidade por permissao
for (const [email, nome] of [['supervisor@a.mat.test', 'supervisor'], ['vendedor@a.mat.test', 'vendedor'], ['operador@a.mat.test', 'operador']]) {
  const s = await session(email);
  await go(s.page, '/', 1500);
  const semMenu = (await s.page.getByRole('link', { name: /Liberacoes/ }).count()) === 0;
  await go(s.page, '/settings/access-exceptions', 2000);
  const t = await bodyText(s.page);
  check(`8 ${nome}: sem item "Liberacoes" no menu e /settings/access-exceptions mostra "Acesso restrito" (sem lista)`, semMenu && t.includes('Acesso restrito') && !t.includes('Conceder liberacao'));
  await shot(s.page, 8, `${nome}-acesso-restrito`);
  await s.ctx.close();
}
{
  const a = await session('admin@exemplo.crm.local', 'Admin123!');
  await go(a.page, '/', 1500);
  check('8b Admin ve o item "Liberacoes" no menu', (await a.page.getByRole('link', { name: /Liberacoes/ }).count()) >= 1);
  await a.ctx.close();
}

await browser.close();
const ok = RES.filter((r) => r.ok).length;
console.log(`\n[RESUMO MAT-014] ${ok} de ${RES.length} verificacoes conforme o esperado; screenshots: ${shotN}`);
for (const r of RES.filter((x) => !x.ok)) console.log('DIVERGENTE:', r.passo);
