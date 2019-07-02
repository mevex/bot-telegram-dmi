#!/root/Documents/progetto_ingegneria/venv_ingegneria/bin/python3
from config import TOKEN

from telegram.ext import Updater, CommandHandler

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")


def search_professor(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Cerca un professore usando il suo cognome")


def show_planner(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Orario del giorno")


updater = Updater(token=TOKEN)
dp = updater.dispatcher

start_handler = CommandHandler('start', start)
search_professor_handler = CommandHandler('cerca_professore', search_professor)
show_planner_handler = CommandHandler('mostra_orario', show_planner)

dp.add_handler(start_handler)
dp.add_handler(search_professor_handler)
dp.add_handler(show_planner_handler)

updater.start_polling()
