"""Calculate sentiment features."""

# pylint: disable=duplicate-code
import statistics

import pandas as pd
import tqdm
from textblob import TextBlob  # type: ignore

from .columns import (DELIMITER, SENTIMENT_COLUMN, SUBJECTIVITY_COLUMN,
                      TEXT_FEATURES_COLUMN)


def sentiment_process(df: pd.DataFrame, verbose: bool) -> pd.DataFrame:
    """Process the sentiment for any text columns."""
    df_dict: dict[str, list[float | None]] = {}
    df_cols = df.select_dtypes(include="object").columns.tolist()

    written_columns = set()
    it = df.itertuples(name=None)
    if verbose:
        it = tqdm.tqdm(it, desc="Sentiment processing", total=len(df))
    for row in it:
        row_dict = {x: row[count + 1] for count, x in enumerate(df_cols)}
        texts = [x for x in row_dict.values() if isinstance(x, str)]
        if not texts:
            continue
        sentiments = []
        subjectivities = []
        for text in texts:
            blob = TextBlob(text)
            sentiments.append(blob.polarity)
            subjectivities.append(blob.subjectivity)
        col = DELIMITER.join([TEXT_FEATURES_COLUMN, SENTIMENT_COLUMN])
        if col not in df_dict:
            df_dict[col] = [None for _ in range(len(df))]
        df_dict[col][row[0]] = statistics.mean(sentiments)
        written_columns.add(col)
        col = DELIMITER.join([TEXT_FEATURES_COLUMN, SUBJECTIVITY_COLUMN])
        if col not in df_dict:
            df_dict[col] = [None for _ in range(len(df))]
        df_dict[col][row[0]] = statistics.mean(subjectivities)
        written_columns.add(col)

    for column in written_columns:
        df[column] = df_dict[column]

    return df[sorted(df.columns.values.tolist())].copy()
