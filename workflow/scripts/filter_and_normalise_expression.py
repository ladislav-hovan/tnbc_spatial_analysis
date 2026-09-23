#!/usr/bin/env python

### Imports ###
import pandas as pd

from pathlib import Path
from stoat.modules.utils import save_df_into_filelike

### Functions ###
def filter_and_normalise_expression(
    input_file: Path,
    output_file: Path,
    ratio_threshold: float = 0.1,
) -> None:
    """
    Filters the provided expression data based on a threshold for the
    ratio of samples genes need to be expressed in and performs
    sequencing depth normalisation afterwards.

    Parameters
    ----------
    input_file : Path
        Path to the original expression data file
    output_file : Path
        Path to save the processed expression data file into
    ratio_threshold : float, optional
        Ratio threshold for filtering genes, by default 0.1
    """

    df = pd.read_feather(input_file).set_index('index')
    # Filter the genes
    to_keep = (df > 0).mean(axis=0) >= ratio_threshold
    f_df = df.loc[:, to_keep].copy()
    # Normalise the counts to the median
    region_counts = f_df.sum(axis=1)
    target_count = region_counts.median()
    fn_df = f_df.div(region_counts, axis=0).mul(target_count)
    # Invert the DataFrame for consistency with degree files
    save_df_into_filelike(fn_df.T, output_file, 'feather')

### Main body ###
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-i', '--input', dest='input',
        help='path to the expression data file', metavar='FILE')
    parser.add_argument('-o', '--output', dest='output',
        help='path to save the filtered and normalised expression data into',
        metavar='FILE')
    parser.add_argument('-rt', '--ratio-threshold', dest='ratio_threshold',
        help='minimum ratio of regions in which a gene must be present '
            'to be kept', type=float, default=0.1)
    args = parser.parse_args()

    filter_and_normalise_expression(
        input_file=args.input,
        output_file=args.output,
        ratio_threshold=args.ratio_threshold,
    )