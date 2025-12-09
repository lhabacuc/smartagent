
#!/usr/bin/env python3

import subprocess
import sys
import os

def run_command(cmd, description):
    """Executa comando e mostra progresso"""
    print(f"\n {description}...")
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f" {description} - OK")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    print("=" * 60)
    print(" INSTALADOR SMARTAGENT")
    print("=" * 60)
    
    # Verificar Python
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"❌ Python 3.8+ necessário. Você tem: {python_version.major}.{python_version.minor}")
        sys.exit(1)
    
    print(f" Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Mudar para diretório do script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Atualizar pip
    run_command(f"{sys.executable} -m pip install --upgrade pip", "Atualizando pip")

    run_command(f"{sys.executable} -m pip install requests", "Instalando dependências")
    
    # Instalar em modo desenvolvimento
    run_command(f"{sys.executable} -m pip install -e .", "Instalando SmartAgent")
    
    print("\n" + "=" * 60)
    print(" INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    print("\n Uso:")
    print("   from agent import Agent")
    print("   agent = Agent(model='groq')")
    print("\n Veja exemplos em: agent/examples/")
    print()

if __name__ == "__main__":
    main()
