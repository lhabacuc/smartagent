
from agent import Agent

def main():
    agent = Agent(model="groq", enable_history=True, history_limit=5)
    print("=== Chatbot Simples ===")
    print("Digite 'sair' para encerrar.\n")
    while True:
        user_input = input("Você: ")
        if user_input.strip().lower() == "sair":
            break
        resposta = agent.chat(user_input)
        print(f"Agente: {resposta}\n")
    print("\nHistórico da sessão:")
    for i, h in enumerate(agent.get_history(), 1):
        print(f"{i}: {h['user_prompt']} -> {h['final_response']}")

if __name__ == "__main__":
    main()
