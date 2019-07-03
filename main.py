#!/root/Documents/progetto_ingegneria/venv_ingegneria/bin/python3
from config import TOKEN

from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters

from bs4 import BeautifulSoup
import requests


def start(update, context):
    start_msg = 'Benvenuto. Questo bot ti permetterá di cercare i contatti dei' \
        'professori che ti interessano e gli orari di lezione di oggi.'
    update.message.reply_markdown(start_msg)


def ask_professor_name(update, context):
    ask_msg = 'Scrivi il cognome del professore di cui vuoi sapere i contatti'
    update.message.reply_markdown(ask_msg)
    return 1


def search_professor(update, context):
    prof = update.message.text
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'}
    data = {'search_text': prof, 'search_type': 'cognome'}
    url = 'https://www.unipg.it/rubrica'
    r = requests.post(url=url, data=data, headers=headers)

    content = BeautifulSoup(r.content, 'html.parser')
    professore = content.find_all(
        attrs={'class': 'up-fontsize-150 border-bottom mb-2', 'itemprop': 'name'})[0].text
    telefono = content.find_all(attrs={'itemprop': 'telephone'})[0].text
    split = professore.split()
    email = split[1].lower() + '.' + split[0].lower() + '@unipg.it'

    message = 'Professore: ' + professore.title() + \
        '\nTelefono: ' + telefono.replace(' ', '') + '\nEmail: ' + email
    update.message.reply_markdown(message)
    return ConversationHandler.END


def show_planner(update, context):
    planner_msg = 'Orario del giorno'
    update.message.reply_markdown(planner_msg)


def cancel(update, context):
    cancel_msg = '...'
    update.message.reply_markdown(cancel_msg)
    return ConversationHandler.END


updater = Updater(token=TOKEN, use_context=True)
dp = updater.dispatcher
search_cnv = ConversationHandler(
    entry_points=[CommandHandler('cerca_professore', ask_professor_name)],

    states={
        1: [MessageHandler(Filters.text, search_professor)]
    },

    fallbacks=[CommandHandler('cancel', cancel)]
)

dp.add_handler(search_cnv)
dp.add_handler(CommandHandler('start', start))
dp.add_handler(CommandHandler('mostra_orario', show_planner))

updater.start_polling()
updater.idle()
