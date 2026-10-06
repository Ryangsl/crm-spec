# Casos de Uso e Fluxos Críticos

Casos de uso principais, por área. Formato: ator, pré-condição, fluxo principal, exceções. Fluxos de negócio detalhados (com regras) estão em [../02-business/workflows.md](../02-business/workflows.md).

## 1. CRM / Vendas

### UC-01 Captação e distribuição de lead
- **Ator**: Sistema (integração/formulário) ou Vendedor (cadastro manual).
- **Pré-condição**: origem do lead configurada (formulário, importação, atendimento receptivo, integração).
- **Fluxo**: lead é criado ou importado → quando aplicável, o sistema aplica a regra de distribuição (round-robin, por fila, manual) → lead é atribuído a um vendedor/equipe → notificação ao responsável *(Notificações ainda não definidas — `VN-11`)*.
- **Variante (não é erro)**: **lead sem proprietário** ([D-075](../00-governance/decision-register.md#d-075--lead-sem-proprietário-é-um-estado-legítimo-do-negócio), BR-29) — cadastro/importação sem consultor associado (ex.: lista com centenas de pessoas) ou nenhum consultor elegível na regra de distribuição → o lead permanece sem proprietário (`owner_id` nulo), aguardando atribuição/distribuição posterior. Na Fase 3 o único registro é o evento de auditoria `lead.unassigned` ([D-069](../00-governance/decision-register.md#d-069--alerta-de-lead-não-atribuído-só-auditoria-sem-módulo-de-notificações)). *Alerta ao gerente: pendente (`VN-11`); política de distribuição posterior: pendente (`VN-16`).*

### UC-02 Qualificação de lead e conversão em oportunidade
- **Ator**: Vendedor/Operador.
- **Pré-condição**: lead atribuído ao usuário.
- **Fluxo**: usuário registra contato/qualificação → decide avançar → sistema converte lead em Oportunidade vinculada a um Cliente (novo ou existente) → oportunidade entra na primeira etapa do Pipeline.
- **Exceção**: lead desqualificado → usuário registra motivo de desqualificação, lead não vira oportunidade agora. Se o contato retornar depois, o mesmo lead é **reaberto** (não é criado um lead novo) — [D-033](../00-governance/decision-register.md#d-033--reabertura-de-lead-desqualificado-br-06), `DECIDIDO`.

### UC-03 Condução de oportunidade pelo pipeline
- **Ator**: Vendedor/Gerente.
- **Fluxo**: oportunidade avança/retrocede entre etapas configuráveis do pipeline → cada mudança de etapa pode disparar tarefas/notificações → oportunidade é marcada como Ganha ou Perdida (com motivo).
- **Exceção**: movimentação para etapa fora da ordem (pulando etapas) é permitida, mas exige justificativa obrigatória, registrada no histórico da oportunidade — [D-032](../00-governance/decision-register.md#d-032--ordem-de-movimentação-entre-etapas-do-pipeline), `DECIDIDO`.

### UC-04 Follow-up e agenda
- **Ator**: Vendedor.
- **Fluxo**: usuário agenda tarefa/compromisso vinculado a lead/oportunidade/cliente → sistema notifica antes do vencimento → usuário registra resultado.

## 2. Atendimento / Conversas

No MVP, o atendimento é **registrado manualmente** (o operador atende por fora e lança a interação, alimentando o histórico unificado). Os casos UC-05 a UC-07 descrevem fluxos de telefonia (chamada, discagem, escuta) que estão **fora de escopo** ([D-070](../00-governance/decision-register.md#d-070--definição-de-produto-crm-comercial--atendimentoconversas--whatsapp-sem-call-center-telefônico): o produto não é um Call Center telefônico) e devem ser reescritos como fluxos de conversa antes da implementação; UC-08 (WhatsApp) é da **Fase 5** — ver [D-015](../00-governance/decision-register.md#d-015--escopo-oficial-do-mvp).

### UC-05 Atendimento receptivo (chamada) — *Fase 5*
- **Ator**: Operador.
- **Pré-condição**: operador logado em uma fila, status "Disponível".
- **Fluxo**: chamada chega à fila → sistema distribui ao operador disponível (ordem/skill da fila) → tela de atendimento abre com histórico do cliente (se identificado por número) → operador atende → registra disposição → chamada é encerrada e fica associada ao histórico do cliente.
- **Exceção**: cliente não identificado → operador cria/vincula cadastro durante o atendimento. Fila cheia/SLA estourado → chamada é ofertada callback.

### UC-06 Atendimento ativo (discagem) — *Fase 5*
- **Ator**: Operador/Vendedor.
- **Fluxo**: usuário seleciona contato (manualmente ou via lista de discagem) → sistema origina a chamada (click-to-call) → chamada é conectada → operador registra disposição ao final.
- **Exceção**: número inválido/sem resposta → disposição automática "não atendido", pode gerar tarefa de nova tentativa.

### UC-07 Supervisão em tempo real — *Fase 5*
- **Ator**: Supervisor.
- **Fluxo**: supervisor visualiza painel com status de todos os operadores e filas em tempo real → identifica operador em dificuldade/fila com SLA em risco → intervém (escuta, sussurro, transferência ou assume o atendimento).
- **Exceção**: operador cai (perde conexão) — sistema marca operador como offline e libera fila.

### UC-08 Atendimento via WhatsApp — *Fase 5*
- **Ator**: Operador/Vendedor.
- **Fluxo**: mensagem recebida de um contato → sistema cria/atualiza uma Conversa vinculada ao Cliente/Lead (por telefone) → mensagem entra na fila do canal → operador responde pela interface unificada → conversa fica no histórico do cliente.
- **Exceção**: mensagem de número não vinculado a nenhum cadastro → vira lead/atendimento avulso até vinculação manual. *(Texto anterior a [D-070](../00-governance/decision-register.md#d-070--definição-de-produto-crm-comercial--atendimentoconversas--whatsapp-sem-call-center-telefônico)/BR-28 e ainda não validado contra "Lead ≠ Cliente" — pendência `WA-06` em [../03-architecture/whatsapp-architecture.md](../03-architecture/whatsapp-architecture.md).)*

## 3. Administração

### UC-09 Configuração inicial do tenant
- **Ator**: Administrador da empresa.
- **Fluxo**: admin cadastra filiais/equipes → cadastra usuários e papéis → configura filas → configura pipeline(s) → configura canais (telefonia/WhatsApp).

### UC-10 Auditoria
- **Ator**: Admin/Diretor.
- **Fluxo**: usuário consulta trilha de auditoria (quem alterou o quê, quando) filtrando por módulo/usuário/período.

### UC-11 Alterar disponibilidade — *Fase 4*
- **Ator**: Consultor/atendente (próprio estado); Admin/Gerente (Treinamento de terceiros).
- **Pré-condição**: o tenant habilitou a disponibilidade (`crm.availability.enabled`, por Admin via `tenant_settings:update`). Sem isso o seletor não aparece e a API bloqueia a alteração (estados já registrados são preservados).
- **Fluxo**: o consultor escolhe Disponível, Indisponível, Pausa ou Almoço → o sistema grava o estado atual e o histórico e audita; só quem está **Disponível** participa da distribuição automática ([D-071](../00-governance/decision-register.md#d-071--disponibilidade-de-consultoratendente-para-distribuição-automática)). Admin/Gerente colocam um consultor em Treinamento e depois o retiram manualmente; o consultor não entra nem sai de Treinamento.
- **Exceções**: usuário sem registro é Indisponível; não há transição automática por login/logout nem pelo Sistema; ficar Indisponível não retira a carteira; Treinamento não tem duração automática.

## 4. Fluxo crítico ponta a ponta (referência)

```
Lead recebido
  → distribuição (regra de fila/round-robin)
  → contato (ligação/WhatsApp)
  → qualificação
  → oportunidade (pipeline)
  → negociação (etapas)
  → venda (ganho) | perda (motivo)
  → pós-venda (backoffice/atendimento)
```

Este fluxo é o eixo central do produto e orienta a modelagem de dados ([../04-database/entities.md](../04-database/entities.md)) e os eventos de domínio ([../03-architecture/architecture.md](../03-architecture/architecture.md)).
