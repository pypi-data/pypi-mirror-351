import csv
import os
import secrets

SUPPORTED_LANGUAGES = ["en", "de"]


def dice(n: int = 1) -> str:
    """
    Simulate the rolling of one or multiple six-faced dice.

    :param n: the number of dice to simulate. Must be greater than or equal to 1.
    :return: a sequence of ``n`` random numbers between 1 and 6.
    :raises TypeError: if ``n`` is not an integer.
    :raises ValueError: if ``n`` is less than 1.
    """

    if not isinstance(n, int):
        raise TypeError(f"Parameter n must be an integer, but is {type(n)}.")

    if n < 1:
        raise ValueError(f"Parameter n must be greater than or equal to 1, but is {n}.")

    # String representing the sequence of dice results.
    dice_results = ""

    # Roll the dice ``n`` times.
    for _ in range(n):
        dice_results += secrets.choice(["1", "2", "3", "4", "5", "6"])

    return dice_results


def wordlist(language: str = "en") -> dict:
    """
    Read text files containing a Diceware word list and return a dictionary of those words.\n
    Currently supported languages: ``en`` and ``de``.\n
    ``en``: https://www.eff.org/document/passphrase-wordlists\n
    ``de``: https://github.com/dys2p/wordlists-de

    :param language: the language assigned to a specific inbuilt word list.
    :return: a Diceware wordlist as dictionary.
    :raises ValueError: if the specified language is not supported.
    """

    if not isinstance(language, str):
        raise TypeError(
            f"Parameter language must be a string, but is {type(language)}."
        )

    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Language {language} not supported. Supported languages: {', '.join(SUPPORTED_LANGUAGES)}."
        )

    # Path to the word list text files.
    file_path = (
        os.path.abspath(os.path.join(os.path.dirname(__file__), "wordlists")) + "/"
    )

    # Append the file name for the corresponding word list to the file path.
    match language:
        case "en":
            file_path += "eff_large_wordlist.txt"
        case "de":
            file_path += "de-7776-v1-diceware.txt"

    # Dictionary representing the selected Diceware wordlist.
    ret_wordlist = dict([])

    # Open the word list and index each word by its ID.
    with open(file_path, "r") as file:
        reader = csv.DictReader(file, fieldnames=["id", "word"], delimiter="\t")
        for row in reader:
            ret_wordlist[row["id"]] = row["word"]

    return ret_wordlist


def diceware(n: int = 6, language: str = "en") -> list:
    """
    Function implementing the Diceware method for passphrase generation.\n
    For each word in the passphrase, five rolls of a six-faced dice are required.
    The numbers from 1 to 6 that come up in the rolls are assembled as a five-digit number.
    That number is then used to look up a word in a cryptographic word list.\n
    A minimum of 6 words is recommended for passphrases.

    :param n: the desired number of words to generate. Must be greater than or equal to 1.
    :param language: the language assigned to a specific inbuilt word list. Currently supported languages: ``en`` and ``de``.
    :return: a list of ``n`` randomly selected words from a Diceware word list.
    :raises TypeError: if ``n`` is not an integer or if ``language`` is not a string.
    :raises ValueError: if ``n`` is less than 1 or if the specified language is not supported.
    """

    if not isinstance(n, int):
        raise TypeError(f"Parameter n must be an integer, but is {type(n)}.")

    if n < 1:
        raise ValueError(f"Parameter n must be greater than or equal to 1, but is {n}.")

    if not isinstance(language, str):
        raise TypeError(
            f"Parameter language must be a string, but is {type(language)}."
        )

    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Language {language} not supported. Supported languages: {', '.join(SUPPORTED_LANGUAGES)}."
        )

    # Retrieve the Diceware word list corresponding to the specified language.
    diceware_wordlist = wordlist(language=language)

    # List of randomly selected words.
    words = []

    # Generate ``n`` words.
    for _ in range(n):
        dice_results = dice(n=5)
        words.append(diceware_wordlist[dice_results])

    return words


if __name__ == "__main__":
    pass
