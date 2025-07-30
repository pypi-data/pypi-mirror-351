"""Calculate stemmer features."""

# pylint: disable=duplicate-code
import pandas as pd
import tqdm
from nltk.stem import PorterStemmer  # type: ignore
from nltk.tokenize import word_tokenize  # type: ignore

from .columns import DELIMITER, KEY_WORD_COLUMN, TEXT_FEATURES_COLUMN

_STEMMER = PorterStemmer()


def _count_key_word(text: str, key_word: str) -> int:
    words = word_tokenize(text)
    stems = [_STEMMER.stem(x) for x in words]
    return stems.count(key_word)


def stemmer_process(
    df: pd.DataFrame, verbose: bool, key_words: set[str]
) -> pd.DataFrame:
    """Process the stems for any text columns."""
    key_words = {_STEMMER.stem(x) for x in key_words}
    df_dict: dict[str, list[float | None]] = {}
    df_cols = df.select_dtypes(include="object").columns.tolist()

    written_columns = set()
    it = df.itertuples(name=None)
    if verbose:
        it = tqdm.tqdm(it, desc="Stemmer processing", total=len(df))
    for row in it:
        row_dict = {x: row[count + 1] for count, x in enumerate(df_cols)}
        texts = [x for x in row_dict.values() if isinstance(x, str)]
        if not texts:
            continue
        for key_word in key_words:
            key_word_count = 0
            for text in texts:
                key_word_count += _count_key_word(text, key_word)
            column = DELIMITER.join([TEXT_FEATURES_COLUMN, KEY_WORD_COLUMN, key_word])
            if column not in df_dict:
                df_dict[column] = [None for _ in range(len(df))]
            df_dict[column][row[0]] = float(key_word_count)
            written_columns.add(column)

    for column in written_columns:
        df[column] = df_dict[column]

    return df[sorted(df.columns.values.tolist())].copy()
