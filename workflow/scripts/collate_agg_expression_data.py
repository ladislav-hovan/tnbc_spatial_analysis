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
    patient_id_idx: int,
    slide_idx: int,
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
    patient_id_idx : int
        Index of the patient ID in the file path
    slide_idx : int
        Index of the slide in the file path
    """

    data_list = []
    for data_path in agg_expr_files:
        df = pd.read_feather(data_path).set_index('index')
        # Figure out patient ID and slide names
        parts = Path(data_path).parts
        patient_id = parts[patient_id_idx]
        slide = parts[slide_idx]
        # Rename the columns to include patient and slide information
        df.rename(columns=lambda x: f'{patient_id}_{slide}_{x}', inplace=True)
        data_list.append(df.T)
    # Convert the list of dataframes into a single dataframe and save it
    df = pd.concat(data_list)
    save_df_into_filelike(df.fillna(0), output_file, 'feather')

### Main body ###
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-ef', '--expression-files', dest='expr_files',
        help='files with the aggregated expression data', action='extend',
        nargs='+', metavar='FILE')
    parser.add_argument('-pi', '--patient-id-idx', dest='patient_id_idx',
        type=int, help='index of the patient ID in the file path',
        metavar='INT')
    parser.add_argument('-si', '--slide-id-idx', dest='slide_id_idx', type=int,
        help='index of the slide ID in the file path', metavar='INT')
    parser.add_argument('-o', '--output', dest='output',
        help='file to save the collated data into', metavar='FILE')

    args = parser.parse_args()

    collate_agg_expression_data(
        agg_expr_files=args.expr_files,
        output_file=args.output,
        patient_id_idx=args.patient_id_idx,
        slide_idx=args.slide_id_idx,
    )