import re

from string import printable, punctuation

NUMBER_MAP = dict(zip("0123456789", "၀၁၂၃၄၅၆၇၈၉"))
PUNCTUATION = ["။", "၊", *punctuation]

is_english = lambda c: c in printable
myanmar_alphabet = "ကခဂဃငစဆဇဈညဋဌဍဎဏတထဒဓနဖဗဘမယရလ၀ဟဠအ"

def contains_burmese(text: str):
    return any(a in text for a in myanmar_alphabet)


def apply_written_suite(text: str):
    """
    Apply the suite of tools.
    """
    return clear_spacing(transliterate_numbers(remove_punctuation(text)))


def transliterate_numbers(text: str):
    """
    Transliterate English numbers into burmese.
    """
    return "".join(NUMBER_MAP.get(c, c) for c in text)


def clear_spacing(text: str):
    """
    Removes all spacing except those between foreign words and burmese words.
    """
    is_english = lambda c: c in printable

    text = text.replace(" ", "")

    # add spaces back to english characters
    new_str = ""
    last_eng = False
    for c in text:
        if is_english(c) and not last_eng or not is_english(c) and last_eng:
            new_str += " " + c
        else:
            new_str += c
        last_eng = is_english(c)

    return new_str


@staticmethod
def remove_punctuation(text: str):
    return "".join(c for c in text if c not in PUNCTUATION)


symbolic_words = {"$": "အ", "အဇမ်း": "အရမ်း"}


@staticmethod
def normalize(text: str, shorten_visarga=True, convert_slangs=True):
    """
    Normalize informal patterns of burmese tools into written burmese style,
    making it more processible.

    1. shorten repeated visarga (vowel extender):  အရမ်းးးးးးး -> အရမ်း
    2. convert informal slangs to colloquial form
    """
    if shorten_visarga:
        text = re.sub(r"း+", "း", text)

    if convert_slangs:
        for w, sub in symbolic_words:
            if w in text:
                text = text.replace(w, sub)
