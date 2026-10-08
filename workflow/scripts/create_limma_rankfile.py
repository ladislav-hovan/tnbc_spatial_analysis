#!/usr/bin/env python

### Imports ###
from pandas import read_table
from pathlib import Path

### Functions ###
def create_limma_rankfile(
    input_path: Path,
    output_path: Path,
) -> None:
    """
    Creates a rank file from limma results.

    Parameters
    ----------
    input_path : Path
        Path to the input tsv file
    output_path : Path
        Path to save the rank file into
    """

    # Load the tsv file and sort the right column
    df = read_table(input_path, index_col=0)
    df_t = df['t'].copy()
    df_t.sort_values(ascending=False, inplace=True)
    # Save the DataFrame to a tsv file
    df_t.to_csv(output_path, sep='\t', header=False)

### Main body ###
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-i', '--input', dest='input',
        help='path to the input tsv file', metavar='FILE')
    parser.add_argument('-o', '--output', dest='output',
        help='path to save the rank file into', metavar='FILE')

    args = parser.parse_args()

    create_limma_rankfile(
        input_path=args.input,
        output_path=args.output
    )