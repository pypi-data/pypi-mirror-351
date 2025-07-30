"""Calculate count features."""

import pandas as pd
import tqdm
from nltk.tokenize import word_tokenize  # type: ignore

from .columns import COUNT_COLUMN, DELIMITER, TEXT_FEATURES_COLUMN


def count_process(df: pd.DataFrame, verbose: bool) -> pd.DataFrame:
    """Process the count for any text columns."""
    df_dict: dict[str, list[float | None]] = {}
    df_cols = df.select_dtypes(include="object").columns.tolist()

    written_columns = set()
    it = df.itertuples(name=None)
    if verbose:
        it = tqdm.tqdm(it, desc="Count processing", total=len(df))
    for row in it:
        row_dict = {x: row[count + 1] for count, x in enumerate(df_cols)}
        texts = [x for x in row_dict.values() if isinstance(x, str)]
        if not texts:
            continue
        word_count = sum(len(word_tokenize(x)) for x in texts)
        col = DELIMITER.join([TEXT_FEATURES_COLUMN, COUNT_COLUMN])
        if col not in df_dict:
            df_dict[col] = [None for _ in range(len(df))]
        df_dict[col][row[0]] = float(word_count)
        written_columns.add(col)

    for column in written_columns:
        df.loc[:, column] = df_dict[column]

    return df[sorted(df.columns.values.tolist())].copy()
