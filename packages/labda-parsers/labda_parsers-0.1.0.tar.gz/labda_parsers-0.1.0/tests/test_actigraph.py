"""Test Actigraph parser loading."""

from pathlib import Path

import pandas as pd

from labda_parsers import Actigraph

DATA_DIR = Path(__file__).parent.parent / 'data'


def test_actigraph_loads():
    """Test that Actigraph parser can load the test file."""
    parser = Actigraph()
    df = parser.from_file(DATA_DIR / 'actigraph.gt3x')
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
