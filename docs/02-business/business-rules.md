# Regras de Negócio

## 1. Multi-tenancy e escopo
- BR-01: Todo registro de negócio (lead, cliente, oportunidade, atendimento, etc.) pertence a exatamente um `tenant_id`, atribuído no momento da criação e imutável.
- BR-02: Nenhuma consulta pode retornar dados de mais de um tenant, mesmo para o Super Admin da plataforma (que opera fora do escopo de tenant, ver [personas.md](../01-product/personas.md)).

## 2. Leads
- BR-03: Um lead sempre tem uma origem (`source`) registrada no momento da criação (formulário, importação, atendimento receptivo, manual, integração).
- BR-04: Um lead não pode ser convertido em oportunidade sem estar vinculado a um Cliente (novo ou existente, resolvido por deduplicação — ver BR-08).
- BR-05: Distribuição automática de leads (round-robin) só considera consultores/vendedores **ativos**, **disponíveis** (BR-14) e dentro do horário de atendimento configurado do tenant.
  - **Estado da implementação (Fase 3.4)**: o round-robin implementado considera apenas usuário ativo, do mesmo tenant, com a permissão `leads:update`. **Disponibilidade (BR-14) e horário de atendimento ainda não filtram** — divergência registrada em [D-071](../00-governance/decision-register.md#d-071--disponibilidade-de-consultoratendente-para-distribuição-automática); evolução prevista: ativo + disponível + permissão, sem vincular a disponibilidade a um papel específico.
- BR-06: Lead desqualificado exige motivo de desqualificação (lista configurável pelo tenant). Quando o contato retorna, o sistema **reabre o lead desqualificado existente** — não cria um novo lead para o mesmo contato ([D-033](../00-governance/decision-register.md#d-033--reabertura-de-lead-desqualificado-br-06), `DECIDIDO`). O histórico e o motivo da desqualificação anterior permanecem preservados.

## 3. Clientes / Deduplicação
- BR-07: Um Cliente é identificado unicamente, dentro do tenant, por documento (CPF/CNPJ) quando disponível; na ausência, por telefone normalizado (E.164) ou e-mail.
- BR-08: Ao criar um Cliente com dado de contato (documento/telefone/e-mail) já existente no tenant, o sistema **bloqueia a criação automática de um duplicado**: retorna `409` com os candidatos encontrados (um ou mais), cabendo ao usuário decidir usar o cliente existente ou seguir por um fluxo explicitamente permitido pela aplicação. O sistema nunca escolhe automaticamente entre múltiplos candidatos ([D-067](../00-governance/decision-register.md#d-067--deduplicação-de-customer-é-bloqueante-409), `DECIDIDO`).

## 4. Oportunidades / Pipeline
- BR-09: Toda oportunidade pertence a um único Pipeline e está em exatamente uma Etapa a cada momento. Mover para uma etapa fora da ordem (pulando uma ou mais etapas) é **permitido**, desde que acompanhado de **justificativa obrigatória** ([D-032](../00-governance/decision-register.md#d-032--ordem-de-movimentação-entre-etapas-do-pipeline), `DECIDIDO`). O pipeline não é um fluxo rigidamente sequencial.
- BR-10: Mudança de etapa gera um registro de histórico imutável (etapa anterior, etapa nova, usuário, timestamp, e a justificativa quando houver salto de etapa — BR-09/D-032).
- BR-11: Oportunidade Ganha ou Perdida é um estado terminal — não pode retornar ao pipeline; uma nova negociação com o mesmo cliente é uma nova Oportunidade.
- BR-12: Oportunidade Perdida exige um motivo de perda, de uma lista configurável pelo tenant.
- BR-13: O valor monetário da oportunidade **não é obrigatório na criação**; passa a ser obrigatório quando a oportunidade estiver numa etapa individualmente marcada como exigindo valor (`stages.requires_value`, ver [entities.md](../04-database/entities.md)) — a regra vale só para a etapa marcada, **sem propagar** por ordem para etapas anteriores ou posteriores, e nunca por nome fixo de etapa ([D-034](../00-governance/decision-register.md#d-034--obrigatoriedade-de-valor-em-oportunidade-br-13), `DECIDIDO`).

## 5. Atendimento / Conversas e disponibilidade
> O produto é CRM Comercial + Atendimento/Conversas + WhatsApp + futuro Omnichannel — **não** um Call Center telefônico ([D-070](../00-governance/decision-register.md#d-070--definição-de-produto-crm-comercial--atendimentoconversas--whatsapp-sem-call-center-telefônico)). "Atendimento" aqui são conversas/interações comerciais, principalmente via WhatsApp, e as funções relacionadas a Lead/Cliente.

- BR-14: Um consultor/atendente só recebe distribuição automática de novos Leads/atendimentos enquanto estiver **ativo e disponível**.
  - Usuário ativo, porém **indisponível**, não integra o conjunto elegível da distribuição automática.
  - Disponibilidade é um estado comercial/de atendimento do usuário — **não** está atrelada a um papel específico e é reutilizável por qualquer distribuição (leads, conversas de WhatsApp, filas de atendimento, futuros canais do Omnichannel).
  - Pendente de modelagem: o conceito já existe na especificação (`agent_status_log`, RF-15), mas sua representação final, a semântica dos estados e quem os altera dependem de validação de negócio — ver [D-071](../00-governance/decision-register.md#d-071--disponibilidade-de-consultoratendente-para-distribuição-automática). A distribuição de leads da Fase 3.4 ainda não aplica esta regra (ver BR-05).
- BR-15: Todo atendimento/conversa finalizado exige uma disposição (resultado), de uma lista configurável pelo tenant (e por fila, quando houver filas de atendimento). *Pendência de negócio ([D-070](../00-governance/decision-register.md#d-070--definição-de-produto-crm-comercial--atendimentoconversas--whatsapp-sem-call-center-telefônico)): definir o que caracteriza uma Conversa "finalizada" e se toda conversa exige disposição.*
- BR-16: Um consultor/atendente pode se colocar em **pausa** (indisponibilidade voluntária — regra de disponibilidade, não de operador de telefonia). Tempo em pausa além do limite configurado gera alerta ao gestor/supervisor; não bloqueia o consultor no MVP. *Pendência de negócio: valor/forma de configuração do limite e quais estados de disponibilidade contam como "pausa" (dependem de [D-071](../00-governance/decision-register.md#d-071--disponibilidade-de-consultoratendente-para-distribuição-automática)); o alerta depende da primeira versão de Notificações (Fase 4).*
- ~~BR-17~~: **removida** ([D-070](../00-governance/decision-register.md#d-070--definição-de-produto-crm-comercial--atendimentoconversas--whatsapp-sem-call-center-telefônico)). O produto não prevê gravação de chamada nem telefonia; não há regra substituta. O identificador permanece reservado para não renumerar as regras seguintes.
- BR-18: SLA de fila/atendimento/conversa (tempo máximo de espera até ser atendido) é configurável; violação gera evento para métricas e alerta ao supervisor — não bloqueia a operação. *Pendência de negócio: pontos de medição do SLA de uma Conversa e onde é configurado (por fila, canal ou tenant).*

## 6. Conversas e Omnichannel
> WhatsApp é um **canal de conversa** dentro do CRM (não "Call Center"); as regras abaixo valem para o WhatsApp e para canais futuros.

- BR-19: Toda mensagem recebida (WhatsApp/outros) é vinculada a uma Conversa; uma Conversa é vinculada a um Cliente/Lead por identificador de canal (ex.: telefone).
- BR-20: Processamento de webhook de canal é idempotente por `external_message_id` — reentrega do provedor não duplica mensagem.
- BR-21: Falha de envio de mensagem aciona retry com backoff (ver [../03-architecture/architecture.md](../03-architecture/architecture.md)); após esgotar tentativas, o status fica "Falha" visível ao usuário.

## 7. Auditoria e exclusão
- BR-22: Exclusão de Cliente, Lead, Oportunidade e Atendimento é sempre lógica (soft delete) — nunca remoção física via API. Vendedor/Consultora não tem permissão de excluir esses registros; a exclusão fica restrita a Gerente/Admin, sem fluxo de aprovação nesta fase ([D-035](../00-governance/decision-register.md#d-035--regra-de-aprovação-para-exclusão-por-vendedor), `DECIDIDO`).
- BR-23: Toda criação, edição e exclusão de dado sensível gera entrada de auditoria imutável (usuário, ação, entidade, timestamp, tenant).
- BR-24: Dados de auditoria não são editáveis nem excluíveis por nenhum papel de tenant.

## 8. Permissões
- BR-25: Toda operação de escrita valida, nesta ordem: (1) usuário autenticado, (2) tenant do recurso == tenant do usuário, (3) permissão do papel para a ação, (4) escopo de dado (próprio/equipe/filial/tenant).
- BR-26: Falha em qualquer etapa da BR-25 retorna erro padronizado sem vazar existência do recurso a quem não tem permissão de leitura (retornar 404 em vez de 403 quando apropriado — ver [../05-api/api-guidelines.md](../05-api/api-guidelines.md)).
