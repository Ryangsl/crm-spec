# WhatsApp — Pacote de decisões para abrir o Gate da Fase 5

> **Natureza**: proposta para decisão do responsável pelo produto, preparada em 2026-11-16. **Nada aqui está `DECIDIDO`** e nada autoriza implementação: o [Gate de entrada](whatsapp-architecture.md#10-gate-de-entrada-para-implementação) continua **fechado** até a aprovação explícita. Registro no Decision Register: [D-102](../00-governance/decision-register.md#d-102--gate-da-fase-5-abertura-em-duas-etapas-e-pacote-de-decisões-proposta) (`PROPOSTO`).
>
> **Base**: [whatsapp-architecture.md](whatsapp-architecture.md) (Gate §10, fronteira §3, arquitetura §6, catálogo `WA-01`–`WA-30`), [D-011](../00-governance/decision-register.md#d-011--provedor-de-whatsapp), [D-024](../00-governance/decision-register.md#d-024--convenção-de-variáveis-de-ambiente-de-provedores), [D-025](../00-governance/decision-register.md#d-025--secrets-management-em-produção), D-070 a [D-076](../00-governance/decision-register.md#d-076--fronteira-f4f5-diretrizes-de-planejamento-da-fase-4-aprovadas-a1a3), [D-081](../00-governance/decision-register.md#d-081--núcleo-de-conversas-agnóstico-ao-canal-f46) e o `main` do `crm-backend` (`3cf8f58`, conferido em 2026-11-16).
>
> **Legenda**: 🔑 indispensável para o primeiro teste real · ⏳ pode esperar, com padrão provisório seguro (vale só até a decisão) · **Rec.** = recomendação do time. Valores, prazos e limites da Meta mudam: conferir a documentação vigente em cada passo ([whatsapp-architecture.md §5](whatsapp-architecture.md#5-o-que-pertence-exclusivamente-à-fase-5)).

## 1. Resumo

- **Gate hoje**: nenhum dos 10 critérios atendido por completo; **6 parciais** (G2, G4, G5, G7, G8, G9) e **4 sem início** (G1, G3, G6, G10). A Fase 4 entregou boa parte do que a Fase 5 consome (conversas manuais, disponibilidade, horário comercial, linha do tempo, notificações); o texto original do Gate ainda dizia "F4 não iniciada".
- **Para o primeiro teste real**: 8 respostas do responsável (§3.1), 5 providências fora do código (§5, itens 1–5) e um PR de documentação do time (G1, G2, G3, G4 e G10) antes da primeira linha de código.
- **Proposta central (DR-01)**: abrir o Gate em **duas etapas** — **A. teste controlado** (número de teste da Meta, uma empresa de teste, dados fictícios, só texto, só respostas dentro da janela de 24 h) e **B. primeiro cliente** (todo o restante do Gate). Hoje o Gate exige tudo antes de qualquer código.

## 2. Estado real do Gate (2026-11-16)

| # | Critério | Situação | O que já existe | Falta — responsável | Falta — time (depois das decisões) |
|---|---|---|---|---|---|
| G1 | Arquitetura definida | ❌ | Proposta das §3 e §6 | Aprovar a arquitetura revisada (DR-01, DR-02, DR-04) | Ajustar a §6 ao que a F4 entregou de fato (mensagens dentro do módulo `conversations`; distribuição só de Leads; `ChannelAdapter` na F5 por D-076/A2) e promovê-la a `DECIDIDO` |
| G2 | Modelo de dados validado | 🟡 | `conversations`/`messages` agnósticos em [entities.md](../04-database/entities.md) e no schema (F4.6); disponibilidade (D-077); `access_exceptions` (D-083) | Aprovar o modelo (DR-04, DR-06, DR-08) | Documentar `channel_accounts`, `channel_webhook_events`, os campos aditivos de `messages` (id externo, status de entrega, erro) e de `conversations` (conta, contato externo) e o destino de `whatsapp_messages` (DR-19) |
| G3 | Fluxos definidos | ❌ | Fluxo de conversa manual ([workflows.md §7.3](../02-business/workflows.md), UC-14) | DR-06, DR-07, DR-08 | Reescrever [workflows.md §5](../02-business/workflows.md) e UC-08 com as respostas e os padrões provisórios |
| G4 | Regras de negócio validadas | 🟡 | WA-12 resolvida (D-082/D-083); WA-11 só no formato do horário; WA-07, WA-08 e WA-14 em parte (§2.1) | Etapa A: DR-06 a DR-08. Etapa B: DR-11 a DR-15, DR-17, DR-18 | Novas regras em [business-rules.md](../02-business/business-rules.md) |
| G5 | Decisões críticas registradas | 🟡 | WA-24 resolvida (§2.1); princípio de WA-02 (D-074) | DR-04 (WA-03), DR-09 | Registrar no Decision Register |
| G6 | Provedor/API definido | ❌ | Direção oficial (D-011); o legado já fala com a Meta Cloud API | DR-02, DR-03 e a conta de teste (§5) | Revisar D-024/D-025 conforme DR-04 |
| G7 | Fronteira F4/F5 aprovada | 🟡 | A1–A3 aprovadas (D-076); o núcleo foi entregue na F4 (F4.6), então o deslocamento para a F5.0 não se aplica mais | Aprovar a §3 corrigida | Corrigir a §3 (`ChannelAdapter` e identidade de contato por canal saíram da F4, D-076/A2) e reescrever as funcionalidades da Fase 5 no [roadmap](../10-roadmap/roadmap.md) |
| G8 | F4 concluída no que a F5 consome | 🟡 | Itens 3, 5, 7, 9 e 11 da §4 entregues; 1, 2 e 8 em parte; 4 e 10 não; 6 movido para a F5 (tabela abaixo) | Aceitar que a própria F5 entregue os itens 4 e 10 (DR-06, DR-11) | Execução por empresa fora de HTTP já existe (worker da importação de Leads, D-096); falta o "ator Sistema" (auditoria com `userId` nulo, WA-23) |
| G9 | Legado sob controle | 🟡 atendido para a entrada | Congelado (D-073) e **desligado por padrão com bloqueio efetivo** ([D-097](../00-governance/decision-register.md#d-097--módulo-communications-desligado-por-padrão-até-a-f50), 2026-11-10) | DR-19 (destino) | Reconciliação na F5.0 |
| G10 | OpenAPI antes do código | ❌ | Teste de contrato da API no backend (RNF-16, registrado no crm-spec #25) passa a cobrar o contrato | — | Contratos do webhook, da conta de canal e do envio no [openapi.yaml](../05-api/openapi.yaml) |

**G8 — itens da [§4](whatsapp-architecture.md#4-o-que-a-fase-4-precisa-fornecer-para-o-whatsapp)**

| Item | Situação | Onde |
|---|---|---|
| 1. Conversation/Message normalizados | 🟡 vínculos dedicados, `direction` e canal neutro ✅; status de entrega, id externo e anexo entram na F5 de forma aditiva (D-081 item 3) | F4.6 |
| 2. Ciclo de vida | 🟡 abrir, encerrar, reabrir e atribuição manual ✅; transferência e disposição ❌ (VN-12) | F4.6 |
| 3. Disponibilidade | ✅ | F4.2, D-077 |
| 4. Distribuição generalizada | ❌ só Leads (D-078); conversas não são distribuídas | — |
| 5. `business_hours` | ✅ formato, restrição de acesso e liberação excepcional | F4.1, F4.7, D-082/D-083 |
| 6. `ChannelAdapter` + adapter de teste | ➡️ movido para a F5 (D-076/A2) | F5.0 |
| 7. Interações/linha do tempo | ✅ (mensagens ficam fora da timeline, D-081 item 10) | F4.4, D-079, D-095 |
| 8. Notificações v1 | 🟡 o módulo existe; só `lead.assigned` (D-080) | F4.5 |
| 9. Visibilidade de conversas | ✅ por empresa (tenant-only) | D-081 item 8 |
| 10. Identidade de contato por canal | ❌ | DR-06 |
| 11. Não estender o legado | ✅ | D-073, D-097 |

### 2.1 Itens do catálogo resolvidos, total ou parcialmente, por decisões posteriores ao discovery

| WA | Resolvido por | O que continua aberto |
|---|---|---|
| WA-02 | D-074 (princípio) | Titular da conta, planos, quantidade de números, onboarding, tela (DR-09, DR-10) |
| WA-07 | D-076/A3 e D-081 itens 2 e 4: FKs dedicadas; conversa nunca converte Lead | Uma conversa aberta por contato; destino na conversão do Lead (VN-14) — DR-08 |
| WA-08 | D-081 item 5: no núcleo, atribuição só manual | Regra para conversa vinda do WhatsApp — DR-11 |
| WA-10 | Para Leads: D-075/D-078 (ninguém elegível = sem dono) | Para conversas — DR-11 |
| WA-11 | D-082 item 6: formato do horário | O que acontece com mensagem recebida fora do horário — DR-12 |
| WA-12 | ✅ D-082/D-083 (liberação excepcional implementada no F4.7) | — |
| WA-14 | D-081 item 4: `open`/`closed`; encerrada não recebe mensagem | Disposição (BR-15); reabrir × abrir nova — DR-08, DR-14 |
| WA-23 | D-081 item 10: só o ciclo de vida da conversa é auditado; mensagens fora do `audit_log` | `userId` de evento de sistema (técnico; proposta: nulo, como já previsto na §6.8) |
| WA-24 | ✅ D-081 itens 8–9 (por empresa; `conversations:*`), D-089, D-084 e D-101 (sem dado pessoal em log e no Sentry) | Segredo do webhook — DR-04 |
| WA-25 | D-101 (`PROPOSTO`, desligado) | Métricas de fila e de webhook (F5.7) |
| WA-26 | D-090: limite de requisições por rota, endereço e conta, no Redis | Cota por empresa no canal (F5.7) |
| WA-29 | D-080: o módulo de notificações existe | Aviso de "nova conversa/mensagem" (F5.6) |
| WA-30 | D-073 e D-097 (desligado e bloqueado) | Destino — DR-19 |

Sem avanço desde o discovery: WA-01, WA-03 a WA-06, WA-09, WA-13, WA-15 a WA-22, WA-27 e WA-28.

## 3. Decisões do responsável

### 3.1 Indispensáveis para o primeiro teste (🔑)

**DR-01 — Podemos fazer um teste real controlado antes de fechar todas as regras de atendimento?** (regra do próprio Gate, D-072)
- **A. Gate único (como hoje)**: nenhuma linha de código antes de G1–G10 completos. Impacto: o primeiro teste só depois das 19 decisões e de um ambiente de staging.
- **B. Duas etapas.** **Etapa A — teste controlado**: número de teste da Meta, uma empresa de teste, dados fictícios e celulares da equipe, só texto, só respostas dentro da janela de 24 h, sem tela de configuração e sem cliente real; os critérios do Gate valem no escopo dessa etapa e as regras ⏳ seguem com o padrão provisório documentado. **Etapa B — primeiro cliente**: G1–G10 completos antes de qualquer número ou dado real de cliente. Impacto: teste em poucas semanas, sem fixar regra de negócio por acidente.
- **C. Teste com API não oficial.** Descartada: contraria D-011.
- **Rec.: B.** Na etapa A as regras de segurança valem por inteiro: canal oficial, configuração por empresa, segredos cifrados, webhook assinado e idempotente.

**DR-02 — Conectamos direto na Meta ou contratamos um intermediário oficial (BSP)?** (WA-01, D-011)
- **A. Meta Cloud API direta.** Custo: só o da Meta (cobrança por mensagem de modelo, conforme categoria e país; mensagens livres dentro da janela de atendimento de 24 h não são cobradas — conferir a tabela vigente para o Brasil); número de teste gratuito. Prazo: número de teste no mesmo dia. Trabalho: o onboarding das empresas clientes fica com a plataforma (programa de provedor de tecnologia da Meta, que exige verificação da empresa e revisão do app). O código legado já fala com a Cloud API e pode ter partes reaproveitadas na F5.0.
- **B. BSP oficial** (por exemplo Twilio, 360dialog, Gupshup, Infobip, Zenvia, Blip). Custo: mensalidade e/ou margem por número ou mensagem, sob cotação. Prazo: contrato e cadastro (dias a semanas). Ganho: suporte, onboarding de clientes pronto e, em alguns, faturamento centralizado. Formato de API e webhook varia por BSP.
- **C. Cloud API agora e BSP só se o onboarding ou o suporte virarem gargalo** — o `ChannelAdapter` torna a troca um novo adapter, sem mexer no núcleo.
- **Rec.: C.** Cloud API direta na etapa A e na F5.0–F5.3; a escolha comercial definitiva (direto × BSP) fica para antes do primeiro cliente, junto da DR-09.

**DR-03 — Quem cria a conta Meta e o número de teste, e em nome de quem?** (G6)
- **A.** O responsável, no **portfólio empresarial da plataforma** (Meta Business do CRM Universal, com o CNPJ do MEI), cria um app de desenvolvedor com o produto WhatsApp e usa o **número de teste gratuito** da Meta. Exige: conta pessoal no Facebook do administrador, até 5 celulares da equipe cadastrados como destinatários e um usuário do sistema com token permanente (o token temporário do painel vale 24 h). A verificação da empresa não é exigida para o teste.
- **B.** Usar já o número real de uma empresa piloto. Exige verificação, número próprio para a API e nome de exibição aprovado; mistura teste com cliente real.
- **C.** Conta pessoal de um desenvolvedor. Vínculo frágil; a conta precisa ser da plataforma.
- **Rec.: A**, e começar **já** a verificação da empresa na Meta, que leva tempo e é exigida para produção e para atender empresas clientes.

**DR-04 — Onde guardamos a chave de acesso ao WhatsApp de cada empresa?** (WA-03, D-024, D-025)
- **A. No banco, cifrada por conta de canal** (AES-256-GCM), com a chave-mestra fora do banco (variável da plataforma de deploy, D-025) e versão de chave para rotação; nunca devolvida pela API, nunca em log nem no Sentry; toda troca auditada.
- **B. Cofre externo** (Vault, Doppler, Infisical ou o da nuvem), com só a referência no banco. Mais robusto em escala; exige infraestrutura e custo agora, sem ambiente de deploy definido (D-027).
- **C. Variáveis de ambiente por empresa** (como o legado). Descartada: credencial global, redeploy a cada cliente, contraria D-074.
- **Rec.: A**, atrás de uma interface de cofre que permita migrar para B. As variáveis `WHATSAPP_*` (D-024) passam a nomear só configuração **da plataforma** (id e segredo do app Meta, token de verificação do webhook, versão da API), nunca credencial de empresa. Revê a sugestão de "cofre dedicado antes da Fase 5" de [pending-production-decisions.md](../00-governance/pending-production-decisions.md); [security.md §5](security.md#5-dados-sensíveis-e-criptografia) já admite cifrar em repouso.

**DR-05 — Onde o sistema roda para a Meta conseguir nos avisar das mensagens?** (o webhook exige URL pública com HTTPS e certificado válido; não há ambiente de deploy, [D-027](../00-governance/decision-register.md#d-027--ambiente-de-staging))
- **A. Túnel seguro temporário** (por exemplo Cloudflare Tunnel) até a máquina de desenvolvimento, publicando **só** a rota do webhook, ligado só durante o teste e com dados fictícios. Custo zero; pronto em horas.
- **B. Staging mínimo numa VPS** com domínio e HTTPS ([deployment.md](../08-devops/deployment.md), D-027). Mais próximo de produção; custo mensal e escolhas de hospedagem, domínio e acesso aos segredos.
- **C. Produção.** Descartada para teste.
- **Rec.: A** na etapa A; **B** como condição da etapa B (já era pré-requisito do primeiro cliente, D-027).

**DR-06 — Quando chega mensagem de um telefone, como achamos o cadastro?** (WA-05)
- **A.** Procurar o telefone (E.164) no **Cliente** (telefone principal e contatos) e no **Lead** não convertido. Um resultado: vincula. Nenhum: DR-07. Vários: conversa **"a identificar"** (guarda só o telefone) até um usuário escolher — nunca escolha automática (mesmo princípio da D-067). Lead convertido sai da busca e vale o Cliente ligado a ele; Lead desqualificado é vinculado sem ser reaberto (a reabertura continua manual, D-033).
- **B.** Procurar só em Clientes (mensagem de Lead cai como desconhecida).
- **C.** Escolher o cadastro mais recente. Descartada (D-067).
- **Rec.: A.** Impacto: a conversa "a identificar" amplia, de forma aditiva, o item 2 da D-081 (pelo menos um vínculo) só para conversas de canal; as conversas manuais continuam exigindo vínculo. Risco técnico conhecido: o identificador do WhatsApp de alguns celulares brasileiros chega sem o nono dígito — a busca considera as duas formas.

**DR-07 — Mensagem de um número que não está em nenhum cadastro** (WA-06; BR-03, BR-28, BR-29)
- **A.** Criar um **Lead** com origem "WhatsApp" (nome do perfil, quando vier) e a conversa vinculada a ele; o Lead segue a regra de criação de hoje (D-068/D-078: distribuição quando há elegível, senão sem dono, D-075). Consistente com Lead ≠ Cliente e com o texto histórico do UC-08. Impacto: conta no limite de Leads do plano (D-085); número errado vira Lead (descartável pela desqualificação).
- **B.** Conversa "a identificar" (só o telefone); um usuário vincula a um cadastro ou cria o Lead. Menos cadastro indevido, mais trabalho manual.
- **C.** Ignorar a mensagem. Descartada: perde mensagem.
- **Rec.: A**, caindo em **B** quando o plano não permitir criar o Lead — a mensagem nunca é perdida.

**DR-08 — A pessoa manda mensagem de novo: continua a mesma conversa ou abre outra?** (WA-07, WA-14)
- **A.** No máximo **uma conversa aberta por contato e por número da empresa**; a mensagem nova entra nela; se a última estiver encerrada, abre **nova** conversa (as anteriores ficam no histórico).
- **B.** Reabrir a última encerrada. Histórico contínuo, mas mistura atendimentos (atrapalha resultado e SLA futuros).
- **C.** Uma conversa permanente por contato. Sem fronteira entre atendimentos.
- **Rec.: A.** Impacto: cria a unicidade de conversa aberta para conversas de canal (parte de VN-12); uma conversa aberta **não** muda de vínculo se o Lead for convertido (comportamento atual do F4.6; VN-14 segue aberta); a próxima conversa já nasce ligada ao Cliente (DR-06).

### 3.2 Podem esperar (⏳), com padrão provisório seguro na etapa A

**DR-09 — De quem é a conta do WhatsApp de cada empresa cliente: dela ou da plataforma?** (D-074, WA-02) — antes do primeiro cliente
- **A.** A **empresa cliente é a titular** (portfólio Meta, número e pagamento à Meta são dela); o CRM Universal recebe acesso autorizado pelo cadastro incorporado da Meta (como provedor de tecnologia) ou por um BSP. O cliente leva o número se sair; qualidade e limites ficam isolados por empresa.
- **B.** A **plataforma é titular** de todas as contas (números no portfólio do CRM Universal). Faturamento e revenda simples, mas a plataforma responde por todas as mensagens, o problema de um cliente pode afetar os outros e o cliente perde o número ao sair. Contraria o espírito da D-074.
- **C.** Um BSP é titular/faturador, com o CRM Universal como parceiro.
- **Rec.: A.** Consequência técnica: um único app Meta da plataforma recebe os webhooks de todas as contas (o segredo de assinatura é da plataforma); a chave de acesso é por conta (DR-04). **Provisório**: a empresa de teste usa a conta de teste da própria plataforma (DR-03); o modelo guarda credencial por conta, sem assumir o onboarding.

**DR-10 — O WhatsApp entra em quais planos, e quantos números cada empresa pode ter?** (WA-02, D-085) — antes do primeiro cliente
- **A.** Adicional pago, por número. **B.** Incluso nos planos pagos, sem WhatsApp no Trial. **C.** Trial com WhatsApp limitado.
- **Rec.**: decisão comercial do responsável, depois de conhecer o custo da DR-02/DR-09. **Provisório**: o catálogo atual fica (Trial com `whatsapp: false`); só a empresa de teste tem a funcionalidade; **1 número por empresa** na etapa A (o modelo aceita vários, D-074); o processamento respeita `allowsBackgroundWork(empresa, 'whatsapp')`.

**DR-11 — Quem atende uma conversa nova?** (WA-08, WA-09, WA-10)
- **A.** O **dono do cadastro** (Cliente ou Lead), se ativo, com permissão de conversa e Disponível (quando a disponibilidade está ligada); senão, distribuição entre os Disponíveis; ninguém elegível → conversa **sem responsável**, visível em "não atribuídas", sem resposta automática. Quem fica indisponível no meio da conversa continua com ela (como a carteira de Leads, D-071).
- **B.** Sempre distribuição, ignorando o dono. **C.** Sempre manual: um gestor distribui.
- **Rec.: A.** **Provisório: C** — a conversa entra sem responsável e quem tem `conversations:assign` atribui (o que o F4.6 já faz).

**DR-12 — Mensagem recebida fora do horário** (WA-11; WA-12 já resolvida)
- **A.** Recebe e guarda normalmente, sem resposta automática; a restrição de acesso do F4.7 continua valendo para o consultor. **B.** Resposta automática configurável por empresa, uma por conversa e período (é resposta dentro da janela de 24 h, não precisa de modelo; exige o "ator Sistema"). **C.** Descartar a mensagem — descartada.
- **Rec.: A** agora e B como melhoria. **Provisório: A.**

**DR-13 — Transferência de conversa** (WA-13)
- **A.** O consultor transfere a própria conversa para um colega, motivo opcional, histórico de/para. **B.** Só quem tem `conversations:assign` (gestor) reatribui — já existe e é auditado. **C.** Como A, com motivo obrigatório.
- **Rec.: B** no início; A quando a operação pedir. **Provisório: B.**

**DR-14 — O que é encerrar um atendimento** (WA-14, BR-15)
- **A.** Encerramento manual com **resultado opcional**, escolhido numa lista por empresa (como os motivos da D-099). **B.** Resultado obrigatório (BR-15 como escrita). **C.** Encerramento automático depois de um tempo sem mensagens (exige agendamento e "ator Sistema").
- **Rec.: A**; tornar obrigatório depois, se os relatórios pedirem. **Provisório**: encerramento manual sem resultado (F4.6).

**DR-15 — Ociosidade (regra dos 5 minutos)** (WA-15, VN-13, F4.8)
- **A.** Definir depois do primeiro cliente, com uso real. **B.** Definir e implementar antes do primeiro cliente.
- **Rec.: A.** **Provisório**: nenhuma transferência automática.

**DR-16 — Modelos de mensagem e mensagem ativa** (WA-17, WA-20; regra da Meta: fora da janela de 24 h, só modelo aprovado)
- **A.** Modelos criados no gerenciador da Meta e sincronizados no CRM; o Admin escolhe quais podem ser usados. **B.** Modelos criados e enviados para aprovação de dentro do CRM. **C.** Sem mensagem ativa no lançamento, só respostas.
- **Rec.: A.** **Provisório: C** — fora da janela o envio é recusado com aviso claro; modelos entram na F5.4.

**DR-17 — Consentimento para receber mensagens (opt-in/opt-out)** (WA-22) — antes de qualquer mensagem ativa ou automação
- **A.** Registrar o consentimento por contato e por empresa (origem, data, texto aceito), exigi-lo para mensagem ativa e bloquear mensagens ativas depois de um pedido de saída ("SAIR", "PARAR" ou opção na tela). **B.** Exigir só para marketing. **C.** Deixar a responsabilidade no contrato com a empresa cliente, sem registro no CRM.
- **Rec.: A**, validada pelo jurídico (LGPD e política da Meta). **Provisório**: sem mensagem ativa na etapa A (DR-16), logo nenhum envio sem consentimento.

**DR-18 — Por quanto tempo guardamos as mensagens?** (WA-27, D-047)
- **A.** Conteúdo enquanto a empresa for cliente, mais um prazo definido após o fim do contrato; exclusão ou anonimização do titular a pedido, auditada; payload bruto do webhook com prazo curto (só para reprocessar). **B.** Guardar sem prazo. **C.** Não guardar o conteúdo, só metadados — inviabiliza o histórico do CRM.
- **Rec.: A**, com prazos fixados pelo responsável e pelo jurídico (o time sugere 30 dias para o payload bruto). **Provisório**: etapa A só com dados fictícios e celulares da equipe, em banco descartável.

**DR-19 — Destino do módulo legado `communications`** (WA-30, D-073, D-097)
- **A. Substituir**: a nova arquitetura não usa o legado, que continua desligado; reaproveita-se só o cliente HTTP da Meta (com timeout); tabelas e rotas do legado são removidas quando as automações forem redesenhadas (Fase 8). **B. Migrar** `whatsapp_messages` para `messages` e religar as automações sobre a nova arquitetura. **C. Evoluir o legado** — descartada (D-073, D-074).
- **Rec.: A.** **Provisório**: legado desligado e intocado; a F5 não lê dado dele.

## 4. Caminho mais curto até um teste real (proposta)

**Objetivo da etapa A**: enviar e receber mensagem de texto real entre um celular da equipe e o número de teste da Meta, numa empresa de teste, com todas as regras de segurança.

**Pré-condições**: DR-01 a DR-08 aprovadas; §5 itens 1 a 5 providenciados; PR de documentação do crm-spec com G1 (§6 revisada), G2 ([entities.md](../04-database/entities.md)), G3 ([workflows.md §5](../02-business/workflows.md) e UC-08), G4 (regras das DR-06 a DR-08 e padrões provisórios) e G10 (contratos no [openapi.yaml](../05-api/openapi.yaml)); aprovação explícita do Gate da etapa A.

**Incremento técnico mínimo** (F5.0 mínima + F5.1 + fatias da F5.2 e da F5.3; migrations só aditivas, D-081 item 3):

| Bloco | O que entra | Regras que garante |
|---|---|---|
| Conta de canal | `channel_accounts` (empresa, canal, provedor, identificadores da Meta, número, situação, credencial cifrada e versão da chave); cadastro por comando de operador, sem tela, auditado | Por empresa (D-074); segredo cifrado (DR-04) |
| Adapter | `ChannelAdapter` e `WhatsAppCloudAdapter` instanciado por conta, com timeout curto; adapter falso para os testes | RF-22, RNF-05 |
| Webhook | `GET` (desafio) e `POST /v1/webhooks/whatsapp` públicos; corpo bruto só nessa rota; assinatura HMAC da Meta conferida antes de tudo (inválida → 401); payload bruto em `channel_webhook_events`; resposta 200 imediata; fila `whatsapp-inbound` levando só o id do evento; limite de requisições próprio; isento do guard comercial com justificativa (o bloqueio por plano é feito no worker); empresa resolvida pelo identificador do número → conta, nunca pelo `Host` nem por campo do payload; conta desconhecida falha fechado | BR-20, [security.md §7](security.md#7-webhooks), D-002, D-088 |
| Recebimento | Worker no contexto da empresa (mesmo padrão da importação de Leads, D-096) com "ator Sistema" (auditoria com `userId` nulo); `allowsBackgroundWork`; idempotência pelo id externo (único por conta) com teste-e-set; identificação (DR-06, DR-07); conversa (DR-08); mensagem `inbound` | BR-19, BR-20, BR-28 |
| Envio | Consultor responde na conversa aberta, só dentro de 24 h desde a última mensagem do contato (fora: 422 com aviso); mensagem `pending` com chave de idempotência → fila `whatsapp-outbound` → id externo gravado; nova tentativa só para erro transitório; esgotou → `failed` visível | BR-21, [integrations.md §3](integrations.md#3-whatsapp--mensageria) |
| Status de entrega | `sent → delivered → read` ou `failed`, aplicados sem regredir | [whatsapp-architecture.md §6.6](whatsapp-architecture.md#66-fluxo--mensagem-enviada) |
| Tela | Detalhe da conversa mostra o canal, o status de cada mensagem, a falha e o aviso de janela encerrada; polling atual | RNF-04 |
| Testes | Assinatura inválida rejeitada; reentrega não duplica; conta desconhecida descartada; isolamento entre empresas (conta, conversa, mensagem); janela encerrada recusa; falha esgotada visível; segredo nunca na resposta nem em log | [testing-strategy.md](../09-testing/testing-strategy.md) |

**Fica para depois** (etapa B e incrementos seguintes): modelos e mensagem ativa (F5.4, DR-16, DR-17); mídia (F5.5 — na etapa A um anexo recebido vira mensagem de aviso, sem download); tempo real e supervisão (F5.6); distribuição automática de conversas (DR-11); transferência pelo consultor (DR-13); resultado do atendimento (DR-14); ociosidade (DR-15); resposta fora do horário (DR-12); tela de configuração e cadastro incorporado de clientes (DR-09); vários números por empresa; circuit breaker, cota por empresa e retenção automática (F5.7, DR-18); reconciliação do legado (DR-19); BSP.

**Saída da etapa B** (antes do primeiro cliente): G1–G10 completos; DR-09 a DR-19 decididas; staging com HTTPS (D-027); quem acessa os segredos definido (D-025); verificação da empresa na Meta concluída; política de privacidade publicada; D-047 e, se ligada, D-101 resolvidas.

## 5. O que o responsável providencia fora do código

| # | Item | Etapa | Observação |
|---|---|---|---|
| 1 | Conta pessoal no Facebook do administrador e **portfólio empresarial na Meta** (Meta Business) em nome do CRM Universal (CNPJ do MEI) | A | A Meta exige uma pessoa como administradora |
| 2 | **App de desenvolvedor** (tipo empresa) com o produto WhatsApp, que traz o número de teste e uma conta WhatsApp Business de teste | A | Gratuito |
| 3 | Até 5 **celulares da equipe** cadastrados e confirmados como destinatários do número de teste | A | Recebem o código de confirmação |
| 4 | **Usuário do sistema** no portfólio, com token permanente e permissões de mensagens e de gestão do WhatsApp, entregue ao time por canal seguro (nunca em chat ou e-mail em texto) | A | O token temporário do painel vale 24 h |
| 5 | **Endereço público**: conta no serviço de túnel (DR-05) e um subdomínio para o webhook | A | O time cadastra no app a URL e o token de verificação e assina o campo de mensagens |
| 6 | **Verificação da empresa na Meta** (documento do CNPJ, site e domínio com e-mail próprio, telefone) | Iniciar já; exigida na B | Pode levar de dias a semanas; sem ela o limite de mensagens iniciadas pela empresa é baixo |
| 7 | **Hospedagem de staging** (VPS), domínio e certificado HTTPS (D-027) e quem acessa os segredos (D-025) | B | — |
| 8 | **Política de privacidade** publicada (a Meta exige a URL para o app sair do modo de desenvolvimento) e revisão jurídica de consentimento e retenção (DR-17, DR-18, D-047) | B | — |
| 9 | Para cada cliente: número para a API (o uso simultâneo com o app WhatsApp Business depende das regras vigentes da Meta), nome de exibição dentro das regras da Meta, forma de pagamento na Meta ou via BSP e aceite dos termos do WhatsApp Business | B | Conforme DR-09 |
| 10 | Cotação de BSP, se a DR-02 seguir para B | Antes da B | — |

## 6. Depois da aprovação

1. O responsável responde a §3.1 (e, se quiser, a §3.2) item a item.
2. O time passa a `DECIDIDO` os itens aprovados da [D-102](../00-governance/decision-register.md#d-102--gate-da-fase-5-abertura-em-duas-etapas-e-pacote-de-decisões-proposta) e entrega o PR de documentação do Gate (G1–G4, G10).
3. Com a aprovação explícita da etapa A, começa o incremento da §4.
4. A etapa B fecha o restante do Gate antes do primeiro cliente.
