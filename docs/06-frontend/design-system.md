# Design System

## 1. Princípios

- **Mobile First**: todo componente é desenhado para tela pequena primeiro, depois adaptado para telas maiores — nunca o inverso.
- **Consistência sobre customização**: componentes do design system são reutilizados por toda a aplicação; exceções pontuais de estilo indicam que falta um componente, não que se deve estilizar ad-hoc.
- **Baixo atrito operacional**: operadores de call center e vendedores usam o sistema sob pressão de tempo — densidade de informação e número de cliques importam mais do que estética elaborada.

## 2. Fundamentos (tokens)

- Cores, espaçamento, tipografia e raio de borda definidos como tokens Tailwind (`tailwind.config`), nunca valores mágicos no componente.
- Paleta de marca definitiva: `[VALIDAÇÃO DE NEGÓCIO NECESSÁRIA]` ([D-043](../00-governance/decision-register.md#d-043--paleta-de-marca), antes do primeiro cliente/piloto). **Não bloqueia a Fase 1**: o design system usa uma paleta neutra de placeholder e todas as cores são tokens — trocar a paleta depois é alterar tokens, não componentes.
- Escala de espaçamento e tipografia segue a escala padrão do Tailwind, evitando valores arbitrários fora da escala.

## 3. Componentes base

| Componente | Uso principal |
|---|---|
| Botão (primário/secundário/destrutivo/ghost) | Ações em toda a aplicação |
| Campo de formulário (input, select, textarea, date/time picker) | Formulários (integrado a React Hook Form) |
| Tabela | Listagens administrativas (usuários, clientes) — com paginação por cursor |
| Kanban | Pipeline de oportunidades — arrastar/mover etapa (com alternativa por menu em touch, ver seção 5) |
| Card | Listagens em grade mobile (lead, cliente, tarefa) |
| Modal / Bottom Sheet | Confirmações e formulários curtos — bottom sheet em mobile, modal centralizado em desktop |
| Toast | Feedback de ação |
| Badge de status | Status de lead/oportunidade/chamada/operador |
| Avatar | Usuário/operador |
| Skeleton | Estado de loading |
| Empty state | Ausência de dados |
| Painel de status em tempo real | Operadores/filas (supervisão) |

## 4. Layout e navegação

- **Mobile/tablet**: navegação inferior (*bottom navigation*) com os módulos de maior uso (Início/Dashboard, Leads/Pipeline, Atendimento, Agenda, Mais); ações secundárias em menu "Mais".
- **Desktop**: sidebar lateral persistente com todos os módulos, mesma hierarquia de informação da bottom navigation, apenas expandida.
- Cabeçalho contextual (breadcrumb simplificado) para orientar o usuário em fluxos profundos (ex.: Cliente → Oportunidade → Etapa).

## 5. Padrões específicos de Call Center/CRM

- **Kanban de pipeline em touch**: arrastar-e-soltar tem alternativa explícita via ação de menu ("Mover para etapa..."), pois drag-and-drop é pouco confiável em telas pequenas.
- **Tela de atendimento**: layout fixo com histórico do cliente sempre visível (não escondido atrás de aba), ações de disposição sempre acessíveis sem rolagem em telas de até 6.5".
- **Status de operador**: sempre visível no cabeçalho quando o usuário está logado em uma fila, com troca de status em um toque.

## 6. Estados visuais obrigatórios

Todo componente de listagem/detalhe do design system fornece variantes de loading, empty e error prontas para uso (ver [frontend-architecture.md](frontend-architecture.md) seção 5) — não é responsabilidade de cada feature reinventar esses estados.

## 7. Acessibilidade

- Contraste mínimo AA (WCAG 2.1) em todos os tokens de cor de texto/fundo.
- Todo ícone usado como ação isolada tem rótulo acessível (`aria-label`).
- Navegação por teclado suportada em toda a superfície desktop.
