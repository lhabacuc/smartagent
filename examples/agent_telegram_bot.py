import os
from agent import Agent
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Substitua pelo seu token do Bot do Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "COLOQUE_SEU_TOKEN_AQUI")

# Inicializa o agente
agent = Agent(model="groq", enable_history=True, history_limit=20)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Olá! Sou o SmartAgent. Envie sua pergunta ou mensagem.")

def handle_message(update: Update, context: CallbackContext):
    user_input = update.message.text
    resposta = agent.chat(user_input)
    update.message.reply_text(resposta)

def history(update: Update, context: CallbackContext):
    hist = agent.get_history()
    if not hist:
        update.message.reply_text("Nenhum histórico disponível.")
    else:
        msgs = [f"{i+1}: {h['user_prompt']} -> {h['final_response']}" for i, h in enumerate(hist)]
        update.message.reply_text("\n".join(msgs))

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("history", history))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    print("Bot do Telegram rodando...")
    updater.idle()

if __name__ == "__main__":
    main()
