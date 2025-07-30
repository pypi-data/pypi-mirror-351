"""The main process function."""

import pandas as pd

from .embedding_process import embedding_process
from .sentiment_process import sentiment_process
from .stemmer_process import stemmer_process
from .count_process import count_process


def process(
    df: pd.DataFrame,
    verbose: bool,
    key_words: set[str],
) -> pd.DataFrame:
    """Process the dataframe for text features."""
    df = embedding_process(df, verbose)
    df = stemmer_process(df, verbose, key_words)
    df = sentiment_process(df, verbose)
    df = count_process(df, verbose)
    return df[sorted(df.columns.values.tolist())]
