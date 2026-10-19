#!/usr/bin/env python

### Imports ###
import numpy as np
import pandas as pd

from pathlib import Path
from typing import Any, List, Optional

### Functions ###
def replace_final_conditional(
    text: str,
    compare: str,
    sep: str = '_',
    new_final: str = 'rest',
) -> str:
    """
    Replaces the final part of a string if it doesn't match a provided
    string.

    Parameters
    ----------
    text : str
        String which can potentially be amended
    compare : str
        String to compare the final part to
    sep : str, optional
        Separator for splitting the string, by default '_'
    new_final : str, optional
        What to replace the final part with, by default 'rest'

    Returns
    -------
    str
        Potentially amended string
    """

    parts = text.split(sep=sep)
    if parts[-1] == compare:
        # Final part matches - perform no changes
        return text
    else:
        # Replace the final part, reconstruct string
        return sep.join(parts[:-1] + [new_final])


def create_paired_files(
    metadata_file: Path,
    lioness_output_file: Path,
    pairing: List[str],
    condition: str,
    group_a: str,
    group_b: str,
    output_mapfile: Path,
    output_lioness: Path,
    select_column: Optional[str] = None,
    select_value: Optional[Any] = None,
) -> None:
    """
    Selects a column from a metadata file to write into a mapfile.
    Assumes the index in the metadata file corresponds to the
    identifiers for the data points. Also adjusts a LIONESS output file
    to contain the required columns, especially if the 'rest' keyword
    is used to specify all other groups.

    Parameters
    ----------
    metadata_file : Path
        Path to the metadata file
    lioness_output_file : Path
        Path to the LIONESS output file
    pairing : List[str]
        List of columns to be used for pairing
    condition : str
        Column in the metadata file to be used as condition
    group_a : str
        Name of the first group to select
    group_b : str
        Name of the second group to select
    output_mapfile : Path
        Path to write the mapfile to
    output_lioness : Path
        Path to write the adjusted LIONESS output file to
    select_column : Optional[str], optional
        Column to subset the data on or None to not subset,
        by default None
    select_value : Optional[Any], optional
        Value in the subsetting column to select, by default None
    """

    metadata = pd.read_table(metadata_file)
    lioness = pd.read_feather(lioness_output_file)
    lioness = lioness.set_index(lioness.columns[0]).T
    # Subset the data if desired
    if select_column is None:
        metadata_sel = metadata
        lioness_sel = lioness
    else:
        metadata_sel = metadata[metadata[select_column] == select_value]
        lioness_sel = lioness[metadata[select_column] == select_value]
    # Create a column for pairing
    metadata_sel.dropna(subset=pairing, inplace=True)
    metadata_sel['Paired'] = metadata_sel.apply(
        lambda row: '_'.join(row[pairing].astype(str)),
        axis=1,
    )
    # Handle the special 'rest' keyword
    if group_a == 'rest':
        # rest vs group_b
        metadata_sel[condition] = metadata_sel[condition].apply(lambda x:
            replace_final_conditional(x, group_b))
        metadata_sel.index = [replace_final_conditional(x, group_b)
            for x in metadata_sel.index]
    elif group_b == 'rest':
        # group_a vs rest
        metadata_sel[condition] = metadata_sel[condition].apply(lambda x:
            replace_final_conditional(x, group_a))
        metadata_sel.index = [replace_final_conditional(x, group_a)
            for x in metadata_sel.index]
    else:
        # group_a vs group_b, drop everything else
        metadata_sel[condition] = metadata_sel[condition].apply(
            lambda x: np.nan if (x != group_a and x != group_b) else x)
        metadata_sel.dropna(subset=condition, inplace=True)
        lioness_sel = lioness_sel.loc[metadata_sel.index]
    # Make sure that the adjusted names are added to LIONESS DataFrame
    lioness_sel['Condition'] = metadata_sel.index
    # The above process can create duplicates, drop them
    metadata_sel.drop_duplicates(inplace=True)
    # Keep only matches which have exactly two samples
    counts = metadata_sel.groupby('Paired')[condition].nunique()
    mask = counts[counts == 2].index
    subset = metadata_sel[metadata_sel['Paired'].isin(mask)]
    # Pivot the DataFrame to create a matching index
    subset.reset_index(inplace=True)
    df = subset.pivot(columns=condition, values='index', index='Paired')
    # Group the LIONESS output and create a frame with averages
    lioness_grouped = lioness_sel.groupby('Condition').mean()
    # Save the resulting DataFrames
    df.to_csv(output_mapfile, index=False)
    lioness_grouped.T.to_csv(output_lioness, sep='\t')

### Main body ###
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-m', '--metadata', dest='metadata',
        help='path to the metadata file', metavar='FILE')
    parser.add_argument('-l', '--lioness', dest='lioness',
        help='path to the LIONESS output file', metavar='FILE')
    parser.add_argument('-sc', '--select-column', dest='select_column',
        help='name of the column to subset the data on', default=None)
    parser.add_argument('-sv', '--select-value', dest='select_value',
        help='value in the subsetting column to select', default=None)
    parser.add_argument('-p', '--pairing', dest='pairing',
        help='names of the columns to be used for pairing separated by +')
    parser.add_argument('-c', '--condition', dest='condition',
        help='name of the condition column')
    parser.add_argument('-ga', '--group-a', dest='group_a',
        help='name of the first group to select')
    parser.add_argument('-gb', '--group-b', dest='group_b',
        help='name of the second group to select')
    parser.add_argument('-om', '--output-mapfile', dest='output_mapfile',
        help='file to save the mapping into', metavar='FILE')
    parser.add_argument('-ol', '--output-lioness', dest='output_lioness',
        help='file to save the adjusted LIONESS output into', metavar='FILE')

    args = parser.parse_args()

    create_paired_files(
        metadata_file=args.metadata,
        lioness_output_file=args.lioness,
        pairing=args.pairing.split('+'),
        condition=args.condition,
        group_a=args.group_a,
        group_b=args.group_b,
        output_mapfile=args.output_mapfile,
        output_lioness=args.output_lioness,
        select_column=args.select_column,
        select_value=args.select_value,
    )