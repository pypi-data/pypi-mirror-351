import re
from typing import Literal
from string import printable, punctuation

BURMESE_NUMBERS = "၀၁၂၃၄၅၆၇၈၉"
NUMBER_MAP = dict(zip("0123456789", BURMESE_NUMBERS))
PUNCTUATION = ["။", "၊", *punctuation]

is_english = lambda c: c in printable
BURMESE_ALPHABET = "ကခဂဃငစဆဇဈညဋဌဍဎဏတထဒဓနဖဗဘမယရလ၀ဟဠအ"


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


def remove_punctuation(text: str):
    return "".join(c for c in text if c not in PUNCTUATION)


symbolic_words = {"$": "အ", "အဇမ်း": "အရမ်း"}


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


def is_burmese(text: str, allow_space=True):
    """
    Check if all of the characters in the text belongs to the Myanmar Unicode block (U+1000-U+109F) or a space character.

    Args:
        text (str): A string to check

    Returns:
        bool: True if the character is in the Myanmar Unicode block, False otherwise
    """
    if not isinstance(text, str) or len(text) < 1:
        return False

    return all(
        0x1000 <= ord(char) <= 0x109F or (char == " " and allow_space) for char in text
    )


def contains_burmese(text: str):
    return any(is_burmese(a, allow_space=False) for a in text)


def get_burmese_script(text: str):
    """
    Determine the specific script variant for a Myanmar text. Texts which
    may belong to different script variants, but does not contain any
    recoginized characters from the extensions will be considered as
    "burmese" by default. Note that this makes it impossible to detect
    most pali texts.

    Args:
        text (str): The Myanmar text

    Returns:
        str: The script name or "unknown" if not in Myanmar block or unrecognized
    """
    if not is_burmese(text):
        return "unknown"

    for char in text:
        code_point = ord(char)
        # Pali and Sanskrit extensions
        if 0x1050 <= code_point <= 0x1059:
            return "pali_sanskrit"

        # Mon extensions
        elif code_point in [0x105A, 0x105B, 0x105C, 0x105D, 0x105E, 0x105F, 0x1060]:
            return "mon"

        # S'gaw Karen extensions
        elif code_point in [0x1061, 0x1062, 0x1063, 0x1064]:
            return "sgaw_karen"

        # Western Pwo Karen extensions
        elif 0x1065 <= code_point <= 0x106D:
            return "western_pwo_karen"

        # Eastern Pwo Karen extensions
        elif code_point in [0x106E, 0x106F, 0x1070]:
            return "eastern_pwo_karen"

        # Geba Karen extension
        elif code_point == 0x1071:
            return "geba_karen"

        # Kayah extensions
        elif 0x1072 <= code_point <= 0x1074:
            return "kayah"

        # Shan extensions (including letters, signs, and digits)
        elif 0x1075 <= code_point <= 0x1099:
            return "shan"

        # Khamti Shan extensions
        elif code_point in [0x109A, 0x109B]:
            return "khamti_shan"

        # Aiton and Phake extensions
        elif code_point in [0x109C, 0x109D]:
            return "aiton_phake"

        # Shan symbols
        elif code_point in [0x109E, 0x109F]:
            return "shan"

    return "burmese"


def fix_medial(text, position: Literal["before", "after"] = "before"):
    """
    Rearrange Myanmar text by moving dependent consonant medial signs (ya, ra, ကျ, ကြ) before or after their base characters.

    In Myanmar script, medial consonant signs (like ya and ra) typically follow their base
    consonants in Unicode representation, but sometimes this is skewed and needs to be
    fixed for proper rendering.

    This function identifies and reorders these signs to match the correct visual order.

    Args:
        text (str): Myanmar text to rearrange
        position (Literal["before", "after"]): Whether to place dependent signs before or after base characters.
            Defaults to "before" for proper visual rendering.

    Returns:
        str: Text with medial consonant signs moved to the specified position relative to base characters

    Example:
        >>> fix_medial("ကျ")
        >>> "ျက"
        >>> fix_medial("ကျ", position="after")
        >>> "ကျ"
    """
    if not text:
        return text

    dependent_consonant_signs = {
        0x1031,  # MYANMAR VOWEL SIGN E
        0x103B,  # MYANMAR CONSONANT SIGN MEDIAL YA
        0x103C,  # MYANMAR CONSONANT SIGN MEDIAL RA
    }

    result = []
    i = 0

    while i < len(text):
        current_char = text[i]
        current_code = ord(current_char)

        if is_burmese(current_char) and current_code not in dependent_consonant_signs:
            dependent_chars = []
            j = i + 1

            while j < len(text):
                next_char = text[j]
                next_code = ord(next_char)

                if is_burmese(next_char) and next_code in dependent_consonant_signs:
                    dependent_chars.append(next_char)
                    j += 1
                else:
                    break

            if position == "before":
                # Add dependent symbols first, then base character
                result.extend(dependent_chars)
                result.append(current_char)
            else:  # position == "after"
                # Add base character first, then dependent symbols
                result.append(current_char)
                result.extend(dependent_chars)

            # Move index past the processed characters
            i = j
        else:
            # For non-base characters or characters already in correct position
            result.append(current_char)
            i += 1

    return "".join(result)
