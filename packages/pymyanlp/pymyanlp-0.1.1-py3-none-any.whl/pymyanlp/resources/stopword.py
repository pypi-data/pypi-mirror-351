from pymyanlp.text.pos import PartOfSpeech

STOPWORDS = []

STOPWORD_POS = (
    PartOfSpeech.Pronoun.value,
    PartOfSpeech.Conjunction.value,
    PartOfSpeech.Interjection.value,
    PartOfSpeech.Particle.value,
    PartOfSpeech.PostPositionalMarker.value,
    PartOfSpeech.Symbol.value,
    PartOfSpeech.Punctuation.value,
)


def remove_stop_words(tagged_words: list[tuple[str, str]]):
    """
    Stopwords are removed based on a few conditions: they are removed based
    on the part of speech. Words that belong to the part of speech that do
    not contribute to the sentiment of a sentence, only grammatical and
    contextual meaning. Stopwords that belong to the part of speech that
    is considered potentially useful are removed on word by word basis like in
    English.
    """
    return [
        (word, tag)
        for (word, tag) in tagged_words
        if tag not in STOPWORD_POS and word not in STOPWORDS
    ]
