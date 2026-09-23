#!/usr/bin/env python

### Imports ###
import pandas as pd

from pathlib import Path
from typing import Any, List, Optional

### Functions ###
def create_targets_file(
    metadata_file: Path,
    pairing: List[str],
    condition: str,
    output_path: Path,
    select_column: Optional[str] = None,
    select_value: Optional[Any] = None,
) -> None:
    """
    Creates a targets file for limma analysis based on the provided
    metadata file and pairing information.

    Parameters
    ----------
    metadata_file : Path
        Path to the metadata file
    pairing : List[str]
        List of columns to be used for pairing
    condition : str
        Column in the metadata file to be used as condition
    output_path : Path
        Path to write the mapfile to
    select_column : Optional[str], optional
        Column to subset the metadata on, by default None
    select_value : Optional[Any], optional
        Value in the select_column to subset on, by default None
    """

    metadata = pd.read_table(metadata_file)
    if select_column is None:
        metadata_sel = metadata
    else:
        metadata_sel = metadata[metadata[select_column] == select_value]
    metadata_sel.dropna(subset=pairing, inplace=True)
    metadata_sel['Paired'] = metadata_sel.apply(
        lambda row: '_'.join(row[pairing].astype(str)),
        axis=1,
    )
    metadata_sel['Condition'] = metadata_sel[condition]
    counts = metadata_sel.groupby('Paired')['Condition'].nunique()
    mask = counts[counts > 1].index
    subset = metadata_sel[metadata_sel['Paired'].isin(mask)]
    subset[['Paired', 'Condition']].to_csv(output_path, sep='\t')

### Main body ###
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-m', '--metadata', dest='metadata',
        help='path to the metadata file', metavar='FILE')
    parser.add_argument('-p', '--pairing', dest='pairing',
        help='names of the columns to be used for pairing separated by +')
    parser.add_argument('-c', '--condition', dest='condition',
        help='name of the condition column')
    parser.add_argument('-o', '--output', dest='output',
        help='file to save the mapping into', metavar='FILE')
    parser.add_argument('-sc', '--select-column', dest='select_column',
        help='name of the column to subset the data on', default=None)
    parser.add_argument('-sv', '--select-value', dest='select_value',
        help='value in the subsetting column to select', default=None)

    args = parser.parse_args()

    create_targets_file(
        metadata_file=args.metadata,
        pairing=args.pairing.split('+'),
        condition=args.condition,
        output_path=args.output,
        select_column=args.select_column,
        select_value=args.select_value,
    )