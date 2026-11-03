# MAT-014 — Restrição por horário: interface (toggle, banner, `403` e tela de liberações)

## 1. Identificação

| Campo | Valor |
|---|---|
| ID | MAT-014 |
| Fase / incremento | 4 / F4.7 |
| Prioridade | ALTA |
| Tipo | Funcional (interface) + Segurança (visibilidade por permissão) |
| Requisitos relacionados | BR-27, UC-15 |
| Decisions relacionadas | [D-082](../../00-governance/decision-register.md#d-082--restrição-por-horário-comercial-e-liberação-excepcional-vn-07-vn-08), [D-083](../../00-governance/decision-register.md#d-083--exceções-de-acesso-modelo-técnico-e-critério-de-identificação-td-05-td-14) |
| Ambiente | **Ambiente integrado**: backend + frontend + navegador. Exige screenshot |

## 2. Objetivo

Validar, na interface real, que: o toggle global só aparece para o Admin; o banner "Fora do horário" aparece para o usuário sujeito à restrição quando algum recurso está bloqueado; o `403 OUTSIDE_BUSINESS_HOURS` é mostrado como aviso claro (não como erro genérico); a tela de liberações lista, concede e revoga; e o menu respeita a permissão.

## 3. Escopo

**Cobre**: `/settings/business-hours` (toggle), banner no `AppShell`, telas `/leads`, `/leads/:id`, `/conversations`, `/conversations/:id` e a seção "Conversas" nos detalhes de Cliente e Oportunidade, `/settings/access-exceptions`, item de menu "Liberacoes".

**Não cobre**: a regra de acesso em si ([MAT-010](MAT-010-restricao-acesso-dentro-fora-horario.md) a [MAT-012](MAT-012-restricao-liberacao-excepcional.md)). Lacunas conhecidas: `LeadEditPage` e `LeadNewPage` **não** têm tratamento específico do `403` (mostram o erro genérico) — registradas, não bloqueantes.

## 4. Pré-requisitos

[F4-7-preparacao-do-ambiente.md](F4-7-preparacao-do-ambiente.md), com o **frontend no ar** (`VITE_API_URL=http://localhost:3101 npm run dev`). **Estado inicial** (via API, como Admin): horário `$HORARIO_FORA`, restrição **ligada**, nenhuma liberação vigente, `LEAD_ID` e `CONV_ID` criados. O banner reconsulta o status a cada ~1 minuto; ao mudar o estado pela API, aguarde até 1 minuto ou recarregue a página.

## 5. Dados de teste

Quatro sessões (use janelas anônimas diferentes): Admin, Gerente, Vendedor (`vendedor@a.mat.test`), Supervisor. Senha dos usuários de teste: `Mat12345!`.

## 6. Tutorial de execução manual

> Para cada passo, capture **screenshot** da tela indicada e registre a URL.

### Passo 1 — Toggle visível só para o Admin
**Perfil**: Admin, depois Gerente. Abra `/settings/business-hours`.
**Esperado**: o Admin vê "Restricao por horario: ligada/desligada" e o botão **"Desligar restricao"** (ou "Ligar restricao"). O Gerente (que não tem `tenant_settings:read`) vê a página inteira como **"Acesso restrito"**, sem o toggle. Um perfil personalizado com `tenant_settings:read` mas sem `tenant_settings:update` veria o estado e o texto "Somente o Admin pode ligar ou desligar a restricao.", sem o botão. **Evidência**: screenshot de cada perfil.

### Passo 2 — Ligar/desligar pela interface e recusa sem horário
**Perfil**: Admin. Com a restrição ligada, clique em "Desligar restricao" → a tela passa a "Ligar restricao". Para o caso sem horário válido, use um tenant sem horário configurado (ou apague o horário pela API de teste) e tente ligar: o botão fica indisponível com o texto "Salve um horario de funcionamento valido acima para poder ligar a restricao." **Evidência**: screenshots dos três estados.

### Passo 3 — Banner "Fora do horário" para o Vendedor
**Perfil**: Vendedor, com a restrição ligada e fora do horário. Navegue por qualquer tela do sistema.
**Esperado**: banner de aviso **"Fora do horario de funcionamento"** com o texto "O acesso a Leads e Conversas esta indisponivel neste horario. Se precisar acessar agora, peca uma liberacao excepcional a um Admin ou Gerente." **Evidência**: screenshot com o banner.
**Contra-prova**: Gerente, Supervisor e Operador **não** veem o banner; o Vendedor também não o vê com a restrição desligada ou dentro do horário.

### Passo 4 — Banner parcial com liberação de um escopo
**Perfil**: Gerente concede ao Vendedor (pela tela do Passo 7 ou pela API) a liberação `leads`. Após ≤ 1 min / recarregar, o Vendedor vê o banner mencionando **apenas "Conversas"**. Com a liberação `all`, o banner desaparece. **Evidência**: screenshots.

### Passo 5 — `403 OUTSIDE_BUSINESS_HOURS` tratado nas telas
**Perfil**: Vendedor (sem liberação, fora do horário). Abra `/leads`, `/leads/<LEAD_ID>`, `/conversations`, `/conversations/<CONV_ID>` e a seção "Conversas" no detalhe de um Cliente/Oportunidade (se houver).
**Esperado**: em cada uma, o aviso **"Fora do horario de funcionamento"** (texto "O acesso a Leads e Conversas esta indisponivel neste horario. Tente novamente dentro do horario de funcionamento ou peca uma liberacao excepcional a um Admin ou Gerente."), **sem** mensagem de erro genérica ("Erro ao carregar") e sem tela quebrada. **Evidência**: screenshot de cada tela.
**Lacuna conhecida (observar, não reprovar)**: em `/leads/new` e na edição de Lead o erro aparece de forma genérica.

### Passo 6 — O fluxo volta ao normal com a liberação
**Perfil**: Gerente concede `all` ao Vendedor. O Vendedor recarrega `/leads` e `/conversations`: as listas carregam e o banner some. Revogada a liberação, volta o aviso. **Evidência**: screenshots.

### Passo 7 — Tela de liberações (Admin e Gerente)
**Perfil**: Gerente (e depois Admin). Abra `/settings/access-exceptions` (item de menu **"Liberacoes"**).
1. Em "Conceder liberacao": escolha o Vendedor, o escopo, informe o **motivo** e a **expiração futura** → "Conceder liberacao". **Esperado**: mensagem de sucesso e a liberação na lista, "Vigente".
2. Tente conceder sem motivo, sem "Vale até", com motivo só de espaços e com expiração no passado. **Esperado**: motivo vazio e "Vale até" vazio são campos obrigatórios e o **navegador bloqueia o envio** (validação nativa; nada é criado); motivo só de espaços → "Informe o motivo da liberacao."; expiração no passado → "A expiracao deve estar no futuro.". *(Texto corrigido em 2026-10-19: a versão anterior previa as mensagens da tela também para os campos vazios; ver o [relatório](../execucao-assistida-f4-7.md).)*
3. Filtro "Todas / Vigentes / Revogadas ou expiradas": confira cada visão.
4. Clique em **"Revogar"** numa liberação: ela passa para revogada e as demais continuam vigentes.
**Evidência**: screenshots da lista antes/depois e das mensagens de recusa.

### Passo 8 — Visibilidade do menu e da tela por permissão
**Perfil**: Supervisor e Vendedor: o item **"Liberacoes"** **não** aparece no menu; abrir `/settings/access-exceptions` diretamente mostra "Acesso restrito" (sem a lista). Admin e Gerente veem o item. **Evidência**: screenshots.

## 7. Resultado que NÃO deve acontecer

- ✗ O Gerente (ou outro perfil sem `tenant_settings:update`) conseguir ligar/desligar a restrição pela interface.
- ✗ Banner exibido a quem não é sujeito, com a restrição desligada, dentro do horário, ou quando nada está bloqueado.
- ✗ `403 OUTSIDE_BUSINESS_HOURS` aparecer como erro genérico ou tela em branco nas telas listadas no Passo 5.
- ✗ Item "Liberacoes" ou a lista de liberações visível para Supervisor/Vendedor/Operador.
- ✗ A tela conceder liberação sem motivo ou com expiração no passado.
- ✗ Dados de outro tenant na lista de liberações.

---

## 8. Resultado da IA — Execução anterior

> **NÃO EXECUTADO pela IA.** Este MAT exige navegador, frontend em execução e screenshots, e a IA não dispôs de navegador nesta sessão. **Nenhum resultado de interface está registrado aqui.**

| Campo | Valor |
|---|---|
| Executor | — |
| Data | — |
| Resultado | **NÃO EXECUTADO** |

**O que existe como evidência indireta (não substitui este MAT)**: testes automatizados de componente do frontend (Vitest/Testing Library), 275/275 passando em 2026-10-19 no `main` pós-merge (`289373e`), incluindo `AccessStatusBanner.test.tsx`, `BusinessHoursRestrictionToggle.test.tsx`, `OutsideBusinessHours.test.tsx`, `AccessExceptionsPage.test.tsx` e `AppShell.access-control.test.tsx`. Eles provam o comportamento dos componentes com a API simulada, não a interface real integrada ao backend.

> **Atualização (2026-10-19, rodada posterior)**: este MAT passou a ser executado com navegador real; ver o Histórico e o relatório consolidado. O texto acima é o registro da época e não foi alterado. Os achados dessa execução (defeito D1 e a correção do passo 7.2 do roteiro) estão no [relatório consolidado](../execucao-assistida-f4-7.md).

## 9. Validação Manual do Responsável

> **Não preencher automaticamente.** Responsabilidade do responsável pelo projeto, após executar de verdade os passos da seção 6. A execução técnica assistida por IA (2026-10-19) está registrada no [relatório consolidado](../execucao-assistida-f4-7.md), na seção 8 e no Histórico, e **não substitui** esta validação.

- **Executor**: _______________________________
- **Data**: _______________________________
- **Ambiente**: _______________________________
- **Resultado**: [ ] PASSOU  [ ] FALHOU  [ ] BLOQUEADO

**Passos executados:**
- [ ] 1 Toggle só Admin · [ ] 2 Ligar/desligar e recusa · [ ] 3 Banner do Vendedor · [ ] 4 Banner parcial · [ ] 5 `403` nas telas · [ ] 6 Volta ao normal com liberação · [ ] 7 Tela de liberações · [ ] 8 Visibilidade por permissão

**Observações:**

_______________________________

**Evidências** (log / saída dos comandos / screenshots):

_______________________________

## 10. Critério de Aceite

- 🟢 **PASSOU** — comportamento observado na interface igual ao esperado em cada passo, com screenshots, sem nenhuma ocorrência da seção 7.
- 🔴 **FALHOU** — qualquer resultado da seção 7 ocorreu.
- 🟡 **BLOQUEADO** — não foi possível executar por ambiente, dependência ou fixture.

> **Importante**: executado em 2026-10-19 em execução técnica assistida pela IA (ver o [relatório](../execucao-assistida-f4-7.md) e o Histórico); o aceite humano formal continua pendente.

## 11. Histórico

| Data | Executor | Tipo | Resultado |
|---|---|---|---|
| _(a preencher)_ | _(IA ou responsável)_ | IA | NÃO EXECUTADO |
| 2026-10-19 | Claude (Sonnet 5.5) | IA (interface, Chrome real, rodada posterior à seção 8; ver [relatório](../execucao-assistida-f4-7.md)) | PASSOU (39/39; defeito menor D1 registrado) |
| _(a preencher)_ | _(responsável pelo projeto)_ | Manual | PENDENTE |
