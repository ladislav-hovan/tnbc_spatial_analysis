#!/usr/bin/env python

### Imports ###
import pandas as pd

from pathlib import Path
from typing import Any, Optional

### Functions ###
def create_mapfile(
    metadata_file: Path,
    column: str,
    output_path: Path,
    select_column: Optional[str] = None,
    select_value: Optional[Any] = None,
) -> None:
    """
    Selects a column from a metadata file to write into a mapfile.

    Parameters
    ----------
    metadata_file : Path
        Path to the metadata file
    column : str
        Column in the metadata file to be used
    output_path : Path
        Path to write the mapfile to
    select_column : Optional[str], optional
        Column to subset the data on or None to not subset,
        by default None
    select_value : Optional[Any], optional
        Value in the subsetting column to select, by default None
    """

    metadata = pd.read_table(metadata_file)
    if select_column is None:
        metadata_sel = metadata
    else:
        metadata_sel = metadata[metadata[select_column] == select_value]
    metadata_sel[column].to_csv(output_path)

### Main body ###
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-m', '--metadata', dest='metadata',
        help='path to the metadata file', metavar='FILE')
    parser.add_argument('-c', '--column', dest='column',
        help='name of the column to process')
    parser.add_argument('-o', '--output', dest='output',
        help='file to save the mapping into', metavar='FILE')
    parser.add_argument('-sc', '--select-column', dest='select_column',
        help='name of the column to subset the data on', default=None)
    parser.add_argument('-sv', '--select-value', dest='select_value',
        help='value in the subsetting column to select', default=None)

    args = parser.parse_args()

    create_mapfile(
        metadata_file=args.metadata,
        column=args.column,
        output_path=args.output,
        select_column=args.select_column,
        select_value=args.select_value,
    )