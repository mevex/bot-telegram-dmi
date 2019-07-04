#!/root/Documents/progetto_ingegneria/venv_ingegneria/bin/python3
from config import TOKEN
from config_ext import ALLOWED_CHARS
from utility import sanitize, generate_email

from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters

from bs4 import BeautifulSoup
import requests


def start(update, context):
    start_msg = 'Bot dmi'
    update.message.reply_markdown(start_msg)


def ask_professor_name(update, context):
    ask_msg = 'Scrivi il cognome del professore di cui vuoi sapere i contatti'
    update.message.reply_markdown(ask_msg)
    return 1


def search_professor(update, context):
    prof = update.message.text.lower()
    prof = sanitize(prof, ALLOWED_CHARS)
    print(prof)
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'}
    data = {'search_text': prof, 'search_type': 'cognome'}
    url = 'https://www.unipg.it/rubrica'

    try:
        r = requests.post(url=url, data=data, headers=headers)
    except:
        message = "Spiacente, si è verificato un errore inaspettato.\n Riprova"
        update.message.reply_markdown(message)
        return ConversationHandler.END

    content = BeautifulSoup(r.content, 'html.parser')

    miss_error = list(content.find_all(attrs={'class': 'alert-message'}))
    if not miss_error:
        nome = content.find_all(
            attrs={'class': 'up-fontsize-150 border-bottom mb-2', 'itemprop': 'name'})
        tel = content.find_all(attrs={'itemprop': 'telephone'})

        professori = []
        dict_professore = {}
        for i in range(0, len(nome)):
            email = generate_email(nome[i].text)
            dict_professore['nome'] = nome[i].text.title()
            dict_professore['tel'] = tel[i].text.replace(
                ' ', '') if tel else 'Non presente'
            dict_professore['email'] = email if email else 'Non presente'

            professori.append(dict(dict_professore))

        for prof in professori:
            message = '*Professore:* {nome}\n*Telefono:* {tel}\n *Email:* {email}'.format(
                nome=prof['nome'], tel=prof['tel'], email=prof['email'],)
            update.message.reply_markdown(message)

    else:
        message = 'Spiacente, nessun professore trovato relativo al cognome ' + prof.capitalize()
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
print('Ready to rock')

updater.idle()
