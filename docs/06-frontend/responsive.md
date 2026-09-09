# Responsividade

## 1. Breakpoints de referência

| Nome | Largura | Dispositivo típico | Prioridade |
|---|---|---|---|
| `xs` | ≥360px | Celular pequeno | **Baseline obrigatório** |
| `sm` | ≥640px | Celular grande | Obrigatório |
| `md` | ≥768px | Tablet retrato | **Alvo prioritário do produto** |
| `lg` | ≥1024px | Tablet paisagem / notebook pequeno | Obrigatório |
| `xl` | ≥1280px | Desktop | Obrigatório, sem otimização excessiva além do necessário |

O produto é desenhado **de `xs` para cima**: toda tela é primeiro viável em 360px de largura (RNF-12) e depois ganha camadas de layout para telas maiores — nunca o caminho inverso de "adaptar o desktop para caber no celular".

## 2. Prioridade tablet

Tablets são o dispositivo de maior uso esperado para vendedores em campo e supervisores em movimento. Isso implica:
- Layouts em `md`/`lg` aproveitam a largura extra para mostrar mais contexto simultâneo (ex.: lista + detalhe lado a lado), em vez de apenas aumentar fontes/espaçamento.
- Kanban de pipeline é plenamente utilizável (múltiplas colunas visíveis) a partir de `md`.

## 3. Padrões por tipo de tela

- **Listagens**: lista/cards empilhados em `xs`/`sm`; tabela ou lista+detalhe lado a lado a partir de `md`/`lg`.
- **Formulários**: campo único por linha em `xs`; múltiplas colunas a partir de `md` quando o formulário for longo (ex.: cadastro de cliente).
- **Navegação**: bottom navigation até `md`; sidebar a partir de `lg` (ver [design-system.md](design-system.md) seção 4). O critério de transição é **apenas largura de viewport** ([D-042](../00-governance/decision-register.md#d-042--breakpoint-de-transição-da-navegação), `PROPOSTO`); considerar orientação apenas se o teste em tablet real, na Fase 3, mostrar problema.
- **Tela de atendimento (call center)**: em `xs`/`sm`, histórico e ações de disposição em abas; a partir de `md`, histórico e ações lado a lado sem necessidade de troca de aba.

## 4. Área de toque e ergonomia

- Alvo mínimo de toque: 44x44px (Apple HIG / WCAG) em qualquer botão, ícone acionável ou item de lista clicável.
- Ações destrutivas ou irreversíveis (excluir, perder oportunidade) exigem confirmação explícita, nunca um único toque acidental.
- Áreas de ação primária (ex.: "Registrar disposição") ficam na região inferior da tela em mobile, mais acessível ao polegar.

## 5. Performance percebida em mobile

- Skeletons em vez de spinners genéricos para listas (dá sensação de carregamento mais rápido).
- Paginação por cursor com carregamento incremental ("carregar mais"/scroll infinito) em listas mobile, evitando paginação numérica pouco ergonômica em tela pequena.
- Imagens/anexos carregados sob demanda (lazy), nunca pré-carregados em lote em conexões móveis.

## 6. PWA e uso offline parcial

- Instalável (manifest + service worker), com ícone e splash screen.
- Escopo offline ([D-041](../00-governance/decision-register.md#d-041--escopo-de-funcionamento-offline-do-pwa), `DECIDIDO`): apenas cache de assets estáticos e leitura dos últimos dados carregados. **Sem** fila de escrita offline com sincronização — o risco de conflito de dados em operação de atendimento não se justifica no MVP. Escrita offline fica para fase futura, se houver demanda real.
