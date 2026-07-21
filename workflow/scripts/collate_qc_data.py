#!/usr/bin/env python

### Imports ###
import pandas as pd

from pathlib import Path
from typing import Iterable

### Functions ###
def collate_qc_data(
    qc_files: Iterable[Path],
    output_file: Path,
) -> None:
    """
    Collects the QC data from the provided files into a single table.

    Parameters
    ----------
    qc_files : Iterable[Path]
        Iterable of paths to the QC data files
    output_file : Path
        Path where the final table will be saved
    """

    data_list = [pd.read_table(qc_f) for qc_f in qc_files]
    df = pd.concat(data_list)
    df.to_csv(output_file, index=False, sep='\t')

### Main body ###
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-qc', '--qc-files', dest='qc_files',
        help='files with the qc data', action='extend', nargs='+',
        metavar='FILE')
    parser.add_argument('-o', '--output', dest='output',
        help='file to save the collated data into', metavar='FILE')

    args = parser.parse_args()

    collate_qc_data(
        qc_files=args.qc_files,
        output_file=args.output,
    )