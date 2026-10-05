#!/usr/bin/env python

### Imports ###
from pandas import read_feather
from pathlib import Path

### Functions ###
def convert_lioness_output(
    input_path: Path,
    output_path: Path,
) -> None:
    """
    Converts the lioness output file from a feather file to a tsv file.

    Parameters
    ----------
    input_path : Path
        Path to the input feather file
    output_path : Path
        Path to save the converted tsv file into
    """

    # Load the feather file and set the correct index column
    df = read_feather(input_path)
    ind_col_name = df.columns[0]
    df.set_index(ind_col_name, inplace=True)
    # Save the DataFrame to a tsv file
    df.to_csv(output_path, sep='\t')

### Main body ###
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-i', '--input', dest='input',
        help='path to the input feather file', metavar='FILE')
    parser.add_argument('-o', '--output', dest='output',
        help='path to save the converted tsv file into', metavar='FILE')

    args = parser.parse_args()

    convert_lioness_output(
        input_path=args.input,
        output_path=args.output
    )