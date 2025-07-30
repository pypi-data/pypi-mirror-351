import math
import functools
import sys
import pickle
import numpy as np
from typing import Dict, List, Tuple, Callable, Optional, Any
from importlib.resources import files

# Setting recursion limit for recursive viterbi implementation
# Note: This is a workaround and should ideally be replaced with an iterative approach
sys.setrecursionlimit(10**6)


def read_dict(filepath: str) -> Dict[str, int]:
    """
    Load a dictionary from a pickle file.

    Args:
        filepath: Path to the pickle file containing the dictionary.

    Returns:
        Dictionary mapping words/phrases to their counts.

    Raises:
        FileNotFoundError: If the dictionary file is not found.
        Exception: For other errors during file reading.
    """
    try:
        with open(filepath, "rb") as input_file:
            dictionary = pickle.load(input_file)
            return dictionary
    except FileNotFoundError:
        raise FileNotFoundError(f"Dictionary file {filepath} not found!")
    except Exception as e:
        raise Exception(f"Error reading dictionary file {filepath}: {str(e)}")


class ProbDist(dict):
    """
    Probability distribution class for word/phrase frequencies.
    Extends dict to store word counts and calculate probabilities.
    """

    def __init__(
        self, datafile: Optional[str] = None, unigram: bool = True, N: int = 102490
    ):
        """
        Initialize probability distribution from a data file.

        Args:
            datafile: Path to pickle file containing word counts.
            unigram: If True, use unigram-specific unknown word probability.
            N: Total count/corpus size (normalization factor).
        """
        super().__init__()
        self.N = N

        if datafile:
            data = read_dict(datafile)
            for k, c in data.items():
                self[k] = self.get(k, 0) + c

        # Set unknown word probability function based on distribution type
        if unigram:
            # Penalize longer unknown words more heavily
            self.unknownprob: Callable[[str, int], float] = lambda k, N: 10 / (
                N * 10 ** len(k)
            )
        else:
            # Uniform probability for unknown words
            self.unknownprob: Callable[[str, int], float] = lambda k, N: 1 / N

    def __call__(self, key: str) -> float:
        """
        Get probability of a word/phrase.

        Args:
            key: The word or phrase to get probability for.

        Returns:
            Probability of the word/phrase.
        """
        if key in self:
            return self[key] / self.N
        else:
            return self.unknownprob(key, self.N)


def conditional_prob(
    P_bigram: ProbDist, P_unigram: ProbDist, word_curr: str, word_prev: str
) -> float:
    """
    Calculate conditional probability of current word given the previous word.

    Args:
        P_bigram: Bigram probability distribution.
        P_unigram: Unigram probability distribution.
        word_curr: Current word.
        word_prev: Previous word.

    Returns:
        P(word_curr | word_prev): Conditional probability.
    """
    try:
        bigram_key = f"{word_prev} {word_curr}"
        return P_bigram[bigram_key] / P_unigram[word_prev]
    except KeyError:
        # Backoff to unigram probability if bigram not found
        return P_unigram(word_curr)


class WordSegmenter:
    """
    Class for word segmentation using Viterbi algorithm.

    This approach encapsulates the probability distributions and provides
    both iterative and recursive implementations of the Viterbi algorithm.
    """

    def __init__(
        self, P_unigram: ProbDist, P_bigram: ProbDist, max_word_length: int = 20
    ):
        """
        Initialize word segmenter with probability distributions.

        Args:
            P_unigram: Unigram probability distribution.
            P_bigram: Bigram probability distribution.
            max_word_length: Maximum length of any word to consider.
        """
        self.P_unigram = P_unigram
        self.P_bigram = P_bigram
        self.max_word_length = max_word_length

    def segment_iterative(self, text: str) -> List[str]:
        """
        Segment text using an iterative Viterbi algorithm implementation.

        Args:
            text: Input text to segment.

        Returns:
            List of segmented words.
        """
        if not text:
            return []

        n = len(text)

        # Initialize arrays for dynamic programming
        # best_log_prob[i] = best log probability for text[0:i]
        best_log_prob = np.full(n + 1, -np.inf)
        best_log_prob[0] = 0.0

        # best_word_end[i] = end position of best last word for text[0:i]
        best_word_end = np.zeros(n + 1, dtype=int)

        # previous_word[i] = word ending at position i
        previous_word = [""] * (n + 1)

        # Fill the DP tables
        for i in range(1, n + 1):
            # Consider all possible word lengths
            max_j = max(0, i - self.max_word_length)
            for j in range(i - 1, max_j - 1, -1):
                word = text[j:i]

                # Get conditional probability given the previous word
                prev = previous_word[j] if j > 0 else "<S>"
                word_log_prob = math.log10(
                    conditional_prob(self.P_bigram, self.P_unigram, word, prev)
                )

                # Update if we found a better probability
                if best_log_prob[j] + word_log_prob > best_log_prob[i]:
                    best_log_prob[i] = best_log_prob[j] + word_log_prob
                    best_word_end[i] = j
                    previous_word[i] = word

        # Reconstruct the best path
        segmented_words = []
        i = n
        while i > 0:
            j = best_word_end[i]
            segmented_words.append(text[j:i])
            i = j

        # Reverse to get words in correct order
        return segmented_words[::-1]

    def segment(self, text: str) -> List[str]:
        """
        Segment text into words using the Viterbi algorithm.

        Args:
            text: Input text to segment.

        Returns:
            List of segmented words.
        """
        return self.segment_iterative(text)


P_bigram = ProbDist(
    datafile=files(__package__).joinpath("models/bigram-word.bin").as_posix(),
    unigram=False,
)
P_unigram = ProbDist(
    datafile=files(__package__).joinpath("models/unigram-word.bin").as_posix(),
    unigram=True,
)


def segment_text(text: str, max_word_length: int = 20) -> List[str]:
    """
    Segment text into words using the Viterbi algorithm.

    This function provides backwards compatibility with the original API.
    For new code, consider using the WordSegmenter class directly.

    Args:
        text: Input text to segment.
        P_bigram: Bigram probability distribution.
        P_unigram: Unigram probability distribution.
        use_iterative: Whether to use the iterative version (recommended for longer texts).
        max_word_length: Maximum word length to consider.

    Returns:
        List of segmented words.
    """
    segmenter = WordSegmenter(P_unigram, P_bigram, max_word_length)
    return segmenter.segment(text)
