# Deployment / Infraestrutura

## 1. Alvos de ambiente

O sistema deve funcionar em: desenvolvimento local (Windows/Linux), ambiente Linux genérico, VPS, e futuramente cloud gerenciada. Nenhuma decisão do MVP deve travar exclusivamente em um provedor de nuvem específico.

## 2. Infraestrutura inicial (MVP)

- **Docker + Docker Compose** como unidade de deploy — um único host (VPS) executando: Nginx (proxy reverso/TLS), backend (NestJS), frontend (build estático servido via Nginx ou CDN simples), PostgreSQL, Redis.
- **Nginx**: terminação TLS, proxy para a API, servir os assets estáticos do frontend (PWA), cabeçalhos de cache apropriados para service worker/manifest.
- Kubernetes e orquestração avançada são explicitamente **fora de escopo** até haver evidência real de necessidade (ver [../03-architecture/scalability.md](../03-architecture/scalability.md)).

## 3. Variáveis de ambiente e segredos

- Mesmo conjunto de variáveis do [ambiente local](local-development.md), com valores reais nunca versionados.
- Secrets management ([D-025](../00-governance/decision-register.md#d-025--secrets-management-em-produção), `PROPOSTO`, resolver antes da Fase 5): variáveis de ambiente gerenciadas pela plataforma de deploy, com rotação manual documentada; evoluir para cofre dedicado (Vault/Doppler) quando o número de integrações crescer. Até a Fase 5 não há segredo de provedor externo para guardar.

## 4. Migrations em produção

- Migrations do Prisma executadas como etapa explícita do processo de deploy (antes de subir a nova versão da aplicação), nunca automaticamente no boot da aplicação em produção.
- Toda migration é aditiva sempre que possível (nova coluna nullable, depois backfill, depois `NOT NULL` em migration separada) para permitir rollback seguro.

## 5. Backup e restore

- Backup automático diário do PostgreSQL. O **período de retenção** é `[VALIDAÇÃO DE NEGÓCIO NECESSÁRIA]` ([D-028](../00-governance/decision-register.md#d-028--retenção-de-backup), antes do primeiro cliente em produção) — depende de exigência contratual e de LGPD.
- Restore testado a cada release relevante de infraestrutura e no mínimo trimestralmente ([D-029](../00-governance/decision-register.md#d-029--cadência-de-teste-de-restore), `PROPOSTO`). Backup cujo restore nunca foi testado não conta como backup.
- Backups seguem a mesma política de criptografia/isolamento dos dados originais (ver [../03-architecture/security.md](../03-architecture/security.md)).

## 6. Health checks e observabilidade

- `GET /health` (liveness) e `GET /health/ready` (readiness) usados pelo orquestrador/proxy para decidir se uma instância recebe tráfego.
- Logs estruturados (Pino) centralizados; avaliação de stack de observabilidade:

| Ferramenta | Papel | Quando adotar |
|---|---|---|
| Pino | Log estruturado da aplicação | Desde o MVP |
| Sentry (ou equivalente) | Captura de erros/exceções não tratadas | Desde o MVP — essencial para operação de call center em produção |
| Prometheus | Métricas (latência, taxa de erro, tamanho de fila) | A partir do momento em que houver mais de uma instância/necessidade real de dashboard operacional |
| Grafana | Visualização das métricas do Prometheus | Junto com Prometheus |

Nenhuma ferramenta é adicionada sem necessidade concreta (RNF de observabilidade não significa adotar a stack completa no dia 1) — ver [../03-architecture/architecture.md](../03-architecture/architecture.md) seção 6.

## 7. Estratégia de release

- Deploy por versão de imagem/artefato ([D-026](../00-governance/decision-register.md#d-026--registry-de-imagens-docker), `ADIADO`: o registry se escolhe antes do primeiro deploy real — não bloqueia a Fase 1).
- Rollback = subir a versão anterior da imagem; por isso migrations aditivas (seção 4) são um requisito, não uma preferência.
- Ambientes: `production` desde já; `staging` a introduzir quando houver mais de um desenvolvedor/agente atuando em paralelo, ou antes do primeiro cliente real — o que vier primeiro ([D-027](../00-governance/decision-register.md#d-027--ambiente-de-staging), `PROPOSTO`).
