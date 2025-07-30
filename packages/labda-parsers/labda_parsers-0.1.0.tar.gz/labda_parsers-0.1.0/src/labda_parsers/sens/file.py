"""Sens binary file parser for accelerometer data.

This module provides functionality to parse Sens binary files containing accelerometer
data and convert them to standardized pandas DataFrames. Supports reading from both
files and in-memory buffers with configurable normalization.

Constants:
    SENS_NORMALIZATION_FACTOR (float): Factor used to normalize raw sensor values (-4/512).
    DTYPE (np.dtype): NumPy dtype for parsing binary data structure.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

from ..parser import FileParser

SENS_NORMALIZATION_FACTOR = -4 / 512
DTYPE = np.dtype([('timestamp', '6uint8'), ('x', '>i2'), ('y', '>i2'), ('z', '>i2')])


@dataclass
class Sens(FileParser):
    """Parser for Sens binary accelerometer files.

    This parser reads Sens binary files containing accelerometer data and converts
    them to pandas DataFrames. It handles binary data parsing, timestamp conversion,
    and optional normalization of accelerometer values.

    Attributes:
        normalize (bool): Whether to apply normalization to accelerometer values.
            When True, raw integer values are multiplied by SENS_NORMALIZATION_FACTOR
            to convert to meaningful acceleration units. Defaults to True.

    Examples:
        Reading from a file:

        >>> from labda_parsers.sens import Sens
        >>> parser = Sens(normalize=True)
        >>> df = parser.from_file("data/sensor_data.bin")

        Reading from bytes buffer:

        >>> with open("data/sensor_data.bin", "rb") as f:
        ...     buffer = f.read()
        >>> parser = Sens()
        >>> df = parser.from_buffer(buffer)
    """

    normalize: bool = True

    def _read(
        self,
        obj: Path | bytes,
        func: Callable,
    ) -> pd.DataFrame:
        """Parse binary data using a specified reading function.

        This internal method handles the core parsing logic for Sens binary data,
        including timestamp decoding, data type conversion, and optional normalization.
        It's used by both file and buffer reading methods.

        Args:
            obj (Path | bytes): Either a file path or bytes buffer containing binary data.
            func (Callable): NumPy function to use for reading (np.fromfile or np.frombuffer).

        Returns:
            pd.DataFrame: Parsed accelerometer data with columns:
                - acc_x (float32): X-axis acceleration values
                - acc_y (float32): Y-axis acceleration values
                - acc_z (float32): Z-axis acceleration values
                Index is datetime in UTC timezone.

        Raises:
            ValueError: If the data is empty or cannot be parsed.

        Notes:
            - Timestamps are decoded from 6-byte big-endian format to milliseconds
            - Raw acceleration values are 16-bit signed integers
            - If normalize=True, values are multiplied by SENS_NORMALIZATION_FACTOR
            - Final data is converted to float32 for memory efficiency

        Examples:
            >>> from labda_parsers.sens import Sens
            >>> parser = Sens()
            >>> df = parser._read(path, np.fromfile)
        """
        data = func(obj, dtype=DTYPE, count=-1, offset=0)
        timestamps = np.dot(data['timestamp'], [1 << 40, 1 << 32, 1 << 24, 1 << 16, 1 << 8, 1])

        df = pd.DataFrame(
            {
                'datetime': pd.to_datetime(timestamps, unit='ms', utc=True),
                'acc_x': data['x'].astype(np.int16),
                'acc_y': data['y'].astype(np.int16),
                'acc_z': data['z'].astype(np.int16),
            }
        )

        self.check_empty(df)

        df.set_index('datetime', inplace=True)

        if self.normalize:
            df = df * SENS_NORMALIZATION_FACTOR

        return df.astype(np.float32)

    def from_file(self, path: str | Path) -> pd.DataFrame:
        """Parse a Sens binary file and return accelerometer data as a DataFrame.

        Reads a Sens binary file containing accelerometer data and converts it to
        a pandas DataFrame with standardized column names and datetime indexing.

        Args:
            path (str | Path): Path to the .bin file to parse.

        Returns:
            pd.DataFrame: Accelerometer data with columns:
                - acc_x (float32): X-axis acceleration values
                - acc_y (float32): Y-axis acceleration values
                - acc_z (float32): Z-axis acceleration values
                Index is datetime in UTC timezone.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            ValueError: If the file is not a .bin file or contains no data.
            TypeError: If path is not a string or Path object.

        Examples:
            >>> from labda_parsers.sens import Sens
            >>> parser = Sens()
            >>> df = parser.from_file("data/accelerometer.bin")
        """
        if isinstance(path, str):
            path = Path(path)

        self.check_file(path, '.bin')

        return self._read(path, np.fromfile)

    def from_buffer(self, buffer: bytes) -> pd.DataFrame:
        """Parse Sens binary data from an in-memory bytes buffer.

        Reads Sens binary data from a bytes object and converts it to a pandas
        DataFrame with standardized column names and datetime indexing. Useful
        for processing data received over network or from other in-memory sources.

        Args:
            buffer (bytes): Bytes object containing Sens binary data.

        Returns:
            pd.DataFrame: Accelerometer data with columns:
                - acc_x (float32): X-axis acceleration values
                - acc_y (float32): Y-axis acceleration values
                - acc_z (float32): Z-axis acceleration values
                Index is datetime in UTC timezone.

        Raises:
            TypeError: If buffer is not a bytes object.
            ValueError: If the buffer contains no data or invalid data.

        Examples:
            >>> from labda_parsers.sens import Sens
            >>> with open("data/accelerometer.bin", "rb") as f:
            ...     buffer = f.read()
            >>> parser = Sens()
            >>> df = parser.from_buffer(buffer)
        """
        if not isinstance(buffer, bytes):
            raise TypeError('Expected a bytes object.')

        return self._read(buffer, np.frombuffer)
