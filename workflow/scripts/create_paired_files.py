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
    pairing: List[str],
    condition: str,
    group_a: str,
    group_b: str,
    output_mapfile: Path,
    output_adjustment: Path,
    select_column: Optional[str] = None,
    select_value: Optional[Any] = None,
) -> None:
    """
    Selects a column from a metadata file to write into a mapfile.
    Assumes the index in the metadata file corresponds to the
    identifiers for the data points. Also creates an adjustment file
    which can be used to modify LIONESS output for paired analysis.

    Parameters
    ----------
    metadata_file : Path
        Path to the metadata file
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
    output_adjustment : Path
        Path to write the adjustment file to
    select_column : Optional[str], optional
        Column to subset the data on or None to not subset,
        by default None
    select_value : Optional[Any], optional
        Value in the subsetting column to select, by default None
    """

    metadata = pd.read_table(metadata_file)
    adjustment = pd.DataFrame(index=metadata.index)
    # Subset the data if desired
    if select_column is None:
        metadata_sel = metadata
        adjustment['Keep'] = True
    else:
        metadata_sel = metadata[metadata[select_column] == select_value]
        adjustment['Keep'] = (metadata[select_column] == select_value)
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
        adjustment['Condition'] = metadata_sel.index
    elif group_b == 'rest':
        # group_a vs rest
        metadata_sel[condition] = metadata_sel[condition].apply(lambda x:
            replace_final_conditional(x, group_a))
        metadata_sel.index = [replace_final_conditional(x, group_a)
            for x in metadata_sel.index]
        adjustment['Condition'] = metadata_sel.index
    else:
        # group_a vs group_b, drop everything else
        metadata_sel[condition] = metadata_sel[condition].apply(
            lambda x: np.nan if (x != group_a and x != group_b) else x)
        adjustment['Keep'] = (adjustment['Keep'] &
            ~metadata_sel[condition].isna())
        metadata_sel.dropna(subset=condition, inplace=True)
    # The above process can create duplicates, drop them
    metadata_sel.drop_duplicates(inplace=True)
    # Keep only matches which have exactly two samples
    counts = metadata_sel.groupby('Paired')[condition].nunique()
    mask = counts[counts == 2].index
    subset = metadata_sel[metadata_sel['Paired'].isin(mask)]
    # Do the same for the adjustment DataFrame
    adjustment['Keep'] = (adjustment['Keep'] &
        adjustment['Condition'].isin(subset.index))
    # Pivot the DataFrame to create a matching index
    subset.reset_index(inplace=True)
    df = subset.pivot(columns=condition, values='index', index='Paired')
    # Save the resulting DataFrames
    df.to_csv(output_mapfile, index=False)
    adjustment.to_csv(output_adjustment, sep='\t')

### Main body ###
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-m', '--metadata', dest='metadata',
        help='path to the metadata file', metavar='FILE')
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
    parser.add_argument('-oa', '--output-adjustment', dest='output_adjustment',
        help='file to save the adjustment file into', metavar='FILE')

    args = parser.parse_args()

    create_paired_files(
        metadata_file=args.metadata,
        pairing=args.pairing.split('+'),
        condition=args.condition,
        group_a=args.group_a,
        group_b=args.group_b,
        output_mapfile=args.output_mapfile,
        output_adjustment=args.output_adjustment,
        select_column=args.select_column,
        select_value=args.select_value,
    )