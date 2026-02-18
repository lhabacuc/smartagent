# Changelog

## 0.2.0 - 2026-02-18

### Added
- `AgentConfig` para centralizar configuracao do agente.
- Suporte a `SMARTAGENT_PROVIDER`, `SMARTAGENT_MODEL`, `SMARTAGENT_TIMEOUT`, `SMARTAGENT_RETRIES`.
- Suporte a `SMARTAGENT_API_KEY` e `SMARTAGENT_<PROVIDER>_API_KEY`.
- Registry de providers em `agent.integrations` com aliases (`google-gemini`, `xai`).
- Timeout e retry HTTP padronizados em todas as integracoes.
- Utilitarios de CLI extraidos para `agent/cli.py`.

### Changed
- API publica agora separa semanticamente `provider` de `model`.
- `get_llm_client` agora aceita `provider`, `api_key`, `model`, `timeout`, `retries`.

### Deprecated
- Usar `model` como provider (ex.: `Agent(model="groq")`).
- Metodos de utilitario no `Agent`: `help`, `help_var`, `pociveis_erros`, `run`.

### Migration Guide
1. Trocar inicializacao antiga:
   - antes: `Agent(model="groq")`
   - agora: `Agent(provider="groq", model="qwen/qwen3-32b")`
2. Migrar variaveis de ambiente:
   - preferir `SMARTAGENT_*`
   - `LLM` e `*_API_KEY` legadas continuam suportadas por compatibilidade.
3. Ajustar scripts interativos:
   - preferir funcoes em `agent.cli` para ajuda e modo interativo.

### Compatibility Window
- `0.2.x`: manter comportamento legado com `DeprecationWarning`.
- `0.3.0` (planejado): remover `model` como provider e wrappers legados de CLI no `Agent`.
