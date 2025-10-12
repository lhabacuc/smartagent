
# 🐧 Linux PC Control Agent

Exemplo de agente inteligente para controlar um PC Linux através de comandos naturais.

## 📋 Funcionalidades

### Sistema
- ✅ Executar comandos shell
- ✅ Informações de CPU, memória e disco
- ✅ Data/hora do sistema

### Arquivos
- ✅ Listar arquivos e pastas
- ✅ Ler conteúdo de arquivos
- ✅ Criar novos arquivos

### Processos
- ✅ Listar processos em execução
- ✅ Encerrar processos por PID
- ✅ Monitorar uso de recursos

### Rede
- ✅ Informações de interfaces de rede
- ✅ IPs e status das interfaces

## 🚀 Como Usar

### Pré-requisitos

```bash
pip install psutil
```

### Configurar API Key

```bash
export GROQ_API_KEY="sua-chave-aqui"
```

### Executar

```bash
cd agent/examples
python linux_pc_agent.py
```

## 💡 Exemplos de Comandos

```python
# Informações do sistema
"Qual o uso de CPU e memória?"
"Quanto espaço em disco tenho?"

# Gerenciar arquivos
"Lista os arquivos da pasta /home"
"Cria um arquivo log.txt com a data atual"
"Lê o conteúdo do arquivo config.py"

# Processos
"Quais processos estão usando mais CPU?"
"Lista os 10 processos principais"
"Mata o processo com PID 1234"

# Rede
"Quais interfaces de rede estão ativas?"
"Qual meu IP?"

# Comandos Linux
"Executa o comando 'df -h'"
"Mostra o uptime do sistema"
"Lista usuários logados"
```

## ⚠️ Segurança

Este agente pode executar comandos do sistema. Use com cuidado:

- ✅ Revise os comandos antes de executar
- ✅ Não use com privilégios root desnecessários
- ✅ Limite o acesso em ambientes de produção
- ✅ Monitore logs de execução

## 🔧 Personalização

Você pode adicionar novas ferramentas facilmente:

```python
@agent.tool
def minha_ferramenta(parametro: str):
    """Descrição da ferramenta"""
    # Sua lógica aqui
    return resultado
```

## 📊 Estrutura do Código

```
linux_pc_agent.py
├── Ferramentas do Sistema (5)
├── Ferramentas de Processos (3)
├── Ferramentas de Rede (1)
└── Modo Interativo
```
