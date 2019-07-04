#!/root/Documents/progetto_ingegneria/venv_ingegneria/bin/python3
from config import TOKEN
import requests
import telebot
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters
from bs4 import BeautifulSoup
from telegram import ReplyKeyboardMarkup
from telebot import types


def start(update, context):
    start_msg = 'Benvenuto. Questo bot ti permetterá di cercare i contatti dei' \
        ' professori che ti interessano e gli orari di lezione di oggi.'
    markup = types.ReplyKeyboardMarkup(
        one_time_keyboard=True, resize_keyboard=True)
    button_search = types.KeyboardButton('/cerca_professore', )
    button_plan = types.KeyboardButton('/mostra_orario')
    markup.row(button_search, button_plan)
    chat_id = update.message.chat_id
    tb.send_message(chat_id=chat_id, text=start_msg, reply_markup=markup)


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
    # STAMPA GIORNO
    planner_msg = "Di che giorno vuoi sapere l'orario delle lezioni"
    update.message.reply_markdown(planner_msg)
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'}
    payload = {'key1': 'value1', 'key2': 'value2'}
    url = 'https://servizi.dmi.unipg.it/mrbs/day.php?year=2019&month=06&day=5&area=1&room=3'
    r = requests.get(url=url, params=payload, headers=headers)
    content = BeautifulSoup(r.content, 'html.parser')
    giorno = content.find_all(attrs={'id': 'dwm'})[0].text
    message = giorno.title()
    update.message.reply_markdown(message)
    # STAMPA AULA E LEZIONI/ESAMI

    r = requests.get(url=url)

    content = BeautifulSoup(r.content, 'html.parser')
    rows = content.find('table', id='day_main').tbody.find_all('tr')

    for row in rows:
        cols = row.find_all('td')
        hours = 9
        if cols[0].div.a.text == 'NB19':
            break
        for col in cols:
            class_value = col['class'][0]
            if class_value == 'row_labels':
                message = '*' + col.div.a.text.split('(')[0] + '*\n'
            elif class_value == 'new':
                hours += 1
            else:
                ore = 'dalle ore ' + str(hours)
                hours += int(col.get('colspan'))
                ore += ' alle ore ' + str(hours)
                message += '\t\t• ' + col.div.a.text.title() + ' ~ ' + \
                    col.div.sub.text.title() + '\n\t\t\t\t\t\t' + ore + '\n'

        update.message.reply_markdown(message)

    return ConversationHandler.END


def cancel(update, context):
    cancel_msg = '...'
    update.message.reply_markdown(cancel_msg)
    return ConversationHandler.END


search_cnv = ConversationHandler(
    entry_points=[CommandHandler('cerca_professore', ask_professor_name)],

    states={
        1: [MessageHandler(Filters.text, search_professor)]
    },

    fallbacks=[CommandHandler('cancel', cancel)]
)

updater = Updater(token=TOKEN, use_context=True)
dp = updater.dispatcher
tb = telebot.TeleBot(TOKEN)
dp.add_handler(search_cnv)
dp.add_handler(CommandHandler('start', start))
dp.add_handler(CommandHandler('mostra_orario', show_planner))

updater.start_polling()
updater.idle()
