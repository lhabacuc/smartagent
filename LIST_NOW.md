# LIST NOW - Hoje

## Objetivo do dia
- Avançar o SmartAgent com entregas pequenas, testadas e commitadas localmente.
- Bater meta mínima de 10 commits no dia (sem push).

## Tarefas prioritárias

1. Validar CLI oficial empacotada
- Testar `smartagent --help`
- Testar `smartagent env-check`
- Testar `smartagent doctor --provider groq`
- Testar `smartagent run-example --list`

2. Melhorar comando `chat` para uso real
- Adicionar opção para carregar tools de um módulo externo (ex: `--tools-file`)
- Garantir mensagens de erro claras quando faltar tool/module
- Cobrir com testes unitários

3. Endurecer `doctor`
- Validar provider inválido com saída amigável
- Mostrar resolução efetiva de model/env
- Adicionar testes para aliases (`xai`, `google-gemini`)

4. Documentação da CLI
- Atualizar `README.md` com exemplos completos de cada subcomando
- Atualizar `INSTALL.md` com fluxo rápido de diagnóstico

5. Qualidade
- Rodar `make test`
- Corrigir qualquer regressão

## Meta de commits (micro-commits)
- 1 commit: planejamento do dia
- 6 commits: implementação (feat/fix/refactor)
- 2 commits: testes/docs
- 1 commit: fechamento/cleanup

## Critério de pronto
- Testes passando
- CLI funcional para fluxo básico
- Documentação atualizada
- Commits locais feitos (sem push)
