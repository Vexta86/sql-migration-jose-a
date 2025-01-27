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

    # Remove tildes (accents) from vowels
    name = remove_tildes(name)

    # List of undesired words to truncate from
    undesired_words = ["nueva", "nuevo", "retirado", "retirada", "desertor", "desertora", "se", '-', '- ', 'tuvo', 'paso', 'nvo']
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
    column = column.replace(" ", "_").replace('.', '')

    # Normalize and remove accents
    column = remove_tildes(column)

    # Convert to lowercase and strip any extra whitespace
    return column.strip().lower()
