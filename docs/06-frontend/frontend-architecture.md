# Arquitetura de Frontend

Repositório: `crm-frontend`. Consome exclusivamente os contratos definidos em [../05-api/](../05-api/). Nunca acessa banco de dados nem implementa regra de negócio crítica (ver [../05-api/api-guidelines.md](../05-api/api-guidelines.md) seção 10).

## 1. Stack

| Camada | Tecnologia | Avaliação |
|---|---|---|
| Build | Vite | Necessário — dev server rápido, essencial para produtividade Mobile First (HMR) |
| UI | React + TypeScript | Necessário — ecossistema maduro, tipagem compartilhável com contratos gerados do OpenAPI |
| Estilo | Tailwind CSS | Necessário para consistência de design system utilitário e velocidade em telas mobile |
| Estado de servidor | TanStack Query | Necessário — cache, revalidação e paginação por cursor exigidas pela API tornam isso não-trivial sem uma lib dedicada |
| Formulários | React Hook Form + Zod | Necessário — formulários são o núcleo da UI (cadastro de lead, cliente, disposição de chamada); Zod compartilha validação com os DTOs do contrato |
| Estado global de UI | Context API / store leve (`[DECISÃO PENDENTE]`: Zustand vs. Context puro) | Necessário apenas para estado de UI cross-cutting (sessão, tema, status de conexão realtime) — não para estado de servidor, que é do TanStack Query |
| PWA | Plugin PWA do Vite (service worker, manifest) | Necessário — requisito explícito de Mobile First/instalável |

## 2. Estrutura de pastas (conceitual)

```
src/
  app/                # bootstrap, rotas, providers globais
  features/           # um diretório por módulo de negócio (leads, opportunities, calls, ...)
    <feature>/
      components/
      hooks/
      api/            # chamadas TanStack Query específicas da feature
      types/
  shared/
    components/       # design system (ver design-system.md)
    hooks/
    lib/              # cliente HTTP, formatação, utils
  realtime/           # cliente WebSocket + fallback polling (ver architecture.md seção 5)
```

Cada `feature` corresponde, em geral, a um módulo do backend (ver [../03-architecture/architecture.md](../03-architecture/architecture.md) seção 2), mantendo o vocabulário consistente entre os dois repositórios.

## 3. Estado

- **Estado de servidor** (dados vindos da API): sempre via TanStack Query — cache, invalidação por mutação, paginação por cursor nativa.
- **Estado de UI local**: `useState`/`useReducer` dentro do componente/feature.
- **Estado global de UI** (sessão do usuário, tema, conectividade realtime): store leve compartilhado, nunca duplica dado de servidor.
- Regra geral: **nunca guardar em estado global algo que a API já expõe** — refetch/cache do TanStack Query é a fonte de verdade, evitando dessincronia.

## 4. Formulários e validação

- Todo formulário usa React Hook Form + schema Zod.
- Validação client-side é UX (feedback imediato), nunca a autoridade — o backend sempre revalida (ver [../05-api/api-guidelines.md](../05-api/api-guidelines.md)).
- Schemas Zod devem espelhar os DTOs do [openapi.yaml](../05-api/openapi.yaml); `[DECISÃO PENDENTE]`: geração automática de tipos/schemas a partir do OpenAPI vs. manutenção manual — geração automática é a direção recomendada assim que o contrato estabilizar.

## 5. Tratamento de loading, empty e error states

Todo componente que consome dado assíncrono trata explicitamente três estados, sem exceção:
1. **Loading** — skeleton ou spinner consistente com o design system.
2. **Empty** — estado vazio com mensagem orientativa (nunca uma tela em branco sem explicação).
3. **Error** — mensagem de erro amigável, usando `code`/`message` do contrato de erro padronizado, com ação de retry quando aplicável.

## 6. Notificações e feedback

- Toasts para feedback de ações pontuais (sucesso/erro de uma mutação).
- Modais para confirmações e formulários curtos; nunca navegação principal dentro de modal.
- Notificações em tempo real (novo lead atribuído, mensagem recebida) chegam via `realtime/` e populam tanto um centro de notificações quanto invalidam queries relevantes do TanStack Query.

## 7. Tempo real no frontend

- Um único cliente WebSocket por sessão, com reconexão automática.
- Ao desconectar, o app degrada para polling nos recursos que dependem de tempo real (status de fila/operador, conversa ativa) — nunca trava a tela nem exige reload manual (RNF-04).
- Eventos recebidos via WebSocket, em geral, apenas invalidam a query correspondente no TanStack Query (fonte única de verdade continua sendo a API/refetch), evitando dois caminhos divergentes de estado.

## 8. Acessibilidade

- Componentes de design system seguem práticas WAI-ARIA básicas (foco visível, labels associados, contraste mínimo AA).
- Alvo de toque mínimo de 44x44px em qualquer ação em telas mobile (ver [responsive.md](responsive.md)).
