# Evidence

Política, não arquivo de dados: a evidência de um MAT vive **dentro** do próprio arquivo
`MAT-XXX-*.md`, na seção "Evidências" — não numa pasta separada. Isso evita indireção (abrir
dois arquivos para entender um resultado) e mantém o resultado, a evidência e o veredito no
mesmo lugar versionado.

Esta pasta existe para os casos em que a evidência **não cabe** inline de forma razoável:

- Screenshot de UI (quando a fase tiver interface — nenhuma tem ainda, ver
  [D-063](../../00-governance/decision-register.md#d-063--fase-2-não-exige-interface-mínima-opção-b)).
- Dump de log longo (mais que ~30 linhas) que perderia legibilidade colado no meio do MAT.
- Gravação de vídeo de um fluxo (raro — só para bugs difíceis de reproduzir em texto).

## Convenção, quando usada

`evidence/<MAT-XXX>/<data>-<descrição-curta>.<ext>` — ex.: `evidence/MAT-001/2026-09-09-cookie-devtools.png`.
O MAT correspondente linka para o arquivo em vez de descrevê-lo só em texto.

## Regra

Evidência proporcional ao risco (ver [manual-acceptance/README.md](../manual-acceptance/README.md) seção "Regra de evidência") — não criar arquivo aqui para todo MAT só por hábito. Um MAT de API sem UI normalmente não precisa de nada nesta pasta: a resposta HTTP inline já é a evidência.
