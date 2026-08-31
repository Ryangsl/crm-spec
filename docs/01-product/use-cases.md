# Casos de Uso e Fluxos Críticos

Casos de uso principais, por área. Formato: ator, pré-condição, fluxo principal, exceções. Fluxos de negócio detalhados (com regras) estão em [../02-business/workflows.md](../02-business/workflows.md).

## 1. CRM / Vendas

### UC-01 Captação e distribuição de lead
- **Ator**: Sistema (integração/formulário) ou Vendedor (cadastro manual).
- **Pré-condição**: origem do lead configurada (formulário, importação, atendimento receptivo, integração).
- **Fluxo**: lead é criado → sistema aplica regra de distribuição (round-robin, por fila, manual) → lead é atribuído a um vendedor/equipe → notificação ao responsável.
- **Exceção**: nenhum vendedor disponível na regra de distribuição → lead cai em fila "não atribuído" e gera alerta ao gerente.

### UC-02 Qualificação de lead e conversão em oportunidade
- **Ator**: Vendedor/Operador.
- **Pré-condição**: lead atribuído ao usuário.
- **Fluxo**: usuário registra contato/qualificação → decide avançar → sistema converte lead em Oportunidade vinculada a um Cliente (novo ou existente) → oportunidade entra na primeira etapa do Pipeline.
- **Exceção**: lead desqualificado → usuário registra motivo de perda, lead é encerrado sem virar oportunidade.

### UC-03 Condução de oportunidade pelo pipeline
- **Ator**: Vendedor/Gerente.
- **Fluxo**: oportunidade avança/retrocede entre etapas configuráveis do pipeline → cada mudança de etapa pode disparar tarefas/notificações → oportunidade é marcada como Ganha ou Perdida (com motivo).
- **Exceção**: tentativa de mover para etapa fora da ordem permitida — bloqueado ou exige justificativa, conforme configuração do pipeline (`[DECISÃO PENDENTE]`).

### UC-04 Follow-up e agenda
- **Ator**: Vendedor.
- **Fluxo**: usuário agenda tarefa/compromisso vinculado a lead/oportunidade/cliente → sistema notifica antes do vencimento → usuário registra resultado.

## 2. Atendimento / Call Center

### UC-05 Atendimento receptivo (chamada)
- **Ator**: Operador.
- **Pré-condição**: operador logado em uma fila, status "Disponível".
- **Fluxo**: chamada chega à fila → sistema distribui ao operador disponível (ordem/skill da fila) → tela de atendimento abre com histórico do cliente (se identificado por número) → operador atende → registra disposição → chamada é encerrada e fica associada ao histórico do cliente.
- **Exceção**: cliente não identificado → operador cria/vincula cadastro durante o atendimento. Fila cheia/SLA estourado → chamada é ofertada callback.

### UC-06 Atendimento ativo (discagem)
- **Ator**: Operador/Vendedor.
- **Fluxo**: usuário seleciona contato (manualmente ou via lista de discagem) → sistema origina a chamada (click-to-call) → chamada é conectada → operador registra disposição ao final.
- **Exceção**: número inválido/sem resposta → disposição automática "não atendido", pode gerar tarefa de nova tentativa.

### UC-07 Supervisão em tempo real
- **Ator**: Supervisor.
- **Fluxo**: supervisor visualiza painel com status de todos os operadores e filas em tempo real → identifica operador em dificuldade/fila com SLA em risco → intervém (escuta, sussurro, transferência ou assume o atendimento).
- **Exceção**: operador cai (perde conexão) — sistema marca operador como offline e libera fila.

### UC-08 Atendimento via WhatsApp
- **Ator**: Operador/Vendedor.
- **Fluxo**: mensagem recebida de um contato → sistema cria/atualiza uma Conversa vinculada ao Cliente/Lead (por telefone) → mensagem entra na fila do canal → operador responde pela interface unificada → conversa fica no histórico do cliente.
- **Exceção**: mensagem de número não vinculado a nenhum cadastro → vira lead/atendimento avulso até vinculação manual.

## 3. Administração

### UC-09 Configuração inicial do tenant
- **Ator**: Administrador da empresa.
- **Fluxo**: admin cadastra filiais/equipes → cadastra usuários e papéis → configura filas → configura pipeline(s) → configura canais (telefonia/WhatsApp).

### UC-10 Auditoria
- **Ator**: Admin/Diretor.
- **Fluxo**: usuário consulta trilha de auditoria (quem alterou o quê, quando) filtrando por módulo/usuário/período.

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
