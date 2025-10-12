
# 📦 Guia de Instalação - SmartAgent

## Métodos de Instalação

### 1. Instalação Rápida (Recomendado)

```bash
cd agent
python install.py
```

### 2. Usando o Script Bash

```bash
cd agent
chmod +x install.sh
./install.sh
```

### 3. Instalação Manual

```bash
cd agent
pip install requests
pip install -e .
```

### 4. Usando Makefile

```bash
cd agent
make install
```

## Verificar Instalação

```python
from agent import Agent

agent = Agent(model="groq")
print("✅ SmartAgent instalado com sucesso!")
```

## Configuração de API Keys

Configure as chaves de API como variáveis de ambiente:

```bash
# Groq
export GROQ_API_KEY="sua_chave_aqui"

# OpenAI
export OPENAI_API_KEY="sua_chave_aqui"

# Google Gemini
export GOOGLE_API_KEY="sua_chave_aqui"

# Grok
export GROK_API_KEY="sua_chave_aqui"

# Modelo
export LLM="seu_modelo_aqui"
```

Ou passe diretamente no código:

```python
agent = Agent(model="groq", api_key="sua_chave")
```

## Desinstalação

```bash
make uninstall
# ou
pip uninstall agent
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
