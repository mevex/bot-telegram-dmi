#!/root/Documents/progetto_ingegneria/venv_ingegneria/bin/python3
from config import TOKEN

from telegram.ext import Updater, CommandHandler

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

updater = Updater(token=TOKEN)
dp = updater.dispatcher

start_handler = CommandHandler('start', start)
dp.add_handler(start_handler)

updater.start_polling()
