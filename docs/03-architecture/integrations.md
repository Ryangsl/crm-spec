# Integrações

## 1. Princípio: abstração de canal

Nenhum módulo de negócio (CRM, Atendimento) conhece detalhes de um provedor específico. Toda integração de comunicação implementa a interface `ChannelAdapter` descrita em [architecture.md](architecture.md) seção 4. Isso é o que permite trocar de provedor de telefonia ou WhatsApp sem alterar regra de negócio, e é tratado como requisito de arquitetura, não opcional.

## 2. Telefonia

| Opção | Natureza | Observação |
|---|---|---|
| Provedor de voz via SIP/tronco + gateway (ex. Asterisk/FreeSWITCH próprio) | Auto-hospedado | Mais controle, mais complexidade operacional |
| Provedor de voz em nuvem (CPaaS, ex. Twilio-like) | Terceirizado | Mais rápido de integrar, custo por uso, menos controle sobre telefonia legada |

`[DECISÃO PENDENTE]`: provedor específico de telefonia para o MVP. Critério de escolha: suportar click-to-call, webhooks de eventos de chamada (iniciada/atendida/encerrada) e gravação. A escolha vira um ADR específico quando definida — a arquitetura não depende de qual for escolhido, apenas exige que ele se encaixe no `ChannelAdapter`.

Eventos mínimos exigidos do provedor: `call.ringing`, `call.answered`, `call.ended` (com duração e disposição/motivo de encerramento quando disponível), `call.recording.available`.

## 3. WhatsApp / Mensageria

| Opção | Natureza | Observação |
|---|---|---|
| WhatsApp Business Platform (API oficial, via BSP) | Oficial | Compliance, templates aprovados, mais estável para produção, custo por conversa |
| Evolution API (ou similar não-oficial) | Não oficial | Mais barato/flexível para começar, risco de bloqueio pelo WhatsApp, não recomendado como única via em produção para operação crítica |

Recomendação: iniciar com a API oficial (via BSP) como canal primário assim que o módulo WhatsApp entrar no roadmap (Fase 6); Evolution API pode ser um adapter alternativo para ambientes de teste/POC, nunca a única opção em produção, dado o risco de bloqueio. `[DECISÃO PENDENTE]`: confirmar BSP e se Evolution API entra como adapter suportado oficialmente ou fica apenas como referência de compatibilidade da abstração.

Elementos modelados: Mensagens, Conversas, Anexos, Áudios, Templates (para mensagens ativas fora da janela de 24h, exigido pela política do WhatsApp), Webhooks (recebimento e status de entrega), Falhas e Reprocessamento, Idempotência (ver [../02-business/business-rules.md](../02-business/business-rules.md) BR-19 a BR-21).

## 4. E-mail e SMS

Fora do MVP como canal de atendimento em tempo real; a abstração de canal já contempla que possam ser adicionados como mais um `ChannelAdapter` no futuro sem mudança estrutural. `[DECISÃO PENDENTE]`: provedor de e-mail/SMS quando entrar em roadmap.

## 5. Padrão de tratamento de webhook (todos os provedores)

1. Validar assinatura/segredo do provedor.
2. Persistir o payload bruto antes de processar (permite reprocessamento/auditoria).
3. Normalizar para o modelo interno via o `ChannelAdapter` correspondente.
4. Aplicar idempotência por identificador externo do evento.
5. Enfileirar processamento (não processar de forma síncrona dentro da requisição do webhook) — resposta HTTP rápida ao provedor, processamento real no worker.

## 6. Falhas de integração externa

- Indisponibilidade de um provedor não deve derrubar o restante do sistema — chamadas a provedores externos passam por timeout curto e, quando aplicável, circuit breaker (`[DECISÃO PENDENTE]`: biblioteca/abordagem, avaliar na Fase 6/backend).
- Falhas de envio (mensagem/chamada) ficam visíveis ao usuário com status claro ("Falha no envio"), nunca falham silenciosamente.
