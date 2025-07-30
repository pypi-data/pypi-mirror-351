from functools import wraps
from pymyanlp.lib.mypos import tag_part_of_speech as _inner
from enum import Enum

class PartOfSpeech(Enum):
    """
    Ease of use part of speech enum.
    I recommend using the value of the enums over the enum objects when
    possible, this helps in serialization data.
    """

    # အထက(Basic Education High School), လ.ဝ (Confidentiality)
    Abbreviation = "abb"
    # ရဲရင့် (brave), လှပ (beautiful), မွန်မြတ် (noble)
    Adjective = "adj"
    # ဖြေးဖြေး (slow), နည်းနည်း (less)
    Adverb = "adv"
    # နှင့် (and), ထို့ကြောင့် (therefore), သို့မဟုတ် (or)
    Conjunction = "conj"
    ForeignWord = "fw"
    # အမလေး (Oh My God!)
    Interjection = "int"
    Noun = "n"
    Number = "num"
    # များ (used to form the plural nouns as "-s" , "-es"), ခဲ့ (the past tense "-ed"), သင့် (modal verb "shall"), လိမ့် (modal verb "will"), နိုင် (modal verb "can")
    Particle = "part"
    # သည်, က, ကို, အား, သို့, မှာ, တွင် (at, on ,in, to)
    PostPositionalMarker = "ppm"
    Pronoun = "pron"
    Punctuation = "punc"
    Symbol = "sb"
    TextNumber = "tn"
    Verb = "v"

    @staticmethod
    def from_notation(value: str):
        return PartOfSpeech._value2member_map_[value]


@wraps(_inner)
def pos_tag(*args, **kwargs):
    """Part-of-speech tagging."""
    return [(word, PartOfSpeech.from_notation(tag)) for word, tag in _inner(*args, **kwargs)]

