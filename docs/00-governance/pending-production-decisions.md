# Decisões pendentes antes de produção — propostas (06/11/2026)

Levantamento feito no hardening de 06/11/2026. **Nada aqui é decisão**: cada item continua com o status do [Decision Register](decision-register.md) até o responsável pelo produto aprovar, e só então é registrado lá. As propostas são recomendações técnicas.

| Decisão | Status hoje | Risco de seguir sem decidir | Proposta recomendada | Depende do responsável |
|---|---|---|---|---|
| [D-025](decision-register.md#d-025--secrets-management-em-produção) — segredos em produção | `PROPOSTO` | `JWT_ACCESS_SECRET`, `DATABASE_URL` e futuras credenciais de canal sem dono nem rotação definidos; vazamento de um `.env` expõe tudo | Variáveis da plataforma de deploy, com acesso restrito por pessoa; rotação do `JWT_ACCESS_SECRET` documentada (derruba os access tokens em até 15 min, sem perder sessões de refresh); cofre dedicado antes da Fase 5 | Escolha da plataforma de deploy e de quem tem acesso aos segredos |
| [D-027](decision-register.md#d-027--ambiente-de-staging) — staging | `PROPOSTO` | Migrations e runbooks (domínios D-088, `users:read` D-089, `citext` D-092) testados só em banco descartável; primeiro teste real seria em produção | Staging com a mesma topologia de produção e dados fictícios, antes do primeiro cliente; todo `migrate deploy` passa por lá antes | Custo e prazo do ambiente |
| [D-028](decision-register.md#d-028--retenção-de-backup) — retenção de backup | `VALIDAÇÃO DE NEGÓCIO` | Sem prazo, não há como dimensionar armazenamento nem responder a contrato/LGPD | Diário com 30 dias + mensal com 12 meses, criptografado e fora da região do banco | Prazo exigido por contrato e pela política de LGPD (D-047) |
| [D-029](decision-register.md#d-029--cadência-de-teste-de-restore) — teste de restore | `PROPOSTO` | Backup nunca restaurado não é backup | Aprovar como está (a cada release relevante de infraestrutura e no mínimo trimestral), com registro de quanto tempo levou | Aprovação e um responsável pela execução |
| [D-036](decision-register.md#d-036--acesso-de-suporte-do-super-admin-a-dados-de-tenant) — acesso de suporte | `VALIDAÇÃO DE NEGÓCIO` | Sem política, suporte que precisar ver dado do cliente só consegue por acesso direto ao banco, sem trilha | Manter "sem acesso" até a Central Administrativa; quando houver, "Support Access Controlado" (motivo, tempo limitado, só leitura, auditoria, aceite do tenant) | Política comercial e jurídica de suporte |
| [D-047](decision-register.md#d-047--fluxo-operacional-de-lgpd-titular-de-dados) — LGPD do titular | `VALIDAÇÃO DE NEGÓCIO` | Pedido de acesso/correção/exclusão sem processo; dados pessoais copiados (ex.: nome em notificações) sem prazo de guarda | Processo manual assistido no início (pedido ao Admin do tenant, executado pela plataforma com registro), self-service depois | Política jurídica e prazos de resposta |
| [D-021](decision-register.md#d-021--plataforma-de-ci) / [D-052](decision-register.md#d-052--ci-dentro-de-cada-repositório) — CI | `PROPOSTO` | Baixo: o CI já roda no GitHub Actions, agora com e2e (D-052, 06/11/2026) | Aprovar GitHub Actions com um workflow por repositório; exigir o CI verde para merge no `main` (proteção de branch) | Aprovação; ativar a proteção de branch no GitHub |
| [D-064](decision-register.md#d-064--rf-03-redefinição-de-senha-fase-e-fluxo-indefinidos) — redefinição de senha | **`DECIDIDO` em 06/11/2026** | — | Troca da própria senha e link do Admin implementados; "esqueci minha senha" por e-mail espera a D-040 | Nada além da D-040 |

## Validações de implementação ainda sem aceite humano

- Limites iniciais de rate limiting ([security.md](../03-architecture/security.md) §4.1): escolha técnica, configurável. Revisar com o uso real (ex.: escritório grande atrás de um só IP).
- Bloqueio por conta de até 15 minutos (D-090): permite que alguém bloqueie temporariamente o login de outra pessoa errando a senha de propósito.
- Validade de 24 h do link de senha e "um link ativo por usuário" (D-064).
- Aceite humano das D-084 a D-093 e dos MATs pendentes.

## Fora desta entrega (continuam no roadmap, sem início)

Central Administrativa do Platform Owner; verificação de domínio próprio; papéis personalizados pela interface (D-050); importação de Leads pela interface; telas dos controles de disponibilidade que ainda não têm; upload seguro de logo e favicon; checkout e planos pagos; monitoramento real de armazenamento; escopo por equipe e filial (D-058); "esqueci minha senha" e troca de e-mail por e-mail (D-040); NestJS 12 (ESM) e Prisma 7; F4.8 e Fase 5.
