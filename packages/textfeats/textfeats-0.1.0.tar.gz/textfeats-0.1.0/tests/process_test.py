"""Tests for the process function."""
import os
import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

from textfeats.process import process


class TestProcess(unittest.TestCase):

    def setUp(self):
        self.dir = os.path.dirname(__file__)

    def test_process(self):
        rows = 100
        df = pd.DataFrame(data={
            "feature1": ["Cool can I have some cheese?", "Where is all the cheese?"],
            "feature2": ["I like goats cheese.", "Cheddar cheese is quite nice."],
        }, index=[x for x in range(2)])
        df = process(df, True, {"cheese"})
        print(df)
        #df.to_parquet("expected.parquet")
        expected_features_df = pd.read_parquet(os.path.join(self.dir, "expected.parquet"))
        assert_frame_equal(df, expected_features_df)
