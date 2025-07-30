"""Axivity .cwa file parser for accelerometer data.

This module provides functionality to parse Axivity .cwa files containing accelerometer
data and convert them to standardized pandas DataFrames. Supports optional timezone
localization and includes temperature data when available in the source files.
"""

from dataclasses import dataclass
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from skdh.io import ReadCwa

from .parser import FileParser


@dataclass
class Axivity(FileParser):
    """Parser for Axivity accelerometer .cwa files.

    This parser reads Axivity .cwa files containing accelerometer data and converts
    them to pandas DataFrames. It supports optional timezone localization and includes
    temperature data when available in the file.

    Notes:
        - Data are stored in local time by default.
        If a timezone is specified, the datetime index will be localized to that timezone.

    Attributes:
        timezone (ZoneInfo | None): Timezone to localize the datetime index to.
            If None, datetime will be timezone-naive. If specified, the index
            will be localized to the given timezone.

    Examples:
        Basic usage:

        >>> from labda_parsers import Axivity
        >>> parser = Axivity(timezone="Europe/Copenhagen")
        >>> df = parser.from_file(Path("data/sample.cwa"))
    """

    timezone: ZoneInfo | None = None

    def from_file(
        self,
        path: Path | str,
    ) -> pd.DataFrame:
        """Parse an Axivity .cwa file and return accelerometer data as a DataFrame.

        The data includes x, y, z acceleration components and optionally temperature
        readings. The datetime index is properly formatted and can be localized to
        a specified timezone.

        Args:
            path (Path | str): Path to the .cwa file to parse.

        Returns:
            pd.DataFrame: DataFrame containing accelerometer data with columns:
                - acc_x (float32): X-axis acceleration
                - acc_y (float32): Y-axis acceleration
                - acc_z (float32): Z-axis acceleration
                - temperature (float32, optional): Temperature readings if available
                Index is datetime with name 'datetime'. If no timezone is specified,
                the index will be timezone-naive, otherwise it will be localized
                to the specified timezone.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            ValueError: If the file is not a .cwa file or contains no data.

        Examples:
            >>> from labda_parsers import Axivity
            >>> parser = Axivity(timezone="Europe/Copenhagen")
            >>> df = parser.from_file(Path("data/sample.cwa"))
        """
        if isinstance(path, str):
            path = Path(path)

        self.check_file(path, '.cwa')

        cwa = ReadCwa().predict(file=path, tz_name=self.timezone)
        df = pd.DataFrame(
            cwa['accel'].astype(np.float32),
            columns=['acc_x', 'acc_y', 'acc_z'],
            index=cwa['time'],
        )

        temperature = cwa.get('temperature')
        if temperature is not None:
            df['temperature'] = temperature.astype(np.float32)

        del cwa

        df.index.name = 'datetime'
        if self.timezone:
            df.index = pd.to_datetime(df.index, utc=True, unit='s')
            df.index = df.index.tz_convert(self.timezone)
        else:
            df.index = pd.to_datetime(df.index, unit='s')

        self.check_empty(df)

        return df
