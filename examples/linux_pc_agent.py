
import sys
sys.path.insert(0, '..')

from agent import Agent
import subprocess
import os
import psutil
from datetime import datetime

# Criar agente com Groq (pode usar: openai, gemini, grok, ollama, llama)
agent = Agent(model="groq")

# ==========================================
# FERRAMENTAS DO SISTEMA
# ==========================================

@agent.tool
def executar_comando(comando: str):
    """Executa um comando shell no terminal Linux"""
    try:
        result = subprocess.run(
            comando, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=10
        )
        return {
            "sucesso": result.returncode == 0,
            "saida": result.stdout,
            "erro": result.stderr
        }
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

@agent.tool
def listar_arquivos(diretorio: str = "."):
    """Lista arquivos e pastas em um diretório"""
    try:
        items = []
        for item in os.listdir(diretorio):
            path = os.path.join(diretorio, item)
            items.append({
                "nome": item,
                "tipo": "pasta" if os.path.isdir(path) else "arquivo",
                "tamanho": os.path.getsize(path) if os.path.isfile(path) else 0
            })
        return items
    except Exception as e:
        return {"erro": str(e)}

@agent.tool
def ler_arquivo(caminho: str, linhas: int = 20):
    """Lê o conteúdo de um arquivo (primeiras N linhas)"""
    try:
        with open(caminho, 'r') as f:
            conteudo = f.readlines()[:linhas]
        return {
            "caminho": caminho,
            "linhas_lidas": len(conteudo),
            "conteudo": ''.join(conteudo)
        }
    except Exception as e:
        return {"erro": str(e)}

@agent.tool
def criar_arquivo(caminho: str, conteudo: str):
    """Cria um novo arquivo com conteúdo"""
    try:
        with open(caminho, 'w') as f:
            f.write(conteudo)
        return {"sucesso": True, "caminho": caminho}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

# ==========================================
# FERRAMENTAS DE PROCESSOS
# ==========================================

@agent.tool
def listar_processos(limite: int = 10):
    """Lista processos em execução ordenados por uso de CPU"""
    try:
        processos = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processos.append({
                    "pid": proc.info['pid'],
                    "nome": proc.info['name'],
                    "cpu": proc.info['cpu_percent'],
                    "memoria": round(proc.info['memory_percent'], 2)
                })
            except:
                pass
        
        # Ordenar por CPU
        processos = sorted(processos, key=lambda x: x['cpu'], reverse=True)[:limite]
        return processos
    except Exception as e:
        return {"erro": str(e)}

@agent.tool
def info_sistema():
    """Retorna informações do sistema"""
    try:
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memoria_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "memoria_usada_gb": round(psutil.virtual_memory().used / (1024**3), 2),
            "memoria_percent": psutil.virtual_memory().percent,
            "disco_total_gb": round(psutil.disk_usage('/').total / (1024**3), 2),
            "disco_usado_gb": round(psutil.disk_usage('/').used / (1024**3), 2),
            "disco_percent": psutil.disk_usage('/').percent,
            "hora_sistema": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {"erro": str(e)}

@agent.tool
def matar_processo(pid: int):
    """Encerra um processo pelo PID"""
    try:
        proc = psutil.Process(pid)
        nome = proc.name()
        proc.terminate()
        return {"sucesso": True, "pid": pid, "nome": nome}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

# ==========================================
# FERRAMENTAS DE REDE
# ==========================================

@agent.tool
def info_rede():
    """Retorna informações de rede"""
    try:
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        
        interfaces = {}
        for interface, addrs_list in addrs.items():
            ips = [addr.address for addr in addrs_list if addr.family == 2]  # IPv4
            if interface in stats:
                interfaces[interface] = {
                    "ips": ips,
                    "ativo": stats[interface].isup
                }
        
        return interfaces
    except Exception as e:
        return {"erro": str(e)}

# ==========================================
# EXEMPLOS DE USO
# ==========================================

if __name__ == "__main__":
    print("=== Agente Linux PC Control ===\n")
    
    # Exemplo 1: Informações do sistema
    print("1️⃣ Verificando status do sistema...")
    response = agent.chat("Qual o uso de CPU e memória do sistema?")
    print(f"   {response}\n")
    
    # Exemplo 2: Listar arquivos
    print("2️⃣ Listando arquivos...")
    response = agent.chat("Lista os arquivos do diretório atual")
    print(f"   {response}\n")
    
    # Exemplo 3: Processos
    print("3️⃣ Verificando processos...")
    response = agent.chat("Quais são os 5 processos usando mais CPU?")
    print(f"   {response}\n")
    
    # Exemplo 4: Informações de rede
    print("4️⃣ Informações de rede...")
    response = agent.chat("Mostra as interfaces de rede ativas")
    print(f"   {response}\n")
    
    # Exemplo 5: Criar arquivo
    print("5️⃣ Criando arquivo de teste...")
    response = agent.chat("Cria um arquivo teste.txt com o conteúdo 'Hello from Agent'")
    print(f"   {response}\n")
    
    # Exemplo 6: Executar comando
    print("6️⃣ Executando comando...")
    response = agent.chat("Executa o comando 'uname -a' para ver informações do kernel")
    print(f"   {response}\n")
    
    # Modo interativo
    print("\n" + "="*50)
    print("Modo Interativo - Digite 'sair' para encerrar")
    print("="*50 + "\n")
    
    while True:
        try:
            user_input = input("Você: ")
            if user_input.lower() in ['sair', 'exit', 'quit']:
                print("Encerrando agente...")
                break
            
            response = agent.chat(user_input)
            print(f"Agente: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\nEncerrando agente...")
            break
        except Exception as e:
            print(f"Erro: {e}\n")
