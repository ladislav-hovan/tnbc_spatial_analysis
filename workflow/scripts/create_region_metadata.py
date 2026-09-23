#!/usr/bin/env python

### Imports ###
import pandas as pd

from pathlib import Path

### Functions ###
def create_region_metadata(
    expression_file: Path,
    metadata_file: Path,
) -> None:
    """
    Creates a metadata file for the regions based on the provided
    aggregated expression data.

    Parameters
    ----------
    expression_file : Path
        Path to the aggregated expression data file
    metadata_file : Path
        Path to save the metadata file into
    """

    expr_df = pd.read_feather(expression_file).set_index('index').T
    # Copy sample ID from the index
    meta_df = pd.DataFrame({'Sample_ID': expr_df.index}, index=expr_df.index)
    # Derive the metadata columns from the sample ID
    meta_df['Patient'] = meta_df['Sample_ID'].str.split('_').str[0]
    meta_df['Slide'] = meta_df['Sample_ID'].str.split('_'
        ).str[1:3].str.join('_')
    meta_df['Classification'] = meta_df['Sample_ID'].str.split('_').str[3]
    # Drop the Sample_ID column and save the metadata to a file
    meta_df.drop(columns=['Sample_ID'], inplace=True)
    meta_df.index.name = None
    meta_df.to_csv(metadata_file, sep='\t', index_label=False)

### Main body ###
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-e', '--expression', dest='expression',
        help='path to the expression file', metavar='FILE')
    parser.add_argument('-m', '--metadata', dest='metadata',
        help='path to save the metadata into', metavar='FILE')

    args = parser.parse_args()

    create_region_metadata(
        expression_file=args.expression,
        metadata_file=args.metadata,
    )