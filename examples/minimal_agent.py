
import sys
sys.path.insert(0, '..')

from agent import Agent

# Criar agente com Groq (pode usar: openai, gemini, grok, ollama, llama)
agent = Agent(model="groq")

# Registrar ferramentas
@agent.tool
def get_products_summary(query="", min_price=0, max_price=999999):
    """Retorna resumo de produtos"""
    return f"Produtos entre {min_price} e {max_price} sobre '{query}'"

@agent.tool
def get_products(query="", min_price=0, max_price=999999):
    """Lista produtos disponíveis"""
    return [
        {"nome": "Mouse", "preço": 50}, 
        {"nome": "Teclado", "preço": 80},
        {"nome": "Monitor", "preço": 300}
    ]

# Executar consulta
if __name__ == "__main__":
    response = agent.process("Quais produtos baratos estão disponíveis?")
    
    print("\n=== Resposta Final ===")
    print(response['final_response'])
    
    print("\n=== Ferramentas Executadas ===")
    print(response['executed_tools'])
    
    print("\n=== Dados Utilizados ===")
    print(response['used_data'])
