# Runbook — cadastros iniciais das empresas (origens de Lead e pipeline padrão)

Decisão: [D-094](../00-governance/decision-register.md#d-094--cadastro-manual-de-lead-e-cadastros-iniciais-da-empresa). Sem origem de Lead, a empresa não cria Lead; sem pipeline, não cria Oportunidade. Desde 06/11/2026, toda empresa nova recebe os cadastros no provisionamento (`npm run tenant:provision-trial`) e no seed de desenvolvimento. Este runbook cobre as **empresas que já existiam**.

## 1. O que é criado

- Origens: Indicação, Site, Telefone, Redes sociais, Evento, Outro.
- Pipeline Padrão (padrão da empresa) com as etapas Novo, Em negociação, Proposta enviada, Ganho (ganho) e Perdido (perda).
- Fonte única no código: `crm-backend/prisma/tenant-catalogs.ts`.

## 2. Regras de segurança do passo

- Só cria o que falta. Nunca altera, apaga nem reativa nada.
- Origem com o mesmo nome (sem distinção de maiúsculas), ativa ou desativada, não é criada de novo: uma origem que a empresa desativou não volta.
- O pipeline só é criado se a empresa **não tiver nenhum** pipeline ativo.
- Motivos de perda e de desqualificação ([D-099](../00-governance/decision-register.md#d-099--motivos-de-perda-e-de-desqualificação-em-listas-por-empresa)): "Outro" é garantido nas duas listas (a migration já o cria); os demais motivos padrão só entram numa lista em que a empresa **nunca cadastrou** motivo próprio, mesmo que depois o tenha excluído. Os motivos padrão ainda aguardam confirmação do responsável: rode com `--dry-run` e confira antes.
- Uma empresa por execução, em transação única.

## 3. Execução

Em ambiente real: só com autorização explícita do responsável e backup recente (D-059). Primeiro a simulação, depois a gravação:

```bash
npm run tenant:seed-catalogs -- --tenant <id-da-empresa> --dry-run
npm run tenant:seed-catalogs -- --tenant <id-da-empresa>
```

A simulação mostra as origens que seriam criadas e se o pipeline seria criado, sem gravar nada. O `DATABASE_URL` do ambiente precisa estar definido; confira host e banco antes (`npx prisma migrate status`).

Em desenvolvimento, `npm run db:seed` (ou `db:setup`) já aplica nas duas empresas de exemplo.

## 4. Conferência

```sql
SELECT t.name,
       (SELECT count(*) FROM lead_sources s WHERE s.tenant_id = t.id AND s.deleted_at IS NULL) AS origens,
       (SELECT count(*) FROM pipelines p WHERE p.tenant_id = t.id AND p.deleted_at IS NULL) AS pipelines
FROM tenants t WHERE t.id = '<id-da-empresa>';
```

**Situação:** testado só em banco descartável; não executado em nenhum ambiente real.
