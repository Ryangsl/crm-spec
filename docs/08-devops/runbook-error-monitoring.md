# Runbook — captura de erros (Sentry)

Decisão: [D-101](../00-governance/decision-register.md#d-101--captura-de-erros-sentry-desligada-por-padrão-e-regras-de-privacidade) (`PROPOSTO`). A captura existe no crm-backend e no crm-frontend e está **desligada por padrão**: sem DSN, nenhum SDK é carregado e nada sai do servidor nem do navegador. Ligar em qualquer ambiente depende do responsável (conta, plano, região de dados, retenção e DSN por ambiente, ver a D-101).

## 1. Variáveis

| Onde | Variável | Padrão | Observação |
|---|---|---|---|
| Backend (ambiente) | `SENTRY_DSN` | vazio = desligado | Em `NODE_ENV=test` nunca liga |
| | `SENTRY_ENVIRONMENT` | `NODE_ENV` | ex.: `staging`, `production` |
| | `SENTRY_RELEASE` | vazio | ex.: o commit publicado |
| | `SENTRY_TRACES_SAMPLE_RATE` | `0` | Só erros. Acima de 0 não tem efeito hoje (nenhuma instrumentação de desempenho está ligada); ligá-la exige nova decisão |
| Frontend (build) | `VITE_SENTRY_DSN` | vazio = desligado | Lida no **build**: mudar exige novo build. O DSN fica visível no JavaScript publicado (é assim no navegador; ele só permite enviar eventos) |
| | `VITE_SENTRY_ENVIRONMENT` | modo do Vite (`production`) | |
| | `VITE_SENTRY_RELEASE` | vazio | |

O `Dockerfile` do frontend hoje só repassa `VITE_API_URL` como `ARG`; ao ligar pela imagem, as `VITE_SENTRY_*` precisam ser repassadas do mesmo jeito.

## 2. Ligar num ambiente

1. **No Sentry (responsável):** um projeto para a API e outro para a web; em cada um, ativar *Prevent Storing of IP Addresses* e o *Data Scrubber* do servidor (segunda camada); na web, *Allowed Domains* com os endereços das empresas; retenção conforme a D-101.
2. **Backend:** definir as variáveis e reiniciar. O log `Captura de erros ligada (ambiente ...)` confirma.
3. **Frontend:** build com as `VITE_SENTRY_*` e publicação.
4. **Política de conteúdo (CSP):** hoje nem o `nginx.conf` nem o `index.html` do frontend definem CSP, então nada bloqueia o envio. Se o proxy de produção passar a definir, `connect-src` precisa incluir o host de ingestão do DSN (o domínio depois do `@`). A CSP da API (`default-src 'none'`, D-090) não interfere: o backend envia de servidor.
5. **PWA:** o service worker (Workbox, `generateSW`) não intercepta o envio (POST para outra origem) e o arquivo do SDK fica fora do precache. Sem rede, a captura não carrega e o app segue normal.
6. **Desligar:** remover o DSN (backend: reiniciar; frontend: novo build).

## 3. O que é enviado e o que nunca é

**Enviado (só o inesperado):** backend, 5xx que não é exceção de domínio, falha definitiva de job (importação de Leads) e erro fatal do processo; frontend, erro de renderização (a pessoa vê "Algo deu errado" e "Recarregar") e erro não tratado da janela. Em cada evento: tipo do erro, mensagem mascarada, pilha (arquivo, função e linha, sem código nem variáveis), ambiente, versão e as tags `source`, `route` (padrão: `/v1/leads/:id`, `/leads/:id`), `method`, `status`, `request_id`, `tenant_id`, `user_id`, `queue`, `job_name`, `job_id`, `mechanism`, `prisma_code`. No frontend, só `source`, `route` e o id do usuário.

**Nunca enviado:** respostas 4xx (validação, 401 de sessão, 403, 404, 409, 422) nem exceções de domínio; corpo da requisição, cookies, cabeçalhos (`authorization`, `cookie`, `set-cookie` e o resto da lista de redação dos logs), query string, fragmento da URL (`#token=` do link de redefinição de senha), e-mail, nome, telefone, documento, IP, nome da máquina, `job.data`, texto das mensagens do Prisma (só o código), breadcrumbs (SQL, requisições, cliques, navegação), replay de tela e o access token. E-mails, números longos e tokens que aparecerem em mensagens de erro são mascarados.

## 4. Validar em ambiente não produtivo

Depois de ligar, num ambiente sem dados reais:

- **Backend**, na pasta da aplicação (onde está `dist/`), com as mesmas variáveis do serviço:

  ```bash
  node -e "const m=require('./dist/common/monitoring/monitoring.config');m.createErrorReporter(m.loadMonitoringConfig(process.env),process.env.NODE_ENV).then(async(r)=>{r.captureException(new Error('Teste de captura D-101'),{source:'process',mechanism:'manual-test'});await r.flush(5000);console.log(r.enabled?'enviado':'desligado')})"
  ```

  Passa pelo mesmo caminho dos erros reais (inclusive a limpeza) e não afeta a API.
- **Frontend:** abrir `/login?email=teste@exemplo.com#token=abc` e, no console do navegador, `setTimeout(() => { throw new Error('Teste de captura D-101') })`.
- **No Sentry:** os dois eventos aparecem; conferir que não há seção de requisição, que o usuário só tem id, que as tags são as da seção 3 e que nem `teste@exemplo.com` nem `abc` aparecem.

Sem conta, um DSN apontando para um coletor HTTP local (`http://chave@127.0.0.1:<porta>/1`) mostra os envelopes; foi assim que a entrega foi validada.

**Situação (13/11/2026):** implementado (crm-backend e crm-frontend, branches `feat/error-monitoring`), validado com transporte falso e coletor local; **não ligado em nenhum ambiente**.
