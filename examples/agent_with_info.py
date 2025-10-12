
import sys
sys.path.insert(0, '..')

from agent import Agent

# Criar agente com instruções customizadas
agent = Agent(
    model="groq",
    info="""
    Você é um assistente especializado em Linux.
    - Sempre explique comandos de forma didática
    - Use emojis para deixar respostas mais amigáveis
    - Priorize segurança ao sugerir comandos
    - Forneça alternativas quando possível
    """
)

# Registrar ferramentas
@agent.tool
def executar_comando(comando: str):
    """Executa comando shell"""
    import subprocess
    try:
        result = subprocess.run(
            comando, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=5
        )
        return {
            "saida": result.stdout,
            "erro": result.stderr,
            "sucesso": result.returncode == 0
        }
    except Exception as e:
        return {"erro": str(e), "sucesso": False}

@agent.tool
def listar_arquivos(diretorio: str = "."):
    """Lista arquivos em diretório"""
    import os
    try:
        return os.listdir(diretorio)
    except Exception as e:
        return {"erro": str(e)}

# Testar
if __name__ == "__main__":
    print("=== Agente com Info Customizado ===\n")
    
    # Teste 1
    print("1️⃣ Pergunta técnica:")
    response = agent.chat("Como listar arquivos ocultos no Linux?")
    print(f"   {response}\n")
    
    # Teste 2
    print("2️⃣ Executar comando:")
    response = agent.chat("Lista os arquivos do diretório atual")
    print(f"   {response}\n")
    
    # Teste 3
    print("3️⃣ Pergunta de segurança:")
    response = agent.chat("Como posso deletar tudo no sistema?")
    print(f"   {response}\n")
