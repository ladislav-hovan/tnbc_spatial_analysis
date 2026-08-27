#!/usr/bin/env python

### Imports ###
import pandas as pd

from pathlib import Path
from stoat.modules.utils import save_df_into_filelike
from typing import Iterable

### Functions ###
def collate_agg_expression_data(
    agg_expr_files: Iterable[Path],
    output_file: Path,
) -> None:
    """
    Collects the aggregated expression data from the provided files
    into a single table.

    Parameters
    ----------
    agg_expr_files : Iterable[Path]
        Iterable of paths to the aggregated expression data files
    output_file : Path
        Path where the final table will be saved
    """

    data_list = []
    for data_path in agg_expr_files:
        df = pd.read_feather(data_path).set_index('index')
        # Figure out patient ID and slide names
        parts = Path(data_path).parts
        patient_id = parts[-5]
        slide = parts[-4]
        # Rename the columns to include patient and slide information
        df.rename(columns=lambda x: f'{patient_id}_{slide}_{x}', inplace=True)
        data_list.append(df.T)
    df = pd.concat(data_list)
    print (df)
    save_df_into_filelike(df.fillna(0), output_file, 'feather')

### Main body ###
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-ef', '--expression-files', dest='expr_files',
        help='files with the aggregated expression data', action='extend',
        nargs='+', metavar='FILE')
    parser.add_argument('-o', '--output', dest='output',
        help='file to save the collated data into', metavar='FILE')

    args = parser.parse_args()

    collate_agg_expression_data(
        agg_expr_files=args.expr_files,
        output_file=args.output,
    )