#!/usr/bin/env python

### Imports ###
import pandas as pd

from pathlib import Path

### Functions ###
def adjust_lioness_output_for_paired(
    input_lioness: Path,
    input_adjustment: Path,
    output_path: Path,
) -> None:
    """
    Selects particular samples for a LIONESS dataset and computes an
    average of degrees for samples associated with given conditions.

    Parameters
    ----------
    input_lioness : Path
        Path to the input LIONESS output file
    input_adjustment : Path
        Path to the input adjustment file
    output_path : Path
        Path to save the converted tsv file into
    """

    # Load the feather file and set the correct index column
    lioness = pd.read_feather(input_lioness)
    ind_col_name = lioness.columns[0]
    lioness = lioness.set_index(ind_col_name).T
    # Load the adjustment file
    adjustment = pd.read_csv(input_adjustment, index_col=0)
    # Subset the required columns
    selected = lioness.loc[adjustment['Keep']]
    # Group by condition and average the values
    adjusted = selected.groupby(adjustment['Condition']).mean()
    # Save the adjusted DataFrame
    adjusted.T.to_csv(output_path, sep='\t')

### Main body ###
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-il', '--input-lioness', dest='input_lioness',
        help='path to the input LIONESS output file', metavar='FILE')
    parser.add_argument('-ia', '--input-adjustment', dest='input_adjustment',
        help='path to the input adjustment file', metavar='FILE')
    parser.add_argument('-o', '--output', dest='output',
        help='path to save the adjusted LIONESS output into', metavar='FILE')

    args = parser.parse_args()

    adjust_lioness_output_for_paired(
        input_lioness=args.input_lioness,
        input_adjustment=args.input_adjustment,
        output_path=args.output,
    )