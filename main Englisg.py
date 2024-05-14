from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from urllib.parse import quote_plus
from solana.rpc.async_api import AsyncClient
import asyncio

# Telegram bot token
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# Solana OAuth URL
SOLANA_AUTH_URL = "https://www.solana.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&state={state}"

# Address of the wallet containing the pool tokens
WALLET_ADDRESS = "YOUR_WALLET_ADDRESS"

# List of tokens in presale with their duration
TOKENS_IN_PRESALE = [
    {"name": "StonkSol", "symbol": "Stonks", "price": 0.05, "duration": "2 weeks"},
    #{"name": "Token B", "symbol": "TKB", "price": 2.0, "duration": "1 month"},
    #{"name": "Token C", "symbol": "TKC", "price": 3.0, "duration": "3 weeks"}
]

SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"

async def get_wallet_balance(wallet_address):
    async with AsyncClient(SOLANA_RPC_URL) as client:
        response = await client.get_balance(wallet_address)
        balance_lamports = response['result']['value']
        balance_sol = balance_lamports / 1e9  # Convert lamports to SOL
        return balance_sol

def get_wallet_balance_sync(wallet_address):
    return asyncio.run(get_wallet_balance(wallet_address))

def start(update, context):
    message = ("Welcome! This bot allows you to buy tokens in presale. "
               "Please follow the steps below:\n\n"
               "1. Connect your Solana wallet by pressing the 'Connect' button.\n"
               "2. Once connected, select the token you want to buy from the list.\n\n"
               "For more information, visit our social media:\n"
               "- [Twitter](https://twitter.com/YOUR_TWITTER_USERNAME)\n"
               "- [Telegram](https://t.me/YOUR_TELEGRAM_CHANNEL)\n\n"
               "You can also check out our [whitepaper](https://your-whitepaper-url.com)")
    
    keyboard = [[InlineKeyboardButton("Connect", url=generate_auth_url(update.effective_chat.id))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(message, reply_markup=reply_markup, parse_mode='MarkdownV2')

def generate_auth_url(chat_id):
    client_id = "YOUR_SOLANA_CLIENT_ID"
    redirect_uri = "https://your-redirect-url.com/auth_callback"
    scope = "wallet:accounts:read"  # Required permissions
    state = chat_id
    return SOLANA_AUTH_URL.format(client_id=client_id, redirect_uri=quote_plus(redirect_uri), scope=scope, state=state)

def connect(update, context):
    message = "Please connect your Solana wallet to continue."
    keyboard = [[InlineKeyboardButton("Connect", url=generate_auth_url(update.effective_chat.id))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(message, reply_markup=reply_markup)

def auth_callback(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    query.answer()
    message = "Your Solana wallet has been successfully connected. Here is the list of tokens in presale:"
    context.bot.send_message(chat_id=chat_id, text=message)
    show_tokens(chat_id, context)

def process_message(update, context):
    message = update.message.text
    try:
        amount = float(message)
        if amount <= 0:
            raise ValueError
        chat_id = update.message.chat_id
        context.bot.send_message(chat_id=chat_id, text=f"You have requested to buy {amount} tokens. Please proceed with the exchange transaction.")
        # Here you can implement the logic to perform the exchange transaction
    except ValueError:
        update.message.reply_text("Please enter a valid amount of tokens.")

def button(update, context):
    query = update.callback_query
    query.answer()
    selected_token = query.data.split("_")[1]
    query.edit_message_text(f"You have selected the token {selected_token}. Please specify the amount you want to buy.")

def show_tokens(chat_id, context):
    balance = get_wallet_balance_sync(WALLET_ADDRESS)
    message = f"Pool wallet balance: {balance} tokens\n\n"
    message += "List of tokens in presale:\n"
    for token in TOKENS_IN_PRESALE:
        message += f"- {token['name']} ({token['symbol']}) - Price: ${token['price']} - Duration: {token['duration']}\n"
    message += ("\nTo buy a token, simply select one from the list.")
    keyboard = [[InlineKeyboardButton(token["name"], callback_data=f"token_{token['symbol']}")] for token in TOKENS_IN_PRESALE]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("connect", connect))
    dp.add_handler(CallbackQueryHandler(auth_callback, pattern='^auth_callback$'))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, process_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
