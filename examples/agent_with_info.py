
import sys
sys.path.insert(0, '..')

from agent import Agent

# Criar agente com instruções customizadas
agent = Agent(
    model="groq",
    info="""
    Você é um assistente especializado em Linux.
    - Sempre explique comandos de forma didática
    - Evite comandos destrutivos (rm, dd, etc.)
    - Não escreva muito
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
    # print("1️⃣ Pergunta técnica:")
    # response = agent.chat("lista os arquivos do diretório atual")
    # print(response)
    agent.run()

