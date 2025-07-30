from pymyanlp.preprocessor.segment import segment_word
from pymyanlp.preprocessor.pos import pos_tag
from pymyanlp.preprocessor.stopword import remove_stop_words

def words_tokenize(text: str):
    return remove_stop_words(pos_tag(segment_word(text)))
