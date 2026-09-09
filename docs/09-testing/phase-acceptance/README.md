# Phase Acceptance

Um arquivo `phase-XX.md` por fase do [roadmap](../../10-roadmap/roadmap.md), criado **no
fechamento** dessa fase (não no início). Cada arquivo é o registro formal de aceite: a matriz
spec↔implementação↔teste↔MAT, as divergências encontradas e corrigidas, as decisões tomadas,
e o veredito final.

Isto é o que substitui "declarar a fase aprovada" numa mensagem de chat — o veredito vive aqui,
versionado, referenciável, e o chat aponta para ele em vez de repetir o conteúdo.

## Regra

- Não escrever um `phase-XX.md` antes da fase estar de fato pronta para fechamento — não é um
  plano, é um registro do que foi verificado.
- Nunca reabrir/editar um `phase-XX.md` já publicado para mudar o veredito silenciosamente —
  se algo depois invalida o aceite, registrar isso como um achado novo (no Decision Register
  ou num ADR), com uma nota neste arquivo apontando para lá, não uma edição que apaga o
  histórico.
- `CLAUDE.md` de cada repositório referencia o `phase-XX.md` correspondente em vez de repetir
  o conteúdo — mantém o `CLAUDE.md` objetivo (ver `crm-spec/CLAUDE.md`).

## Índice

| Fase | Arquivo | Veredito |
|---|---|---|
| Fase 1 — Fundação técnica | [phase-01.md](phase-01.md) | 🟢 Aprovada |
| Fase 2 — Auth/Usuários/Tenants | [phase-02.md](phase-02.md) | ver arquivo |
