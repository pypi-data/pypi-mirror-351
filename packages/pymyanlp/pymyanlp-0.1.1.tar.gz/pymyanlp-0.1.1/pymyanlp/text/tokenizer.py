from pymyanlp.text.segment import segment_word
from pymyanlp.text.pos import pos_tag
from pymyanlp.resources.stopword import remove_stop_words

def words_tokenize(text: str):
    return remove_stop_words(pos_tag(segment_word(text)))
