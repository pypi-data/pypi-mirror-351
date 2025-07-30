"""The main process function."""

import nltk  # type: ignore
import pandas as pd

from .count_process import count_process
from .embedding_process import embedding_process
from .sentiment_process import sentiment_process
from .stemmer_process import stemmer_process


def process(
    df: pd.DataFrame,
    verbose: bool,
    key_words: set[str],
) -> pd.DataFrame:
    """Process the dataframe for text features."""
    nltk.download("punkt_tab")
    df = embedding_process(df, verbose)
    df = stemmer_process(df, verbose, key_words)
    df = sentiment_process(df, verbose)
    df = count_process(df, verbose)
    return df[sorted(df.columns.values.tolist())]
