import pandas as pd

from typing import Callable
from enum import Enum, auto
from pymyanlp.text.tokenizer import words_tokenize
from pymyanlp.text.script import apply_written_suite
from dataclasses import dataclass


class Polarity(Enum):
    POSITIVE = auto()
    NEGATIVE = auto()
    NEUTRAL = auto()


TokenType = tuple[str, str]


@dataclass
class SentimentAnalysisResult:
    polarity: Polarity
    tokens: list[TokenType]


class ScoreBasedSentimentAnalyzer:
    def __init__(
        self,
        tokenizer=words_tokenize,
        preprocessor=apply_written_suite,
        sentiment_lexicon_path="./data/sentiment_lexicon.csv",
        profanity_path="./data/profanity.csv",
        progress_updater: Callable = None,  # type: ignore
    ) -> None:
        self.tokenizer = tokenizer
        self.preprocessor = preprocessor
        self.sentiment_lexicon = pd.read_csv(sentiment_lexicon_path, header=0)
        self.profanity = pd.read_csv(profanity_path, header=0)
        self._progress_updater = progress_updater

    def progress_updater(self, value):
        if self._progress_updater:
            self._progress_updater(value)

    def resolve_sentiment_name(self, sentiment_name: str):
        pass
        # match sentiment_name:
        #     case "pos" | "positive":
        #         return 1
        #     case "neg" | "negative":
        #         return -1
        #     case "neu" | "neutral":
        #         return 0
        #     case _ as undefined:
        #         raise Exception(f"Unsupported sentiment class '{undefined}'")

    def analyze(self, text: str) -> SentimentAnalysisResult:
        if self.preprocessor:
            text = self.preprocessor(text)

        self.progress_updater(25)
        tokens = self.tokenizer(text)

        self.progress_updater(50)

        sentiments = []
        for t in tokens:
            if t[0] in self.profanity:
                sentiments.append((t, "negative"))

            matches = self.sentiment_lexicon.loc[
                self.sentiment_lexicon["word"] == t[0], "sentiment"
            ].values

            if matches:
                sentiments.append(self.resolve_sentiment_name(matches[0]))
        self.progress_updater(100)

        p_e = ""
        p_t = sum(sentiments)
        p_r = p_t / len(sentiments)

        if p_r >= 0.3:
            polarity = Polarity.POSITIVE
        elif p_r <= -0.3:
            polarity = Polarity.NEGATIVE
        else:
            polarity = Polarity.NEUTRAL

        return SentimentAnalysisResult(polarity, tokens)
