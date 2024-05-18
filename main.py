from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from solana.account import Account
from solana.rpc.api import Client
from solana.transaction import Transaction
from spl.token import Token
import json

# Configuración del bot de Telegram
TOKEN = "TU_TOKEN_DE_TELEGRAM"
BOT_WALLET_PRIVATE_KEY = "61R3zAYPpQsAvub4mLaocVU7XfPksAbxxxECHm8UVtnTTSkZjigucCc1RU9uDueLabKrf5uTXaS4ymFv9wocvy8Z"
BOT_WALLET_ADDRESS = "3h8aSEnnmMVK6FcBrpWKbVdgeCEeoaaFJVibXTcWSdU9"

# Configuración de la red de Solana
RPC_URL = "https://api.mainnet-beta.solana.com"
solana_client = Client(RPC_URL)

# Configuración del token en preventa
TOKEN_PREVENTA = {
    "nombre": "StonkSol",
    "simbolo": "Stonks",
    "precio": 0.05,  # Precio en Solana o USDC por token
}

# Dirección de la billetera del contrato del token en preventa
TOKEN_PREVENTA_CONTRACT_ADDRESS = "3uTxsxUjdFzqccKE6NeJs2jyfAnJ9xha86ERqhNj2aGu"

# Estado para almacenar la dirección de la billetera del usuario y la cantidad de tokens
user_wallet_state = {}

# Función para procesar la cantidad ingresada por el usuario
def procesar_cantidad(update, context):
    message = update.message
    chat_id = message.chat_id
    text = message.text.strip()  # Eliminar espacios en blanco al inicio y al final

    try:
        cantidad = int(text)
        if 1 <= cantidad <= 20000:
            user_wallet_state[chat_id]["cantidad"] = cantidad
            seleccionar_metodo_pago(chat_id)
        else:
            message.reply_text("Por favor, ingresa una cantidad dentro del rango de 1 a 20,000.")
    except ValueError:
        message.reply_text("Por favor, ingresa una cantidad válida como un número entero.")

# Función para obtener la dirección de billetera del usuario
def obtener_direccion_billetera_usuario(chat_id):
    return wallet_manager.obtener_direccion_billetera_usuario(chat_id)

# Función para mostrar el mensaje de bienvenida y los detalles del token en preventa
def start(update, context):
    # Mensaje de bienvenida y detalles del token
    message = (
        "¡Bienvenido! Este bot te permite comprar tokens en preventa. "
        "Selecciona un token para ver más detalles y realizar tu compra:\n\n"
        "*Token en preventa:* StonkSol\n"
        "*Cantidad de tokens disponibles:* 1,500,000\n"
        "*Precio por token:* $0.05\n"
        "*Smart contract:* [3uTxsxUjdFzqccKE6NeJs2jyfAnJ9xha86ERqhNj2aGu]\n"
        "*Whitepaper:* [https://stonksol-meme.gitbook.io/stonksol-english/]\n"
        "*Redes sociales:* [linktr.ee/stonksol]\n\n"
        "Por favor, ten en cuenta que el precio y la disponibilidad de los tokens están sujetos a cambios.\n\n"
        "Para más detalles sobre el funcionamiento del bot, consultarno al correo stonksolmemekiller@gmail.com."
    )
    
    # Botones de selección de token
    keyboard = [
        [InlineKeyboardButton("Comprar StonkSol", callback_data="token_stonks")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Envío del mensaje al usuario
    update.message.reply_text(message, reply_markup=reply_markup, parse_mode='MarkdownV2')

# Función para manejar los botones de selección de método de pago
def seleccionar_metodo_pago(chat_id):
    message = "Selecciona un método de pago:"
    keyboard = [
        [InlineKeyboardButton("Pagar con Solana", callback_data="payment_solana")],
        [InlineKeyboardButton("Pagar con USDC", callback_data="payment_usdc")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)

# Función para procesar la selección de método de pago
def procesar_metodo_pago(update, context):
    query = update.callback_query
    query.answer()
    method = query.data.split("_")[1]

    chat_id = query.message.chat_id
    user_wallet_state[chat_id]["address"] = obtener_direccion_billetera_usuario(chat_id)
    token_symbol = "Stonks"  # Esto debe obtenerse de acuerdo a la elección del usuario en start() o button()
    procesar_compra(chat_id, token_symbol, method)

# Función para procesar la compra del token
def procesar_compra(chat_id, token_symbol, metodo_pago):
    user_info = user_wallet_state[chat_id]
    cantidad = user_info["cantidad"]
    address = user_info["address"]

    if cantidad and address:
        # Calcular la cantidad de tokens a comprar
        cantidad_tokens = int(cantidad * TOKEN_PREVENTA["precio"] * 10**Token(solana_client, TOKEN_PREVENTA_CONTRACT_ADDRESS).decimals())

        # Construir la transacción para enviar los tokens al usuario
        transaction = Transaction()
        transaction.add(Token(solana_client, TOKEN_PREVENTA_CONTRACT_ADDRESS).transfer(
            sender=Account.from_base58(BOT_WALLET_PRIVATE_KEY),
            recipient=address,
            amount=cantidad_tokens
        ))

        # Firmar y enviar la transacción
        solana_client.send_transaction(transaction)

        # Enviar mensaje de confirmación al usuario
        mensaje = f"¡La compra de {cantidad} {token_symbol} se ha procesado correctamente y los tokens han sido enviados a tu billetera!"
        context.bot.send_message(chat_id=chat_id, text=mensaje)
    else:
        context.bot.send_message(chat_id=chat_id, text="Por favor, selecciona una cantidad y pega tu dirección de billetera en el chat.")

# Clase para manejar el almacenamiento de las direcciones de billetera
class WalletManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.user_wallets = self.load_wallets()

    def load_wallets(self):
        try:
            with open(self.file_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_wallets(self):
        with open(self.file_path, "w") as file:
            json.dump(self.user_wallets, file)

    def guardar_direccion_billetera(self, usuario_id, direccion_billetera):
        self.user_wallets[usuario_id] = direccion_billetera
        self.save_wallets()

    def obtener_direccion_billetera_usuario(self, usuario_id):
        return self.user_wallets.get(usuario_id)

# Ejemplo de uso:
WALLETS_FILE = "user_wallets.json"
wallet_manager = WalletManager(WALLETS_FILE)
# Handler para manejar la entrada de mensajes del usuario
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, procesar_cantidad))
    dp.add_handler(CallbackQueryHandler(procesar_metodo_pago))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
