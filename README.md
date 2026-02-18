
# SmartAgent 🤖

Biblioteca Python leve para criar agentes de IA com execução determinística em 3 fases.

## Características ✨

- **Multi-Provider**: Suporta Groq, OpenAI, Gemini, Grok, Ollama e Llama
- **Sem Schemas**: Não precisa de Pydantic ou definições complexas
- **3 Fases**: Análise → Execução → Resposta
- **Econômico**: Minimiza uso de tokens
- **Simples**: Menos de 500 linhas de código

## Instalação

```bash
# Instalar dependências
pip install requests
```

## Uso Rápido

```python
from agent import Agent

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

## Arquitetura

1. **Analyzer**: Determina quais ferramentas executar
2. **Executor**: Executa ferramentas com parâmetros
3. **Responder**: Gera resposta humanizada

## Exemplo Completo

Veja `examples/minimal_agent.py`
