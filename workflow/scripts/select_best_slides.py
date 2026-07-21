#!/usr/bin/env python

### Imports ###
import pandas as pd

from pathlib import Path

### Functions ###
def select_best_slides(
    collated_qc_file: Path,
    mapping_file: Path,
) -> None:
    """
    Selects the best slides for each patient based on QC metrics.

    Parameters
    ----------
    collated_qc_file : Path
        Path to the file containing the collated QC data
    mapping_file : Path
        Path where the output mapping file will be saved
    """

    # Read the QC data
    qc_data = pd.read_table(collated_qc_file)
    # Create a new DataFrame to hold the results
    df = pd.DataFrame(index=qc_data['patient_id'].unique())
    df.index.name = 'patient_id'
    # Iterate over QC columns
    for field in qc_data.columns[2:]:
        # Find the best value for each patient
        field_max = qc_data.groupby('patient_id')[field].max()
        # Find which rows contain these best values
        valid = qc_data.apply(lambda row:
            field_max[row['patient_id']] == row[field], axis=1)
        # Select these rows
        selection = qc_data[valid][['patient_id', 'slide']]
        # Rename the slide field
        field_name = 'best_' + field
        mapping = selection.rename(
            columns={'slide': field_name}).set_index('patient_id')
        # Add to the DataFrame
        df[field_name] = mapping
    # Save the result (keep the index)
    df.to_csv(mapping_file, sep='\t')

### Main body ###
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-i', '--input', dest='input',
        help='file with the collated qc data', metavar='FILE')
    parser.add_argument('-o', '--output', dest='output',
        help='file to save the best slides data into', metavar='FILE')

    args = parser.parse_args()

    select_best_slides(
        collated_qc_file=args.input,
        mapping_file=args.output,
    )