from pymyanlp.lib.mypos.RDRPOSTagger.api import pSCRDRtagger
from importlib.resources import files

NLTK_TAGSET_MAP = {
    "PART": "PRT",
    "V": "VERB",
    "N": "NOUN",
    "punc": ".",
    "sb": ".",
}


model_path = files(__package__).joinpath("models/v3_train1.nopipe.RDR").as_posix()
lexicon_path = files(__package__).joinpath("models/v3_train1.nopipe.DICT").as_posix()


def tag_part_of_speech(input_text: str) -> list[tuple[str, str]]:
    return [
        (word, tag)
        for word, tag in pSCRDRtagger(
            input_text=input_text,
            model_path=model_path,
            lexicon_path=lexicon_path,
        )
    ]


# The only files we really need from here are the model and lexicon.
