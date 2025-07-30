# text-features

<a href="https://pypi.org/project/textfeats/">
    <img alt="PyPi" src="https://img.shields.io/pypi/v/textfeats">
</a>

A library for processing text features in a dataframe.

## Dependencies :globe_with_meridians:

Python 3.11.6:

- [pandas](https://pandas.pydata.org/)
- [pyarrow](https://arrow.apache.org/docs/python/index.html)
- [sentence_transformers](https://sbert.net/)
- [tqdm](https://github.com/tqdm/tqdm)
- [nltk](https://www.nltk.org/)
- [textblob](https://textblob.readthedocs.io/en/dev/)
- [numpy](https://numpy.org/)

## Raison D'être :thought_balloon:

`textfeats` transforms text into values that can be used by a model.

## Architecture :triangular_ruler:

`textfeats` is a functional library, meaning that each phase of feature extraction gets put through a different function until the final output. The features its computes are as follows:

1. Embeddings - A mean of all the embeddings from the text values in the row.
2. Stemmer - A count of the keywords containing the stem from the text values in the row.
3. Sentiment - A measure of the positive / negative sentiment from the text values in the row.
4. Objectivity - A measure of the objectivity / subjectivity from the text values in the row.

## Installation :inbox_tray:

This is a python package hosted on pypi, so to install simply run the following command:

`pip install textfeats`

or install using this local repository:

`python setup.py install --old-and-unmanageable`

## Usage example :eyes:

The use of `textfeatures` is entirely through code due to it being a library. It attempts to hide most of its complexity from the user, so it only has a few functions of relevance in its outward API.

### Generating Features

To generate features:

```python
import datetime

import pandas as pd

from textfeats.process import process

df = ... # Your timeseries dataframe
df = process(df, True, {"injuries"})
```

This will produce a dataframe that contains the new text related features.

## License :memo:

The project is available under the [MIT License](LICENSE).
