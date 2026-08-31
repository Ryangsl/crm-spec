# Fluxos de Trabalho (Workflows)

## 1. Fluxo comercial ponta a ponta

```
Lead recebido
  → distribuição (round-robin / fila / manual)
  → contato (ligação, WhatsApp, e-mail)
  → qualificação (critérios do tenant)
       ├─ desqualificado → motivo → encerrado
       └─ qualificado → conversão em Oportunidade
  → oportunidade entra no Pipeline (1ª etapa)
  → negociação (movimentação entre etapas, tarefas, follow-ups)
  → resultado
       ├─ Ganha → cliente ativo, aciona pós-venda/backoffice
       └─ Perdida → motivo obrigatório → encerrado (estado terminal)
```

Regras associadas: [../02-business/business-rules.md](../02-business/business-rules.md) BR-03 a BR-13.

## 2. Fluxo de atendimento receptivo (Call Center)

```
Chamada/mensagem chega ao canal
  → identifica cliente pelo identificador do canal (telefone)
       ├─ encontrado → carrega histórico
       └─ não encontrado → atendimento "avulso", vínculo/cadastro durante o atendimento
  → entra na fila configurada (roteamento por skill/horário)
  → distribuída ao primeiro operador Disponível na fila
       └─ nenhum operador disponível → aguarda (SLA contando) → pode ofertar callback
  → operador atende (tela unificada: histórico + canal ativo)
  → operador registra disposição
  → atendimento encerrado, associado ao histórico do cliente
```

## 3. Fluxo de atendimento ativo (discagem)

```
Operador/vendedor seleciona contato (manual ou lista de discagem)
  → sistema origina chamada (click-to-call) via provedor de telefonia configurado
  → chamada conectada (ou falha: ocupado/sem resposta/inválido)
  → operador conduz o atendimento
  → registra disposição
       └─ disposição "retornar depois" pode gerar tarefa de nova tentativa automaticamente
```

MVP de telefonia = discagem manual/click-to-call (ver [../03-architecture/architecture.md](../03-architecture/architecture.md) seção Call Center e [ADR pendente sobre discador]).

## 4. Fluxo de supervisão em tempo real

```
Supervisor abre painel de monitoramento
  → recebe atualizações em tempo real (WebSocket) de:
       status de operadores, tamanho de filas, SLA em risco
  → pode intervir:
       - escutar chamada (silent monitoring)
       - sussurrar (whisper) ao operador
       - assumir/transferir o atendimento
  → falha de WebSocket → painel cai para polling periódico (fallback)
```

## 5. Fluxo de mensageria (WhatsApp/omnichannel)

```
Provedor de canal envia webhook de mensagem recebida
  → adaptador do canal normaliza payload para o formato interno (Message)
  → verifica idempotência por external_message_id
       └─ já processada → descarta (ack sem reprocessar)
  → resolve/atualiza Conversa vinculada ao Cliente/Lead
  → mensagem entra na fila do canal (se não houver atendimento ativo) ou
    é anexada à conversa em atendimento
  → operador responde pela interface unificada
  → envio é assíncrono (job) com retry/backoff; status de entrega
    é atualizado via webhook de status do provedor
```

Idempotência e reprocessamento: [../02-business/business-rules.md](../02-business/business-rules.md) BR-20/BR-21 e [../03-architecture/architecture.md](../03-architecture/architecture.md).

## 6. Fluxo de configuração inicial de um tenant

```
Tenant provisionado (Super Admin / self-service - [DECISÃO PENDENTE] sobre self-service no MVP)
  → admin da empresa faz primeiro login
  → cadastra filiais e equipes
  → cadastra usuários e atribui papéis
  → configura pipeline(s) e etapas
  → configura filas de atendimento
  → configura canais (telefonia/WhatsApp) — credenciais do provedor
  → operação pronta para uso
```

## 7. Fluxo de auditoria

```
Qualquer ação de escrita relevante (create/update/delete, login, mudança de permissão)
  → gera evento de auditoria (usuário, tenant, entidade, ação, timestamp, payload relevante)
  → persistido de forma imutável, indexado por tenant/usuário/entidade/período
  → consultável por Admin/Diretor via tela de auditoria
```
