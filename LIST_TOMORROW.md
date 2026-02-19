# LIST TOMORROW - Amanhã

## Prioridades sugeridas

1. Carregamento de tools externas no CLI
- Implementar `smartagent chat --tools-file tools.py`
- Permitir usar funções reais do projeto sem editar a lib

2. Segurança no `/exec`
- Bloquear comandos perigosos por padrão
- Adicionar opção `--unsafe` para liberar explicitamente

3. Comando `/status`
- Exibir provider, modelo, tools ativas/desativas, histórico on/off

4. Melhorar `/tools`
- Mostrar docstring e parâmetros de cada tool, não só nome

5. Logging opcional no CLI
- Adicionar `--debug` para exibir análise, `tool_calls` e erros de execução

6. `smartagent doctor --fix-hints`
- Diagnóstico com sugestões práticas de correção do ambiente

7. Hardening do analyzer
- Retry quando vier saída não-JSON
- Pedir reformatação JSON antes de fallback

8. Documentação de comandos interativos
- Atualizar `README.md` com `/clear`, `/cl`, `/exec`, `/enable`, `/disable`, `/tools`

## Ordem recomendada
- `2 -> 1 -> 3 -> 8`
