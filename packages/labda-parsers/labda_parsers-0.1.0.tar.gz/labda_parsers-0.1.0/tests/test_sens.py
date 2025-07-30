"""Test Sens parser loading."""

from pathlib import Path

import pandas as pd

from labda_parsers import Sens

DATA_DIR = Path(__file__).parent.parent / 'data'


def test_sens_loads():
    """Test that Sens parser can load the test file."""
    parser = Sens()
    df = parser.from_file(DATA_DIR / 'sens.bin')
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
