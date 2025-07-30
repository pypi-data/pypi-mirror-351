"""Calculate embedding features."""

# pylint: disable=global-statement,duplicate-code
import hashlib
import os

import numpy as np
import pandas as pd
import tqdm
from sentence_transformers import SentenceTransformer

from .columns import DELIMITER, EMBEDDING_COLUMN, TEXT_FEATURES_COLUMN

_MODEL = None
_MODEL_NAME = "all-mpnet-base-v2"
_CACHE_FOLDER = ".textfeats"
_MODEL_CACHE_FOLDER = os.path.join(_CACHE_FOLDER, _MODEL_NAME)


def _provide_model() -> SentenceTransformer:
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer(_MODEL_NAME)
    return _MODEL


def _produce_embedding(text: str) -> np.ndarray:
    key = hashlib.sha256(text.encode()).hexdigest()
    cache_file = os.path.join(_MODEL_CACHE_FOLDER, key)
    tensor = None
    if os.path.exists(cache_file):
        tensor = np.load(cache_file)
    else:
        model = _provide_model()
        tensor = model.encode(text, show_progress_bar=False)
        np.save(cache_file, tensor)
    if tensor is None:
        raise ValueError("tensor is null")
    return tensor  # type: ignore


def embedding_process(df: pd.DataFrame, verbose: bool) -> pd.DataFrame:
    """Process the embeddings for any text columns."""
    os.makedirs(_MODEL_CACHE_FOLDER, exist_ok=True)
    df_dict: dict[str, list[float | None]] = {}
    df_cols = df.select_dtypes(include="object").columns.tolist()

    written_columns = set()
    it = df.itertuples(name=None)
    if verbose:
        it = tqdm.tqdm(it, desc="Text embedding processing", total=len(df))
    for row in it:
        row_dict = {x: row[count + 1] for count, x in enumerate(df_cols)}
        texts = [x for x in row_dict.values() if isinstance(x, str)]
        if not texts:
            continue
        tensors = np.array([_produce_embedding(x) for x in texts])
        mean_tensor = np.mean(tensors, axis=0).tolist()
        for embedding_dim, value in enumerate(mean_tensor):
            column = DELIMITER.join(
                [TEXT_FEATURES_COLUMN, EMBEDDING_COLUMN, str(embedding_dim)]
            )
            if column not in df_dict:
                df_dict[column] = [None for _ in range(len(df))]
            df_dict[column][row[0]] = value
            written_columns.add(column)

    for column in written_columns:
        df.loc[:, column] = df_dict[column]

    return df[sorted(df.columns.values.tolist())].copy()
