import unicodedata
import re


def remove_tildes(text):
    """Removes the accents of each vowel in a text but preserves the 'ñ'.

    :param str text: The text with vowels with accents.

    :return str: The text without the accents.
    """
    result = []
    for char in text:
        # Preserve 'ñ' and 'Ñ'
        if char in {'ñ', 'Ñ'}:
            result.append(char)
        else:
            # Normalize and remove accents from other characters
            decomposed = unicodedata.normalize('NFD', char)
            filtered = ''.join(c for c in decomposed if unicodedata.category(c) != 'Mn')
            result.append(filtered)
    return ''.join(result)


def clean_name(name):
    """Cleans a name by removing numbers, accents, truncating after undesired words, and capitalizing words.

    Args:
        name (str): The name to be cleaned.

    Returns:
        str: The cleaned name.
    """

    # Remove numbers
    name = re.sub(r'\d+', '', name)
    unwanted_substrings = [
        'mat.', '*', '-', '.', 'folio cal.', 'folio cal', 'folio'
    ]
    # Only removes the specified words
    name = name.lower()
    for substring in unwanted_substrings:
        name = name.replace(substring, '')

    # Remove tildes (accents) from vowels
    name = remove_tildes(name)

    # List of undesired words to truncate from
    undesired_words = ["nueva", "nuevo", "retirado", "retirada", "desertor", "desertora", "se", '-', '- ', 'tuvo',
                       'paso', 'nvo', 'tambien', 'inicio', 'inicia', 'segun', ' mat.', 'no promov', 'promov', 'no promovido',
                       'apellidos']
    pattern = r'\b(?:' + '|'.join(undesired_words) + r')\b'

    # Truncate everything starting from the first undesired word (case-insensitive)
    match = re.search(pattern, name, flags=re.IGNORECASE)
    if match:
        name = name[:match.start()]

    # Upper case each word and remove extra spaces
    name = ' '.join(word.upper() for word in name.split())

    return name.strip()


def clean_column_name(column):
    """Cleans the column name by:
    - Replacing spaces with underscores.
    - Removing accents from vowels.

    :param str column: The original column name.

    :return str: The cleaned column name.
    """
    # Replace spaces with underscores
    column = str(column).lower().strip().replace(" ", "_").replace('.', '').replace('(', '_').replace(')', '').replace('-', '_').replace("'", '').replace('°','')

    # Normalize and remove accents
    column = remove_tildes(column)

    # Replace the shortened values to the known values
    full_names = {
        'cn': 'c_naturales',
        'cnat': 'c_naturales',
        'cs': 'ciencias_sociales',
        'art': 'artistica',
        'eti': 'etica',
        'ef': 'educacion_fisica',
        'rel': 'religion',

        'lc': 'lengua_castellana',
        'esp': 'lengua_castellana',

        'ing': 'ingles',
        'mat': 'matematicas',
        'tec': 'tecnologia',
        'fil': 'filosofia',
        'filo': 'filosofia',

        'qui': 'quimica',
        'qu': 'quimica',
        'biol': 'biologia',
        'fis': 'fisica',

        'soc': 'ciencias_sociales',

        'cep': 'economia_y_politica',
        'ciencias_sociales-ciencias_econ_y_polit': 'economia_y_politica',
        'ciencias_sociales_ciencias_econ_y_polit': 'economia_y_politica',

        'ce_cp': 'economia_y_politica',
        'c_naturales_qca': 'quimica',
        'mt': 'media_tecnica',
        'media_tecnica_dllo_soft': 'media_tecnica',
        'multimedia': 'media_tecnica',
        'negocios': 'media_tecnica',
        'software': 'media_tecnica',
        'media_tecnica:_desarrollo_de_software': 'media_tecnica',
        'dllo_de_multimedia': 'media_tecnica',
        'diseño_e_integracion_de_multimedia': 'media_tecnica',
        'diseño_multimedia': 'media_tecnica',
        'media_tecnica:_negocios_internacionales': 'media_tecnica',
        'media_tecnica_diseño_e_integ': 'media_tecnica',
        'media_tecnica__diseño_e_integrac_de_multimedia': 'media_tecnica',
        'media_tecnica_diseño_e_int_multimedia': 'media_tecnica',

        'pol/econ': 'economia_y_politica',
        'ciencias_politicas_y_economicas': 'economia_y_politica',
        'ciencias_econ_y_polit': 'economia_y_politica',
        'ce-cp': 'economia_y_politica',

        'psicos': 'psicosexualidad',
        'psi': 'psicosexualidad',
        'emp': 'emprendimiento',
        'emprend': 'emprendimiento'

    }

    if column in full_names.keys():
        column = full_names[column]

    # Convert to lowercase and strip any extra whitespace
    return column
