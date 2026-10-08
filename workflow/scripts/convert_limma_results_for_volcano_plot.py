#!/usr/bin/env python

### Imports ###
from pandas import read_table
from pathlib import Path

### Functions ###
def convert_limma_results_for_volcano_plot(
    input_path: Path,
    mapping: list[str],
    output_path: Path,
) -> None:
    """
    Converts the limma results file header to be compatible with the
    sisana's volcano plot visualization.

    Parameters
    ----------
    input_path : Path
        Path to the input results file
    mapping : list[str]
        List containing the old and new column names
    output_path : Path
        Path to save the adjusted file into
    """

    df = read_table(input_path)
    # Adjust the column name
    df = df.rename(columns={mapping[0]: mapping[1]})
    # Save the adjusted DataFrame to a new file
    df.to_csv(output_path, sep='\t', index=False)

### Main body ###
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-i', '--input', dest='input',
        help='path to the limma results file', metavar='FILE')
    parser.add_argument('-m', '--mapping', dest='mapping', nargs=2,
        help='old and new column names', metavar='COL')
    parser.add_argument('-o', '--output', dest='output',
        help='path to save the adjusted file into', metavar='FILE')

    args = parser.parse_args()

    convert_limma_results_for_volcano_plot(
        input_path=args.input,
        mapping=args.mapping,
        output_path=args.output
    )