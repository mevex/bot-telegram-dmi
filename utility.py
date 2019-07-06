def sanitize(word: str, allowed_characters: list) -> str:
    for c in word:
        if c not in allowed_characters:
            word = word.replace(c, '')

    return word


def generate_email(name: str) -> str:
    name = name.lower()
    if name == 'de lillo silvana':
        return 'silvana.delillo@unipg.it'
    if name == 'mamone capria marco':
        return 'marco.mamonecapria@unipg.it'
    if name == 'nucci maria clara':
        return 'mariaclara.nucci@unipg.it'
    if name == 'pinotti maria cristina':
        return 'cristina.pinotti@unipg.it'

    split = name.split()
    email = '{nome}.{cognome}@unipg.it'.format(
        nome=split[1], cognome=split[0])

    return email


def month_convertion(month: str) -> str:
    if month.isdigit():
        return month
    if month == 'gennaio':
        return '1'
    elif month == 'febbraio':
        return '2'
    elif month == 'marzo':
        return '3'
    elif month == 'aprile':
        return '4'
    elif month == 'maggio':
        return '5'
    elif month == 'giugno':
        return '6'
    elif month == 'luglio':
        return '7'
    elif month == 'agosto':
        return '8'
    elif month == 'settembre':
        return '9'
    elif month == 'ottombre':
        return '10'
    elif month == 'novembre':
        return '11'
    elif month == 'dicembre':
        return '12'
