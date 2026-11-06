# Reativação de usuário

**Situação (06/11/2026):** decidida na [D-093](../00-governance/decision-register.md#d-093--reativação-de-usuário-e-troca-de-e-mail) e implementada na branch `feat/hardening-security-consistency` (sem commit). Resumo do que vale:

- `POST /v1/users/{id}/reactivate`, com `users:delete` (quem desativa reativa; hoje só o Admin), sob as regras da D-087 e o limite de usuários do plano.
- Os papéis anteriores voltam. A senha anterior deixa de valer; a resposta traz um link de redefinição de uso único (24 h, [D-064](../00-governance/decision-register.md#d-064--rf-03-redefinição-de-senha-fase-e-fluxo-indefinidos)) para o Admin entregar à pessoa. Sessões antigas continuam revogadas. Auditoria `user.reactivated`.
- Tela de Usuários: ação "Reativar" nos inativos, com o link mostrado uma vez.
- Continua aberta só a limitação da D-084 (access token anterior à desativação volta a valer se a reativação ocorrer em até 15 min).

A análise original (05/11/2026) fica abaixo como registro; as escolhas marcadas **[Decisão]** foram resolvidas pela D-093.

## 1. Como é hoje

- "Excluir" usuário é **desativação lógica** (`status = inactive`, [personas.md](personas.md) §2.2), por `DELETE /v1/users/{id}`, com `users:delete`.
- Desativar revoga todas as sessões na mesma transação ([D-084](../00-governance/decision-register.md#d-084--ciclo-de-vida-da-sessão-usuário-e-tenant-ativos-a-cada-requisição-revogação-na-desativação-e-redação-de-cookies-nos-logs)). Os papéis (`user_roles`) **não** são apagados.
- **Não existe** endpoint nem tela de reativação. Os testes reativam direto no banco.
- Limitação aceita da D-084: um access token emitido antes da desativação volta a valer se o usuário for reativado em até 15 minutos.
- Usuário inativo não conta no limite de usuários do plano ([D-085](../00-governance/decision-register.md#d-085--trial-comercial-modalidade-de-avaliação-por-empresa)).

## 2. O que seria preciso

| Item | Necessidade | Observação |
|---|---|---|
| Rota | `POST /v1/users/{id}/reactivate` (ou equivalente) | Idempotente; usuário de outro tenant = 404 |
| Permissão | **[Decisão]** reutilizar `users:delete` (quem desativa reativa), `users:update` ou criar `users:reactivate` | Nova chave exige seed e passo de dados nos tenants existentes |
| Regras de concessão | Mesmas da [D-087](../00-governance/decision-register.md#d-087--concessão-de-papéis-privilegiados-e-proteção-do-último-admin): quem reativa precisa cobrir as permissões do usuário; reativar um Admin exige ser Admin | Sob o mesmo lock de administração de acesso |
| Papéis ao reativar | **[Decisão]** manter os papéis anteriores ou voltar sem papel e exigir nova atribuição | Manter é o comportamento natural hoje (os vínculos existem) |
| Limite do plano | Reativar ocupa uma vaga: verificar o limite de usuários sob o lock do plano, como na criação | No Trial expirado, é escrita e fica bloqueada |
| Sessões antigas | Os refresh tokens revogados continuam revogados (já é assim) | Fechar a janela de 15 min exige marcador por usuário (`sessions_invalid_before`), com migration, já previsto como melhoria na D-084 |
| Senha | **[Decisão]** reativar com a senha anterior ou exigir troca | Não existe fluxo de redefinição de senha (RF-03); sem ele, exigir troca não é possível |
| Auditoria | `user.reactivated`, na mesma transação | Como as demais ações de usuário |
| Frontend | Ação "Reativar" na tela de Usuários, só para inativos | Hoje a tela informa que a reativação não está disponível |

## 3. Riscos

- Reativar sem fechar a janela de 15 minutos revalida um access token antigo (limitação já aceita na D-084).
- Reativar com a senha anterior devolve o acesso a quem a conhecia; sem RF-03, a única alternativa seria o Admin definir uma senha nova, o que hoje a API também não permite (o PATCH não aceita senha).
