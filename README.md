
# SmartAgent 🤖

Biblioteca Python leve para criar agentes de IA com execução determinística em 3 fases.

## Características ✨

- **Multi-Provider**: Suporta Groq, OpenAI, Gemini, Grok, Ollama e Llama
- **3 Fases**: Análise → Execução → Resposta
- **Tool Calls Estruturados**: `tool_calls` com argumentos por função
- **JSON Estrito na Análise**: resposta do LLM para analyzer deve ser JSON válido sem texto extra
- **Execução Validada**: assinatura da função é validada antes da execução
- **Timeout/Retry HTTP**: configurável globalmente por env ou por `Agent(...)`
- **Econômico**: Minimiza uso de tokens
- **Compatível**: mantém fallback para APIs/env vars legadas por janela de transição

## Instalação

```bash
pip install smartagent-sf
```

## Uso Rápido

```python
from smartagent_sf import Agent

# Criar agente
agent = Agent(provider="groq")

# Registrar ferramentas
@agent.tool
def get_products(max_price=100):
    return [{"nome": "Mouse", "preço": 50}]

# Executar
response = agent.chat("Quais produtos baratos?")
print(response)
```

Também é suportado:

```python
from smartagent_sf import agent

bot = agent.Agent(provider="groq")
```

## Instruções Customizadas

Você pode adicionar instruções personalizadas ao agente:

```python
agent = Agent(
    provider="groq",
    info="""
    Você é um assistente especializado em e-commerce.
    - Sempre sugira produtos relacionados
    - Use tom amigável e profissional
    - Destaque promoções quando disponíveis
    """
)
```

## Providers Suportados

- **Groq**: `Agent(provider="groq", api_key="...")`
- **OpenAI**: `Agent(provider="openai", api_key="...")`
- **Gemini**: `Agent(provider="gemini", api_key="...")`
- **Grok**: `Agent(provider="grok", api_key="...")`
- **Ollama**: `Agent(provider="ollama")` (local)
- **Llama**: `Agent(provider="llama", api_key="...")`

## Variáveis de Ambiente

```bash
# Provider default global (opcional)
export SMARTAGENT_PROVIDER="groq"

export GROQ_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
export GEMINI_API_KEY="your-key"
export XAI_API_KEY="your-key"
export LLAMA_API_KEY="your-key"
export SMARTAGENT_API_KEY="your-key"

# Modelo global (novo)
export SMARTAGENT_MODEL="modelo-ai"

# Modelo por provider (opcional)
export SMARTAGENT_OPENAI_MODEL="gpt-4o-mini"
export SMARTAGENT_GROQ_MODEL="qwen/qwen3-32b"

# Rede (opcional)
export SMARTAGENT_TIMEOUT="30"
export SMARTAGENT_RETRIES="2"

# Compatibilidade legada (ainda suportado)
export LLM="modelo-ai"
```

## Compatibilidade (1-2 versões)

- `model=\"groq\"` (estilo antigo) ainda funciona, mas o recomendado é `provider=\"groq\"`.
- As variáveis `*_API_KEY` continuam suportadas.
- `LLM` continua suportada como fallback para modelo global.
- Métodos legados no `Agent` (`help`, `help_var`, `pociveis_erros`, `run`) ainda existem, mas estão deprecados.

## Contrato de Execução de Ferramentas

O analyzer trabalha com `tool_calls`:

```json
{
  "isValid": true,
  "tool_calls": [
    {"name": "get_products", "args": {"max_price": 100}}
  ]
}
```

- A resposta de análise deve ser JSON estrito.
- Cada chamada de função é validada contra a assinatura real da ferramenta.
- O executor retorna resultado estruturado por chamada (`ok`, `result`, `error`).

## Arquitetura

1. **Analyzer**: Determina quais ferramentas executar
2. **Executor**: Executa ferramentas com parâmetros
3. **Responder**: Gera resposta humanizada

## Exemplo Completo

Veja `examples/minimal_agent.py`

## CLI Oficial

Após instalar o pacote, o comando `smartagent` fica disponível:

```bash
smartagent --help
```

Subcomandos:

- `smartagent env-check`: mostra variáveis de ambiente relevantes
- `smartagent doctor --provider openai`: valida configuração local
- `smartagent chat --provider groq`: inicia chat interativo
- `smartagent chat --provider groq --prompt "Olá"`: executa prompt único
- `smartagent run-example --list`: lista exemplos locais
