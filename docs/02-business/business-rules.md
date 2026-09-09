# Regras de Negócio

## 1. Multi-tenancy e escopo
- BR-01: Todo registro de negócio (lead, cliente, oportunidade, atendimento, etc.) pertence a exatamente um `tenant_id`, atribuído no momento da criação e imutável.
- BR-02: Nenhuma consulta pode retornar dados de mais de um tenant, mesmo para o Super Admin da plataforma (que opera fora do escopo de tenant, ver [personas.md](../01-product/personas.md)).

## 2. Leads
- BR-03: Um lead sempre tem uma origem (`source`) registrada no momento da criação (formulário, importação, atendimento receptivo, manual, integração).
- BR-04: Um lead não pode ser convertido em oportunidade sem estar vinculado a um Cliente (novo ou existente, resolvido por deduplicação — ver BR-08).
- BR-05: Distribuição automática de leads (round-robin) só considera vendedores ativos e dentro do horário de atendimento configurado do tenant.
- BR-06: Lead desqualificado exige motivo de desqualificação (lista configurável pelo tenant). O que acontece quando o contato retorna — novo lead ou reabertura do anterior — é `[VALIDAÇÃO DE NEGÓCIO NECESSÁRIA]` ([D-033](../00-governance/decision-register.md#d-033--reabertura-de-lead-desqualificado-br-06), resolver antes da Fase 3). Não presumir nenhum dos dois comportamentos na implementação antes da validação.

## 3. Clientes / Deduplicação
- BR-07: Um Cliente é identificado unicamente, dentro do tenant, por documento (CPF/CNPJ) quando disponível; na ausência, por telefone normalizado (E.164) ou e-mail.
- BR-08: Ao criar um lead/atendimento com dado de contato já existente no tenant, o sistema deve sugerir vínculo ao cliente existente em vez de duplicar.

## 4. Oportunidades / Pipeline
- BR-09: Toda oportunidade pertence a um único Pipeline e está em exatamente uma Etapa a cada momento. Se mover para uma etapa fora da ordem é livre, bloqueado ou permitido com justificativa é `[VALIDAÇÃO DE NEGÓCIO NECESSÁRIA]` ([D-032](../00-governance/decision-register.md#d-032--ordem-de-movimentação-entre-etapas-do-pipeline), resolver antes da Fase 3).
- BR-10: Mudança de etapa gera um registro de histórico imutável (etapa anterior, etapa nova, usuário, timestamp).
- BR-11: Oportunidade Ganha ou Perdida é um estado terminal — não pode retornar ao pipeline; uma nova negociação com o mesmo cliente é uma nova Oportunidade.
- BR-12: Oportunidade Perdida exige um motivo de perda, de uma lista configurável pelo tenant.
- BR-13: A obrigatoriedade do valor monetário da oportunidade (sempre obrigatório, sempre opcional, ou configurável por pipeline) é `[VALIDAÇÃO DE NEGÓCIO NECESSÁRIA]` ([D-034](../00-governance/decision-register.md#d-034--obrigatoriedade-de-valor-em-oportunidade-br-13), resolver antes da Fase 3). O campo existe no modelo desde já; o que falta é a regra.

## 5. Atendimento / Call Center
- BR-14: Um operador só recebe atendimentos de filas às quais está associado e enquanto seu status é "Disponível".
- BR-15: Toda chamada/atendimento finalizado exige uma disposição (resultado), de uma lista configurável por fila/tenant.
- BR-16: Tempo em status "Pausa" além do limite configurado gera alerta ao supervisor (não bloqueia o operador no MVP).
- BR-17: Gravação de chamada, quando habilitada, deve ser associada ao registro de atendimento e ao cliente, respeitando retenção definida em [../03-architecture/security.md](../03-architecture/security.md).
- BR-18: SLA de fila (tempo máximo de espera) é configurável por fila; violação gera evento para métricas e alerta ao supervisor — não bloqueia a operação.

## 6. Omnichannel
- BR-19: Toda mensagem recebida (WhatsApp/outros) é vinculada a uma Conversa; uma Conversa é vinculada a um Cliente/Lead por identificador de canal (ex.: telefone).
- BR-20: Processamento de webhook de canal é idempotente por `external_message_id` — reentrega do provedor não duplica mensagem.
- BR-21: Falha de envio de mensagem aciona retry com backoff (ver [../03-architecture/architecture.md](../03-architecture/architecture.md)); após esgotar tentativas, o status fica "Falha" visível ao usuário.

## 7. Auditoria e exclusão
- BR-22: Exclusão de Cliente, Lead, Oportunidade e Atendimento é sempre lógica (soft delete) — nunca remoção física via API.
- BR-23: Toda criação, edição e exclusão de dado sensível gera entrada de auditoria imutável (usuário, ação, entidade, timestamp, tenant).
- BR-24: Dados de auditoria não são editáveis nem excluíveis por nenhum papel de tenant.

## 8. Permissões
- BR-25: Toda operação de escrita valida, nesta ordem: (1) usuário autenticado, (2) tenant do recurso == tenant do usuário, (3) permissão do papel para a ação, (4) escopo de dado (próprio/equipe/filial/tenant).
- BR-26: Falha em qualquer etapa da BR-25 retorna erro padronizado sem vazar existência do recurso a quem não tem permissão de leitura (retornar 404 em vez de 403 quando apropriado — ver [../05-api/api-guidelines.md](../05-api/api-guidelines.md)).
