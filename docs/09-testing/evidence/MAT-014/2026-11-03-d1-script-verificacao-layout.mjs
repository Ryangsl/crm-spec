// Script de evidencia (nao faz parte do produto). O prefixo local do caminho foi trocado por <RAIZ> antes de versionar; ajuste OUT/FE para rodar.
import { chromium } from 'playwright-core';
import fs from 'node:fs';
import { execSync } from 'node:child_process';

const WEB = 'http://localhost:5173';
const API = 'http://localhost:3101';
const FE = '<RAIZ>/universal-crm/crm-frontend';
const FILE = 'src/features/access-control/pages/AccessExceptionsPage.tsx';
const OUT = '<RAIZ>/universal-crm/crm-spec/docs/09-testing/evidence/MAT-014';
const DAY = '2026-11-03';
const fixed = fs.readFileSync(`${FE}/${FILE}`, 'utf8');
const original = execSync(`git -C "${FE}" show HEAD:${FILE}`).toString();
const results = [];
const log = (...a) => console.log(...a);

async function api(method, path, token, body) {
  const r = await fetch(API + path, { method, headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: 'Bearer ' + token } : {}) }, body: body ? JSON.stringify(body) : undefined });
  const t = await r.text(); let j = null; try { j = JSON.parse(t); } catch { /* vazio */ }
  return { status: r.status, body: j };
}
const login = async (e, p) => (await api('POST', '/v1/auth/login', null, { email: e, password: p })).body.access_token;

// ---- dados (banco descartavel): usuario sujeito + liberacoes com motivos "ruins" para o layout
const adm = await login('admin@exemplo.crm.local', 'Admin123!');
const roles = (await api('GET', '/v1/roles', adm)).body; const rl = roles.data ?? roles;
const vend = rl.find((r) => r.name === 'vendedor').id;
const u = await api('POST', '/v1/users', adm, { name: 'D1 vendedor', email: 'd1@a.test', password: 'Mat12345!', role_ids: [vend] });
const exp = new Date(Date.now() + 3600e3).toISOString();
const motivos = [
  ['a'.repeat(1000), 'leads'],
  ['Plantao de fim de semana para atendimento de campanha, com motivo normal e espacos entre as palavras.', 'conversations'],
  ['https://exemplo.test/' + 'x'.repeat(300) + '?id=123', 'all'],
];
for (const [reason, scope] of motivos) {
  const r = await api('POST', '/v1/access-exceptions', adm, { user_id: u.body.id, scope, reason, expires_at: exp });
  log(`[dados] liberacao ${scope} (motivo ${reason.length} caracteres) -> HTTP ${r.status}`);
}

const browser = await chromium.launch({ channel: 'chrome', headless: true });
async function measure(label, width, height, shotName) {
  const ctx = await browser.newContext({ viewport: { width, height }, locale: 'pt-BR' });
  const page = await ctx.newPage();
  await page.goto(WEB + '/login');
  await page.getByLabel('E-mail').fill('admin@exemplo.crm.local');
  await page.getByLabel('Senha').fill('Admin123!');
  await page.getByRole('button', { name: 'Entrar' }).click();
  await page.waitForURL((x) => !x.pathname.startsWith('/login'));
  await page.goto(WEB + '/settings/access-exceptions');
  await page.getByText('Liberacoes de acesso').first().waitFor();
  await page.waitForTimeout(2000);
  const m = await page.evaluate(() => {
    window.scrollTo(5000, 0);
    return { inner: window.innerWidth, scrollWidth: document.documentElement.scrollWidth, bodyScrollWidth: document.body.scrollWidth, scrollX: window.scrollX };
  });
  await page.evaluate(() => window.scrollTo(0, 0));
  const ok = m.scrollWidth <= m.inner && m.scrollX === 0;
  results.push({ label, ok, m });
  log(`[${label}] viewport ${width}x${height} | scrollWidth=${m.scrollWidth}px bodyScrollWidth=${m.bodyScrollWidth}px innerWidth=${m.inner}px scrollX apos rolar=${m.scrollX} | sem transbordamento horizontal: ${ok ? 'SIM' : 'NAO'}`);
  if (shotName) { await page.screenshot({ path: `${OUT}/${DAY}-${shotName}.png`, fullPage: true }); log(`[${label}] screenshot ${DAY}-${shotName}.png`); }
  await ctx.close();
  return ok;
}

try {
  // controle ANTES: arquivo do HEAD (sem a correcao)
  fs.writeFileSync(`${FE}/${FILE}`, original);
  await new Promise((r) => setTimeout(r, 2500));
  const before = await measure('ANTES (main, sem correcao) 1280x900', 1280, 900, 'd1-antes-sem-correcao-1280x900');
  // DEPOIS: correcao
  fs.writeFileSync(`${FE}/${FILE}`, fixed);
  await new Promise((r) => setTimeout(r, 2500));
  const a1 = await measure('DEPOIS (com a correcao) 1280x900', 1280, 900, 'd1-corrigido-1280x900');
  const a2 = await measure('DEPOIS (com a correcao) 390x844 (mobile)', 390, 844, 'd1-corrigido-390x844');
  log(`\n[RESUMO D1] antes sem transbordamento: ${before} (esperado false) | depois 1280x900: ${a1} | depois 390x844: ${a2}`);
} finally {
  fs.writeFileSync(`${FE}/${FILE}`, fixed); // garante a correcao restaurada
  await browser.close();
}
