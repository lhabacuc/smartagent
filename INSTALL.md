
# 📦 Guia de Instalação - SmartAgent

## Métodos de Instalação

### 1. Instalação Rápida (Recomendado)

```bash
python install.py
```

### 2. Usando o Script Bash

```bash
chmod +x install.sh
./install.sh
```

### 3. Instalação Manual

```bash
pip install requests
pip install -e .
```

### 4. Usando Makefile

```bash
make install
```

## Verificar Instalação

```python
from agent import Agent

agent = Agent(provider="groq")
print("✅ SmartAgent instalado com sucesso!")
```

## Configuração de API Keys

Configure as chaves de API como variáveis de ambiente:

```bash
# Provider default global (opcional)
export SMARTAGENT_PROVIDER="groq"

# Groq
export GROQ_API_KEY="sua_chave_aqui"

# OpenAI
export OPENAI_API_KEY="sua_chave_aqui"

# Google Gemini
export GEMINI_API_KEY="sua_chave_aqui"

# Grok
export XAI_API_KEY="sua_chave_aqui"

# Modelo global (novo)
export SMARTAGENT_MODEL="seu_modelo_aqui"

# Modelo por provider (opcional)
export SMARTAGENT_OPENAI_MODEL="gpt-4o-mini"
export SMARTAGENT_GROQ_MODEL="qwen/qwen3-32b"

# Rede (opcional)
export SMARTAGENT_TIMEOUT="30"
export SMARTAGENT_RETRIES="2"

# Compatibilidade legada
export LLM="seu_modelo_aqui"
```

Ou passe diretamente no código:

```python
agent = Agent(provider="groq", api_key="sua_chave")
```

## Desinstalação

```bash
make uninstall
# ou
pip uninstall smartagent-sf
```

## Problemas Comuns

### Erro: "requests module not found"
```bash
pip install requests
```

### Erro: "Permission denied"
```bash
chmod +x install.sh
# ou use sudo se necessário
sudo python install.py
```

## Desenvolvimento

Para instalar em modo desenvolvimento com ferramentas extras:

```bash
make dev
# ou
pip install -e ".[dev]"
```
