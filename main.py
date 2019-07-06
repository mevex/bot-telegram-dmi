#!venv_ingegneria/bin/python3
# Own imports
from config import TOKEN
from config_ext import ALLOWED_CHARS
from utility import sanitize, generate_email, month_convertion

# External imports
import datetime
import requests
import telebot
import re
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters
from bs4 import BeautifulSoup
from telegram import ReplyKeyboardMarkup
from telebot import types


def start(update, context):
    start_msg = 'Benvenuto. Questo bot ti permetterà di cercare i contatti dei' \
        ' professori che ti interessano e gli orari di lezione.'
    markup = types.ReplyKeyboardMarkup(
        one_time_keyboard=True, resize_keyboard=True)
    button_search = types.KeyboardButton('/cerca_professore', )
    button_plan = types.KeyboardButton('/orario_lezioni')
    markup.row(button_search, button_plan)
    chat_id = update.message.chat_id
    tb.send_message(chat_id=chat_id, text=start_msg, reply_markup=markup)


def ask_professor_name(update, context):
    ask_msg = 'Scrivi il cognome del professore di cui vuoi sapere i contatti'
    update.message.reply_markdown(ask_msg)
    return 1


def search_professor(update, context):
    # Get the message from the user and prepare the post call
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
        message = 'Scrivi il cognome del professore di cui vuoi sapere i contatti'
        update.message.reply_markdown(message)
        return 1

    content = BeautifulSoup(r.content, 'lxml')

    # Check if there search produced results
    miss_error = list(content.find_all(attrs={'class': 'alert-message'}))
    if not miss_error:
        nome = content.find_all(
            attrs={'class': 'up-fontsize-150 border-bottom mb-2', 'itemprop': 'name'})
        tel = content.find_all(attrs={'itemprop': 'telephone'})
        html_professori = content.find_all('dl', attrs={'class': 'row'})

        professori = []
        dict_professore = {}
        for i in range(0, len(nome)):
            email = generate_email(nome[i].text)
            dict_professore['nome'] = nome[i].text.title()
            dict_professore['tel'] = tel[i].text.replace(
                ' ', '') if tel else 'Non presente'
            dict_professore['email'] = email if email else 'Non presente'

            professori.append(dict(dict_professore))

        for index, prof in enumerate(professori):
            campi = html_professori[index].find_all('dd')
            for campo in campi:
                if campo.text == 'Dipartimento di matematica e informatica':
                    message = '*Professore:* {nome}\n*Telefono:* {tel}\n *Email:* {email}'.format(
                        nome=prof['nome'], tel=prof['tel'], email=prof['email'])
                    update.message.reply_markdown(message)

    else:
        message = 'Spiacente, nessun professore trovato relativo al cognome {cognome}.\n Riprova a scriverlo'.format(
            cognome=prof.capitalize())
        update.message.reply_markdown(message)
        return 1

    return ConversationHandler.END


def ask_day(update, context):
    ask_msg = "Di che giorno vuoi sapere l'orario delle lezioni (giorno mese anno)"
    update.message.reply_markdown(ask_msg)
    return 1


def show_planner(update, context):
    # Get the message from the user
    # and see if it matches the expected format
    reg_ex = r'^([1-9]|[0-2][0-9]|(3)[0-1])((\s)|(\/))([1-9]|(0)[1-9]|(1)[0-2]|gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottebre|novembre|dicembre)((\s)|(\/))(([0-2][0-9])|((20)((0)[0-9]|[1-2][0-9])))$'
    input_data = update.message.text.lower()
    result = re.match(reg_ex, input_data)

    if result:
        if '/' in input_data:
            giorno, mese, anno = update.message.text.split('/')
            mese = month_convertion(mese)
        else:
            giorno, mese, anno = update.message.text.split()
            mese = month_convertion(mese)

        # If the input provided is well formatted
        # check that the date actually exists
        try:
            datetime.datetime(int(anno), int(mese), int(giorno))
        except ValueError:
            error = 'Data inesistente'
            update.message.reply_markdown(error)
            return ConversationHandler.END

        payload = {'year': anno, 'month': mese,
                   'day': giorno, 'area': '1', 'room': '3'}
        url = 'https://servizi.dmi.unipg.it/mrbs/day.php'

        r = requests.get(url=url, params=payload)

        content = BeautifulSoup(r.content, 'lxml')
        data = content.find_all(attrs={'id': 'dwm'})[0].text
        message = data.title()
        update.message.reply_markdown(message)

        rows = content.find('table', id='day_main').tbody.find_all('tr')
        empty = True

        for row in rows:
            cols = row.find_all('td')
            hours = 9
            lessons = False

            if cols[0].div.a.text == 'NB19':
                break

            for col in cols:
                class_value = col['class'][0]
                if class_value == 'row_labels':
                    aula = col.div.a.text.split('(')[0]
                    message = '*{aula}*\n'.format(aula=aula)
                elif class_value == 'new':
                    hours += 1
                else:
                    lessons = True
                    empty = False
                    ore = 'dalle ore ' + str(hours)
                    hours += int(col.get('colspan'))
                    ore += ' alle ore ' + str(hours)
                    lezione = col.div.a.text.title()
                    prof = col.div.sub.text.title()

                    message += '\t\t• {lezione} ~ {prof}\n\t\t\t\t\t\t{ore}\n'.format(
                        lezione=lezione, prof=prof, ore=ore)
            if lessons:
                update.message.reply_markdown(message)

        if empty:
            message = 'Non ci sono lezioni nella data scelta'
            update.message.reply_markdown(message)

        return ConversationHandler.END

    else:
        fail = 'Input giorno non valido'
        update.message.reply_markdown(fail)
        return ConversationHandler.END


def cancel(update, context):
    cancel_msg = '...'
    update.message.reply_markdown(cancel_msg)
    return ConversationHandler.END


def main():
    # Create the two main conversation for the bot
    search_cnv = ConversationHandler(
        entry_points=[CommandHandler('cerca_professore', ask_professor_name)],

        states={
            1: [MessageHandler(Filters.text, search_professor)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    planner_cnv = ConversationHandler(
        entry_points=[CommandHandler('orario_lezioni', ask_day)],

        states={
            1: [MessageHandler(Filters.text, show_planner)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Main bot startup settings
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(search_cnv)
    dp.add_handler(planner_cnv)
    dp.add_handler(CommandHandler('start', start))

    # Start pooling messages, actual bot start
    updater.start_polling()
    print('Ready to rock')

    updater.idle()

if __name__ == '__main__':
    main()
    tb = telebot.TeleBot(TOKEN)
