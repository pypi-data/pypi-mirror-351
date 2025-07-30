"""ActiGraph GT3X file parser for accelerometer data.

This module provides functionality to parse ActiGraph GT3X files and convert them
to standardized pandas DataFrames with consistent column naming and datetime indexing.
Supports automatic timezone handling and configurable idle sleep period management.
"""

import io
from contextlib import redirect_stdout
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import pandas as pd
from pygt3x.reader import FileReader

from .parser import FileParser


@dataclass
class Actigraph(FileParser):
    """Parser for ActiGraph GT3X accelerometer files.

    This parser reads ActiGraph GT3X files containing accelerometer data and converts
    them to pandas DataFrames. It handles timezone localization automatically and
    provides options for managing idle sleep periods in the data.

    Attributes:
        idle_sleep (Literal["ffill", "zero"]): How to handle idle sleep mode.
            "ffill" will forward fill the last valid value during idle periods.
            "zero" will set the accelerometer values to 0 during idle sleep periods.
            Defaults to "ffill".

    Examples:
        >>> from labda_parsers import Actigraph
        >>> parser = Actigraph(idle_sleep="zero")
        >>> df = parser.from_file("data/actigraph_data.gt3x")
    """

    idle_sleep: Literal['ffill', 'zero'] = 'ffill'

    def __post_init__(self):
        """Validate the idle_sleep attribute after object initialization.

        This method ensures that the idle_sleep parameter is set to one of the
        valid options. It's called automatically during object creation when
        using the dataclass decorator.

        Raises:
            ValueError: If idle_sleep is not 'ffill' or 'zero'.

        Examples:
            >>> from labda_parsers import Actigraph
            >>> parser = Actigraph(idle_sleep="zero")
        """
        if self.idle_sleep not in {'ffill', 'zero'}:
            raise ValueError(f"Invalid idle_sleep value: {self.idle_sleep}. Expected 'ffill' or 'zero'.")

    def from_file(
        self,
        path: Path | str,
    ) -> pd.DataFrame:
        """Load and process ActiGraph GT3X accelerometer data from a file.

        Reads ActiGraph GT3X files and converts them to a standardized pandas DataFrame
        format with consistent column names and proper datetime indexing. Handles timezone
        localization automatically and processes idle sleep periods according to the
        configured strategy.

        Args:
            path (Path | str): Path to the GT3X file to be processed.

        Returns:
            pd.DataFrame: Processed accelerometer data with columns:
                - acc_x (float32): X-axis acceleration values
                - acc_y (float32): Y-axis acceleration values
                - acc_z (float32): Z-axis acceleration values
                Index is datetime with timezone information if available in the file.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            ValueError: If the file is not a valid GT3X file or is empty.

        Examples:
            >>> from labda_parsers import Actigraph
            >>> parser = Actigraph(idle_sleep="zero")
            >>> df = parser.from_file("data/sample.gt3x")
        """
        if isinstance(path, str):
            path = Path(path)

        self.check_file(path, '.gt3x')

        with (
            FileReader(path) as reader,
            redirect_stdout(io.StringIO()),
        ):
            df = reader.to_pandas()
            timezone = reader.info.timezone

        self.check_empty(df)

        df.rename(
            columns={'X': 'acc_x', 'Y': 'acc_y', 'Z': 'acc_z', 'IdleSleepMode': 'idle'},
            inplace=True,
        )
        df.index.name = 'datetime'
        df.index = pd.to_datetime(df.index, unit='s')

        if timezone:
            df.index = df.index.tz_localize(timezone)

        if self.idle_sleep == 'zero':
            df.loc[df['idle'], ['acc_x', 'acc_y', 'acc_z']] = 0

        df.drop(columns='idle', inplace=True)

        return df
