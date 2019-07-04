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
