# Visão de Produto

## 1. O que é

Um **CRM + Call Center SaaS** multi-tenant que centraliza o ciclo completo de relacionamento com o cliente — leads, oportunidades, pipeline de vendas, atendimento e comunicação (telefonia, WhatsApp e outros canais) — em uma única plataforma, com experiência **Mobile First** (tablet e celular como uso primário, desktop com excelente suporte).

O produto se dirige a empresas de pequeno e médio porte que hoje operam com ferramentas fragmentadas (planilhas, CRMs genéricos sem telefonia, discadores desacoplados do histórico do cliente) e precisam de uma operação comercial e de atendimento unificada, auditável e escalável.

## 2. Quem usa e quem compra

| | Quem usa o dia a dia | Quem compra / decide |
|---|---|---|
| Perfil | Vendedores, operadores de call center, supervisores, backoffice | Diretores, administradores da empresa (dono da conta/tenant) |
| Motivação | Fechar vendas, atender clientes rápido, cumprir metas e SLA | Visibilidade de indicadores, controle de custo operacional, redução de retrabalho, compliance |

O comprador (admin da empresa/diretor) normalmente não opera o sistema diariamente, mas exige dashboards, relatórios e controle de permissões. O usuário do dia a dia (vendedor/operador) exige velocidade, simplicidade e baixo atrito em telas pequenas.

## 3. Problemas que o produto resolve

- Dados de clientes e histórico de atendimento espalhados entre planilhas, WhatsApp pessoal, e-mail e sistemas de telefonia isolados.
- Falta de visibilidade do gestor sobre o que está acontecendo no pipeline e na operação de atendimento em tempo real.
- Ausência de rastreabilidade: não se sabe quem falou com o cliente, quando, sobre o quê, com qual resultado.
- Distribuição manual e injusta de leads entre vendedores.
- Impossibilidade de medir SLA, produtividade de operador e taxa de conversão de forma confiável.
- Ferramentas que não funcionam bem em celular/tablet, forçando o time de campo e vendas externas a usar desktop.
- Crescimento da operação (mais usuários, mais chamadas, mais mensagens) que quebra ferramentas não pensadas para escalar.

## 4. Dores por papel

- **Gestores/Diretores**: falta de indicadores confiáveis e em tempo real; dificuldade de prever receita; não sabem onde estão os gargalos do funil.
- **Administradores da empresa**: configurar acessos, filas e permissões é complicado ou inexistente nas ferramentas atuais; falta de auditoria.
- **Supervisores de Call Center**: não enxergam status dos operadores em tempo real; não conseguem intervir (escutar, sussurrar, assumir) em atendimentos difíceis; relatórios de produtividade são manuais.
- **Operadores de Call Center**: alternam entre múltiplas ferramentas (discador, CRM, WhatsApp) para atender um único cliente; perdem contexto do histórico.
- **Vendedores/Consultores**: perdem leads por falta de follow-up automatizado; não têm visão clara do próprio pipeline; retrabalho ao registrar a mesma informação em vários lugares.

## 5. Principais casos de uso (visão geral)

- Captar um lead (formulário, importação, integração) e distribuí-lo automaticamente a um vendedor ou fila.
- Qualificar um lead e convertê-lo em oportunidade dentro de um pipeline configurável.
- Realizar atendimento receptivo ou ativo (voz, WhatsApp) com histórico único do cliente disponível na tela.
- Um supervisor acompanhar em tempo real o status de operadores e filas, intervindo quando necessário.
- Um gestor visualizar dashboards de vendas e atendimento por período, equipe e canal.
- Um administrador configurar usuários, papéis, filas e permissões da empresa (tenant) sem depender de suporte técnico.

Fluxos críticos detalhados estão em [use-cases.md](use-cases.md) e [../02-business/workflows.md](../02-business/workflows.md).

## 6. Diferenciais do produto

- **Mobile First de verdade**: não é um CRM desktop "responsivo" — a operação de vendas e atendimento é desenhada primeiro para tablet/celular.
- **CRM e Call Center nativamente integrados**: histórico de chamada, WhatsApp e negociação no mesmo registro de cliente, sem integrações frágeis entre sistemas separados.
- **Multi-canal por abstração**: troca de provedor de telefonia/WhatsApp sem reescrever o produto (ver [../03-architecture/integrations.md](../03-architecture/integrations.md)).
- **Multi-tenant desde o design**, mas sem a complexidade operacional de infraestrutura isolada por cliente antes de ser necessário.
- **Documentação como fonte da verdade**, permitindo evolução consistente por múltiplos times/agentes de IA.

## 7. O que NÃO faz parte do produto inicialmente

- Discador preditivo (Predictive Dialer) com algoritmo de pacing — ver [../02-business/workflows.md](../02-business/workflows.md) seção Call Center.
- Integrações de e-mail marketing/automação de marketing completa (fora de campanhas básicas).
- Módulo de Billing/cobrança de clientes finais do tenant (billing é para cobrar o próprio tenant da plataforma, e mesmo esse é pós-MVP).
- IA como funcionalidade voltada ao usuário final (sugestões, resumo de atendimento, transcrição) — está no roadmap (Fase 10), mas não no MVP. Não confundir com uso de IA para *desenvolver* o software (ver [../../agents/](../../agents/)).
- Aplicativo mobile nativo (iOS/Android via loja) — o caminho inicial é PWA ([ADR-007](../adr/ADR-007.md)); nativo é [D-044](../00-governance/decision-register.md#d-044--aplicativo-mobile-nativo) (`ADIADO`, pós-MVP mediante evidência).
- Multi-idioma além de pt-BR no MVP.

## 8. Visão de crescimento

O sistema deve suportar, sem redesenho de arquitetura, a evolução de uma operação pequena (dezenas de usuários, centenas de leads) para uma operação grande (milhares de usuários, chamadas e mensagens simultâneas). Isso não significa construir para essa escala no dia 1 — significa não tomar decisões no MVP que impeçam essa evolução (ex.: falta de `tenant_id`, ausência de fila assíncrona, acoplamento direto a um único provedor de telefonia). Ver [../03-architecture/scalability.md](../03-architecture/scalability.md).
