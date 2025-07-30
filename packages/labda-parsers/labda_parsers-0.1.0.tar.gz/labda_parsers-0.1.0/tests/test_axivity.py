"""Test Axivity parser loading."""

from pathlib import Path

import pandas as pd

from labda_parsers import Axivity

DATA_DIR = Path(__file__).parent.parent / 'data'


def test_axivity_loads():
    """Test that Axivity parser can load the test file."""
    parser = Axivity()
    df = parser.from_file(DATA_DIR / 'axivity.cwa')
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
