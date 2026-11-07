# Segurança das dependências

Como as dependências do `crm-backend` e do `crm-frontend` são mantidas sem vulnerabilidade conhecida em produção ([D-090](../00-governance/decision-register.md#d-090--proteção-da-api-dependências-rate-limiting-cabeçalhos-de-segurança-e-documentação)).

## 1. Regra

- Dependência de produção com vulnerabilidade **alta ou crítica** bloqueia o CI (`npm audit --omit=dev --audit-level=high`, job próprio nos dois repositórios).
- Moderadas e as de desenvolvimento aparecem no relatório e são tratadas na atualização seguinte, sem bloquear.
- Nunca `npm audit fix --force` às cegas: ele aceita major de qualquer pacote, inclusive rebaixamentos sem sentido.
- `overrides` só com justificativa técnica registrada na tabela da seção 3. Override sem linha na tabela é defeito.

## 2. Situação em 06/11/2026

| Repositório | Produção | Desenvolvimento |
|---|---|---|
| crm-backend | **0** (antes: 24 — 2 críticas, 13 altas, 9 moderadas) | 16 (8 baixas, 8 moderadas: `jest`, `eslint`/`typescript-eslint`, `@nestjs/cli`) |
| crm-frontend | 0 | — |

**Atualizações do backend (Frente 1 do hardening):**

| Pacote | De | Para | Motivo |
|---|---|---|---|
| `@nestjs/common`, `core`, `platform-express`, `testing` | 10.4 | 11.2.8 | `@nestjs/core` (injeção), `body-parser`, `multer`, `file-type` |
| `@nestjs/swagger` | 7.4 | 11.4.8 | `js-yaml`, `lodash` |
| `@nestjs/config` | 3.3 | 4.0.4 | `lodash` |
| `@nestjs/terminus` | 10.2 | 11.1.1 | depende de `@nestjs/core` 10 |
| `@nestjs/bullmq` | 10.2 | 11.0.5 | idem |
| `@nestjs/jwt` | 10.2 | 11.0.2 | compatibilidade com o Nest 11 |
| `@nestjs/cli`, `schematics` | 10 | 11 | compatibilidade |
| `bcrypt` | 5.1.1 | 6.0.0 | remove `@mapbox/node-pre-gyp` e `tar` (crítica); binários pré-compilados, hashes compatíveis |
| `joi` | 17.13.3 | 17.13.9 | protótipo e regex |
| `nestjs-pino` | 4.1 | 4.6.1 | compatibilidade com o Nest 11 |
| `proxy-addr`, `body-parser`, `qs`, `brace-expansion` | — | dentro da faixa | `npm audit fix` sem `--force` (proxy-addr: falsificação de IP, crítica) |

**Por que a linha 11 e não a 12 do NestJS.** A 12 é ESM puro (`"type": "module"`); o backend e os testes (Jest + ts-jest) são CommonJS. A 11 corrige as mesmas vulnerabilidades e continua recebendo correções. Migrar para a 12 é uma frente própria.

**Efeitos do Express 5 tratados no código:** curinga de rota nomeado (`forRoutes('{*path}')`); o roteador interno passou de `app._router` para `app.router` (usado só em teste). Não há parâmetros de query no formato `a[b]`, então o parser de query mais simples do Express 5 não muda o contrato.

**Node:** `engines` passa a `>=20.11.0` (exigência do Nest CLI 11). Imagem Docker `node:20-bookworm-slim` e CI com Node 22 atendem.

## 3. Overrides em vigor (crm-backend)

| Override | Por que existe | Por que é seguro | Quando remover |
|---|---|---|---|
| `@nestjs/platform-express` → `multer` 2.5.0 | O 11.2.8 fixa `multer` 2.4.0 (DoS) | Mesma major; é a versão que o próprio NestJS 12 adotou; importação de Leads coberta por e2e | Quando o `platform-express` da linha 11 subir o `multer` |
| `exceljs` → `uuid` `$uuid` (11.1.1) | `exceljs` 4.4.0 pede `uuid` ^8 (verificação de limites em v3/v5/v6) | O `exceljs` só chama `v4()` por `require`, que a uuid 11 mantém em CommonJS; leitura de planilhas coberta por e2e | Nova versão do `exceljs` ou troca da biblioteca |
| `@prisma/config` → `deepmerge-ts` ^8.0.2 | Prisma 6.19.3 fixa 7.1.5 (estouro de pilha) | Só é chamado para carregar `prisma.config.ts`, que o projeto não tem; usa a função `deepmerge`, mantida na v8 | Migração para o Prisma 7 |

## 4. Como atualizar

1. `npm audit --omit=dev --json` e separar diretas de transitivas.
2. Para cada uma, procurar a menor versão corrigida compatível (`npm view <pacote> versions`), preferindo a mesma major.
3. Atualizar `package.json` e o lockfile juntos; `npm audit fix` sem `--force` para o que está dentro da faixa.
4. Override só pelo critério da seção 1, com linha na tabela da seção 3.
5. Rodar typecheck, lint, unitários, integração, e2e completos e build (mesma sequência do CI) e repetir o `npm audit`.
