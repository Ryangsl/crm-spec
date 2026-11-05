# Identidade visual e personalização por tenant

Decisão: [D-086](../00-governance/decision-register.md#d-086--identidade-visual-executive-e-personalização-visual-por-tenant). Arquitetura: [ADR-011](../adr/ADR-011.md). Design system: [design-system.md](../06-frontend/design-system.md).

## 1. Visão do produto

O CRM Universal tem uma **identidade institucional** ("Executive": moderna, profissional e orientada à produtividade) e oferece, como **serviço administrado pela plataforma**, a personalização visual de cada empresa: nome de exibição, cores e tema.

A personalização é **exclusivamente visual**. Todas as empresas usam o mesmo produto, com os mesmos módulos, telas, fluxos, regras de negócio e permissões. Não é customização estrutural, não é uma versão do frontend por cliente e não é white-label: o CRM Universal continua sendo o produto e a marca responsável pela experiência.

## 2. O que todo cliente recebe

Independentemente de personalizar:

- Estrutura de navegação, layout e organização das telas.
- Painel inicial e seus componentes.
- Design system, tipografia institucional (Inter) e ícones.
- Formulários, tabelas, listas, cartões, indicadores e gráficos.
- Janelas de confirmação, avisos e notificações.
- Responsividade (desktop, notebook, tablet e celular).
- Padrões de interação e estados de carregamento, vazio, erro e sucesso.
- Acessibilidade e contraste (WCAG 2.1 AA).
- Identidade institucional do CRM Universal: marca, nome do produto e assinatura "Mais clientes. Mais resultados.".

## 3. O que pode ser personalizado para o cliente

**É um serviço administrado pelo CRM Universal.** O cliente não aplica a mudança: o **Admin da empresa** vê a identidade atual em **Configurações → Identidade Visual** e **solicita** a alteração; a **equipe da plataforma** avalia e aplica. O Diretor só vê. A mudança vale para todos os usuários daquela empresa assim que aplicada, e nenhuma outra empresa é afetada.

| Perfil | Ver identidade e solicitação | Solicitar | Aplicar e restaurar |
|---|---|---|---|
| Plataforma (operador do CRM Universal) | sim | — | sim (`branding:manage`, reservada) |
| Admin da empresa | sim | sim (`branding:request`) | não |
| Diretor | sim (`branding:read`) | não | não |
| Demais perfis | não (a identidade só aparece aplicada) | não | não |

| Item | O que é | Onde aparece | Restrições | Estado |
|---|---|---|---|---|
| Nome de exibição | Nome da empresa na interface | Barra superior e pré-visualização | 2 a 80 caracteres, texto puro. Em branco, usa o nome cadastrado | Implementado |
| Cor primária | Cor de interação | Links, foco, item ativo do menu, destaques e realces | Contraste mínimo de 3:1 com as superfícies. O tom usado em texto é ajustado sozinho para 4,5:1 | Implementado |
| Cor secundária | Cor do texto de apoio | Descrições, rótulos e textos secundários | Contraste mínimo de 4,5:1 com as superfícies | Implementado |
| Botões principais | Fundo do botão principal | Ações principais de todas as telas | O texto do botão é escolhido automaticamente; precisa atingir 4,5:1 | Implementado |
| Barra lateral | Fundo do menu lateral | Menu do desktop e menu "Mais" do celular | O texto do menu é escolhido automaticamente; precisa atingir 4,5:1 | Implementado |
| Fundo | Cor atrás do conteúdo | Todas as telas | O texto precisa atingir 4,5:1 sobre ela | Implementado |
| Superfícies | Cartões, tabelas e campos | Todas as telas | Texto e texto de apoio precisam atingir 4,5:1 | Implementado |
| Texto | Títulos e texto principal | Todas as telas | 4,5:1 com o fundo e com as superfícies | Implementado |
| Tema | Claro ou escuro | Toda a interface | Cada tema tem cores padrão próprias | Implementado |
| Destaques | Tons derivados da cor primária | Fundos de ícones, selos e realces | Derivados automaticamente | Implementado |
| Logotipo | Marca da empresa | Barra superior | Exige envio seguro de arquivos, que não existe. Enquanto isso, a interface usa as iniciais | **Planejado** |
| Favicon | Ícone da aba do navegador | Navegador | Mesma dependência do logotipo | **Planejado** |

Cores entram só no formato `#RRGGBB`. O backend valida tudo e recusa o que deixaria texto ilegível, dizendo o campo e o motivo.

## 4. O que continua sob controle do CRM Universal

Não é personalizável:

- Estrutura da navegação, ordem e presença dos módulos.
- Layouts, estrutura do painel inicial e dos formulários.
- Regras de negócio, permissões e fluxos de trabalho.
- Comportamento de qualquer componente.
- CSS, HTML, JavaScript ou qualquer código enviado pelo cliente.
- Tipografia institucional e ícones.
- Cores de estado (sucesso, alerta, erro) e das séries dos gráficos: fixas e validadas para daltonismo, para que o significado nunca dependa da marca do cliente.
- A marca e o nome do produto CRM Universal, que continuam visíveis (menu, login e título da página).

Funcionalidades habilitadas por plano continuam sob o sistema de planos ([D-085](../00-governance/decision-register.md#d-085--trial-comercial-modalidade-de-avaliação-por-empresa)). **A identidade visual não depende de plano**: o Trial personaliza como qualquer plano. Uma eventual diferenciação comercial por plano exigiria decisão explícita de produto.

Durante a avaliação expirada (modo de consulta), a identidade continua aplicada, mas não pode ser alterada.

## 5. Evoluções possíveis (não implementadas)

Logotipo e favicon (dependem de armazenamento seguro de arquivos), fontes alternativas, layouts especiais, domínio personalizado, white-label, personalização de e-mails e modelos próprios de comunicação. Nenhuma está disponível hoje.

## 6. Contrato

| Rota | Permissão | Efeito |
|---|---|---|
| `GET /v1/branding` | qualquer usuário do tenant | Identidade em uso (a interface precisa dela para se desenhar) |
| `PUT /v1/branding` | `branding:manage` (plataforma) | Aplica nome, tema e cores e atende a solicitação, com auditoria (`branding.updated`) |
| `DELETE /v1/branding` | `branding:manage` (plataforma) | Restaura o padrão, com auditoria (`branding.reset`) |
| `GET /v1/branding/request` | `branding:read` | Solicitação pendente |
| `POST /v1/branding/request` | `branding:request` (Admin) | Solicita alteração, com auditoria (`branding.change_requested`) |
| `DELETE /v1/branding/request` | `branding:manage` (plataforma) | Encerra sem aplicar (`branding.request_dismissed`) |

Operação: [runbook-branding.md](../08-devops/runbook-branding.md).

Detalhes em [openapi.yaml](../05-api/openapi.yaml). `logo_url` e `favicon_url` já estão no contrato e chegam sempre nulos.
