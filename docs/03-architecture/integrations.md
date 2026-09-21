# Integrações

## 1. Princípio: abstração de canal

Nenhum módulo de negócio (CRM, Atendimento) conhece detalhes de um provedor específico. Toda integração de comunicação implementa a interface `ChannelAdapter` descrita em [architecture.md](architecture.md) seção 4. Isso é o que permite trocar de provedor de telefonia ou WhatsApp sem alterar regra de negócio, e é tratado como requisito de arquitetura, não opcional.

## 2. Telefonia *(fora de escopo — D-070)*

> **Nota de escopo ([D-070](../00-governance/decision-register.md#d-070--definição-de-produto-crm-comercial--atendimentoconversas--whatsapp-sem-call-center-telefônico), 2026-09-21)**: o produto não é um Call Center telefônico; não há integração de telefonia prevista no roadmap (a Fase 5 agora é WhatsApp/Conversas). O conteúdo abaixo é mantido por rastreabilidade — só seria retomado por uma nova decisão de escopo.

| Opção | Natureza | Observação |
|---|---|---|
| Provedor de voz via SIP/tronco + gateway (ex. Asterisk/FreeSWITCH próprio) | Auto-hospedado | Mais controle, mais complexidade operacional |
| Provedor de voz em nuvem (CPaaS, ex. Twilio-like) | Terceirizado | Mais rápido de integrar, custo por uso, menos controle sobre telefonia legada |

[D-010](../00-governance/decision-register.md#d-010--provedor-de-telefonia) (`ADIADO` — decidir antes da **Fase 5**). Não bloqueia as Fases 1, 2, 3 e 4: o MVP não integra telefonia ([D-015](../00-governance/decision-register.md#d-015--escopo-oficial-do-mvp)), apenas registra atendimentos manualmente.

O que a arquitetura precisa garantir desde já é apenas a abstração `TelephonyAdapter`, com implementações plugáveis (`AsteriskAdapter`, `TwilioAdapter`, `ProviderXAdapter`). Critério de escolha quando a Fase 5 chegar: suportar click-to-call, webhooks de eventos de chamada (iniciada/atendida/encerrada) e gravação. A escolha vira um ADR específico. Não integrar nenhum provedor antes da Fase 5 sem necessidade de negócio validada.

Eventos mínimos exigidos do provedor: `call.ringing`, `call.answered`, `call.ended` (com duração e disposição/motivo de encerramento quando disponível), `call.recording.available`.

## 3. WhatsApp / Mensageria

| Opção | Natureza | Observação |
|---|---|---|
| WhatsApp Business Platform (API oficial, via BSP) | Oficial | Compliance, templates aprovados, mais estável para produção, custo por conversa |
| Evolution API (ou similar não-oficial) | Não oficial | Mais barato/flexível para começar, risco de bloqueio pelo WhatsApp, não recomendado como única via em produção para operação crítica |

[D-011](../00-governance/decision-register.md#d-011--provedor-de-whatsapp) (`ADIADO` — decidir antes da **Fase 6**; não bloqueia o MVP). **Direção já definida**: o produto SaaS comercial usa **WhatsApp Business Platform oficial ou BSP oficial** como canal primário. O produto principal não pode depender de solução não oficial — Evolution API e similares, se usados, ficam restritos a ambiente de teste/POC, nunca como única via em produção, dado o risco de bloqueio do número.

O que falta decidir é apenas *qual* BSP, o que exige cotação comercial. A abstração `ChannelAdapter` cobre as operações necessárias: `sendMessage()`, `receiveWebhook()`, `sendTemplate()`, `getMedia()`.

Elementos modelados: Mensagens, Conversas, Anexos, Áudios, Templates (para mensagens ativas fora da janela de 24h, exigido pela política do WhatsApp), Webhooks (recebimento e status de entrega), Falhas e Reprocessamento, Idempotência (ver [../02-business/business-rules.md](../02-business/business-rules.md) BR-19 a BR-21).

## 4. E-mail e SMS

Fora do MVP como canal de atendimento em tempo real; a abstração de canal já contempla que possam ser adicionados como mais um `ChannelAdapter` no futuro sem mudança estrutural. Provedor: [D-040](../00-governance/decision-register.md#d-040--provedor-de-e-mailsms) (`ADIADO` — quando esses canais entrarem no roadmap, pós-Fase 6).

## 5. Padrão de tratamento de webhook (todos os provedores)

1. Validar assinatura/segredo do provedor.
2. Persistir o payload bruto antes de processar (permite reprocessamento/auditoria).
3. Normalizar para o modelo interno via o `ChannelAdapter` correspondente.
4. Aplicar idempotência por identificador externo do evento.
5. Enfileirar processamento (não processar de forma síncrona dentro da requisição do webhook) — resposta HTTP rápida ao provedor, processamento real no worker.

## 6. Falhas de integração externa

- Indisponibilidade de um provedor não deve derrubar o restante do sistema — chamadas a provedores externos passam por timeout curto desde a primeira integração e, quando aplicável, circuit breaker ([D-039](../00-governance/decision-register.md#d-039--circuit-breaker-para-provedores-externos), `ADIADO`: biblioteca/abordagem se decide na Fase 5, com um provedor real em mãos).
- Falhas de envio (mensagem/chamada) ficam visíveis ao usuário com status claro ("Falha no envio"), nunca falham silenciosamente.
