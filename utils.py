import unicodedata
import re


def remove_tildes(text):
    """Removes the accents of each vowel in a text

    :param str text: the text with vowels with accents
    :return str: the text without the accents
    """
    # Normalize and remove accents
    text = ''.join(
        char for char in unicodedata.normalize('NFD', text)
        if unicodedata.category(char) != 'Mn'
    )
    return text.strip()


def clean_name(name):
    """Cleans a name by removing numbers and accents.

    :param str name: The name to be cleaned.
    :return str: The cleaned name.
    """
    # Remove numbers using regex
    name = re.sub(r'\d+', '', name)

    # Remove tildes (accents) from vowels
    name = remove_tildes(name)

    # Return the cleaned name
    return name.strip()


def clean_column_name(column):
    """Cleans the column name by:
    - Replacing spaces with underscores.
    - Removing accents from vowels.

    :param str column: The original column name.

    :return str: The cleaned column name.
    """
    # Replace spaces with underscores
    column = column.replace(" ", "_")

    # Normalize and remove accents
    column = remove_tildes(column)

    # Convert to lowercase and strip any extra whitespace
    return column.strip().lower()