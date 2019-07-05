def sanitize(word: str, allowed_characters: list) -> str:
    for c in word:
        if c not in allowed_characters:
            word = word.replace(c, '')

    return word


def generate_email(name: str) -> str:
    split = name.lower().split()
    email = '{nome}.{cognome}@unipg.it'.format(
        nome=split[1], cognome=split[0])

    # TODO Handle exceptions

    return email


def month_convertion(month: str) -> str:
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
