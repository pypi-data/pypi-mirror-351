from enum import Enum


class BurmeseForm(Enum):
    Old = "OB"  # written - 11th-13th century inscriptions
    Modern = "MB"  # spoken - contemporary burmese
    Written = "WB"  # written - the orthographical form of modern burmese
    Formal = "FB"  # written - using traditional elements with the modern form
    Informal = "FB"  # written - contains slangs, fashionable features


def identify_style(text: str) -> BurmeseForm:
    return BurmeseForm.Modern
