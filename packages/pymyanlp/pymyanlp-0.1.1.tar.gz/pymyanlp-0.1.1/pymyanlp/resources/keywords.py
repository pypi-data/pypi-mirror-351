import numpy as np

# from sklearn.feature_extraction.text import TfidfVectorizer
from pymyanlp.text.script import apply_written_suite
from pymyanlp.text.tokenizer import words_tokenize


def extract_keywords_tfidf(
    corpus: list[str],
    tokenizer=words_tokenize,
    preprocessor=apply_written_suite,
):
    """
    corpus: list[str] - the corpus to extract keywords from
    tokenizer: function - to perform word segmentation
    preprocessor: function - to preprocess text before word segmentation
    """
    vectorizer = TfidfVectorizer(
        tokenizer=tokenizer,
        encoding="utf-8",
        lowercase=True,
        stop_words=[],  # stop words have already been removed
        preprocessor=preprocessor,
    )

    tfidf_matrix = vectorizer.fit_transform(corpus)
    feature_names = vectorizer.get_feature_names_out()
    total_scores = np.sum(tfidf_matrix, axis=0)  # type: ignore

    # Convert the total scores to a 1D array
    total_scores = np.squeeze(np.asarray(total_scores))

    # Create a dictionary to store word-total_score pairs
    word_total_scores = dict(zip(feature_names, total_scores))

    cleaned_word_scores = {}
    # penalize and clean data
    for word, score in word_total_scores.items():
        cleaned_word_scores[word.strip()] = penalize(word.strip(), score)

    # Sort the dictionary by total scores in descending order
    sorted_word_total_scores = sorted(
        cleaned_word_scores.items(), key=lambda x: x[1], reverse=True
    )

    return sorted_word_total_scores


def penalize(word: str, score: float):
    """
    Penalize words based on validity.
    """
    if not word:
        score = 0

    return score
