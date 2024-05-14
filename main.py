from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from urllib.parse import quote_plus
from solana.rpc.async_api import AsyncClient
import asyncio

# Telegram bot token
TOKEN = "token aqui"

# Solana OAuth URL
SOLANA_AUTH_URL = "https://www.solana.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&state={state}"

# Dirección de la wallet donde están los tokens de la pool
WALLET_ADDRESS = "3h8aSEnnmMVK6FcBrpWKbVdgeCEeoaaFJVibXTcWSdU9"

# Lista de tokens en preventa con su tiempo de duración
TOKENS_EN_PREVENTA = [
    {"nombre": "StonkSol", "simbolo": "Stonks", "precio": 0.05, "duracion": "2 semanas"},
    #{"nombre": "Token B", "simbolo": "TKB", "precio": 2.0, "duracion": "1 mes"},
   # {"nombre": "Token C", "simbolo": "TKC", "precio": 3.0, "duracion": "3 semanas"}
]

SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"

async def get_wallet_balance(wallet_address):
    async with AsyncClient(SOLANA_RPC_URL) as client:
        response = await client.get_balance(wallet_address)
        balance_lamports = response['result']['value']
        balance_sol = balance_lamports / 1e9  # Convertir de lamports a SOL
        return balance_sol

def get_wallet_balance_sync(wallet_address):
    return asyncio.run(get_wallet_balance(wallet_address))

def start(update, context):
    message = ("¡Bienvenido! Este bot te permite comprar tokens en preventa. "
               "Por favor, sigue los pasos a continuación:\n\n"
               "1. Conecta tu billetera de Solana presionando el botón 'Conectar'.\n"
               "2. Una vez conectado, selecciona el token que deseas comprar de la lista.\n\n"
               "Para más información, visita nuestras redes sociales:\n"
               "- [Twitter](https://twitter.com/TU_USUARIO_DE_TWITTER)\n"
               "- [Telegram](https://t.me/TU_CANAL_DE_TELEGRAM)\n\n"
               "También puedes consultar nuestro [whitepaper](https://tu-url-del-whitepaper.com)")
    
    keyboard = [[InlineKeyboardButton("Conectar", url=generate_auth_url(update.effective_chat.id))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(message, reply_markup=reply_markup, parse_mode='MarkdownV2')

def generate_auth_url(chat_id):
    client_id = "TU_CLIENT_ID_DE_SOLANA"
    redirect_uri = "https://tu-url-de-redireccion.com/auth_callback"
    scope = "wallet:accounts:read"  # Permisos requeridos
    state = chat_id
    return SOLANA_AUTH_URL.format(client_id=client_id, redirect_uri=quote_plus(redirect_uri), scope=scope, state=state)

def conectar(update, context):
    message = "Por favor, conecta tu billetera de Solana para continuar."
    keyboard = [[InlineKeyboardButton("Conectar", url=generate_auth_url(update.effective_chat.id))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(message, reply_markup=reply_markup)

def auth_callback(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    query.answer()
    message = "Tu billetera de Solana ha sido conectada con éxito. A continuación, puedes ver la lista de tokens en preventa:"
    context.bot.send_message(chat_id=chat_id, text=message)
    show_tokens(chat_id, context)

def process_message(update, context):
    message = update.message.text
    try:
        amount = float(message)
        if amount <= 0:
            raise ValueError
        chat_id = update.message.chat_id
        context.bot.send_message(chat_id=chat_id, text=f"Has solicitado comprar {amount} tokens. Por favor, realiza la transacción de intercambio.")
        # Aquí puedes implementar la lógica para realizar la transacción de intercambio
    except ValueError:
        update.message.reply_text("Por favor, introduce una cantidad válida de tokens.")

def button(update, context):
    query = update.callback_query
    query.answer()
    token_solicitado = query.data.split("_")[1]
    query.edit_message_text(f"Has seleccionado el token {token_solicitado}. Por favor, especifica la cantidad que deseas comprar.")

def show_tokens(chat_id, context):
    balance = get_wallet_balance_sync(WALLET_ADDRESS)
    message = f"Saldo de la wallet de la pool: {balance} tokens\n\n"
    message += "Lista de tokens en preventa:\n"
    for token in TOKENS_EN_PREVENTA:
        message += f"- {token['nombre']} ({token['simbolo']}) - Precio: ${token['precio']} - Duración: {token['duracion']}\n"
    message += ("\nPara comprar un token, simplemente selecciona uno de la lista.")
    keyboard = [[InlineKeyboardButton(token["nombre"], callback_data=f"token_{token['simbolo']}")] for token in TOKENS_EN_PREVENTA]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("conectar", conectar))
    dp.add_handler(CallbackQueryHandler(auth_callback, pattern='^auth_callback$'))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, process_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
