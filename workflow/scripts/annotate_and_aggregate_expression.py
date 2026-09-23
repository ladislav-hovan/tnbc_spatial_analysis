#!/usr/bin/env python

### Imports ###
from pandas import read_feather
from pathlib import Path
from stoat import Stoat
from stoat.modules.utils import save_df_into_filelike

### Functions ###
def annotate_and_aggregate_expression(
    zarr_path: Path,
    classification_path: Path,
    expression_path: Path,
    min_counts_per_spot: float = 0.0,
) -> None:
    """
    Annotates spots with region classification information and
    aggregates expression data for the regions.

    Parameters
    ----------
    zarr_path : Path
        Path to the zarr input
    classification_path : Path
        Path to the file containing the spot classifications
    expression_path : Path
        Path to save the aggregated expression data into
    min_counts_per_spot : float, optional
        Minimum number of counts for a spot to be kept, by default 0.0
    """

    # Loading zarr
    stoat_obj = Stoat()
    stoat_obj.load_zarr(zarr_path)
    # Filtering genes and spots
    stoat_obj.filter_genes(drop_deprecated=True, min_counts=1)
    stoat_obj.filter_spots(min_counts=min_counts_per_spot)
    # Assigning regions based on provided classifications
    df = read_feather(classification_path)
    df[['array_x', 'array_y']] = df[['array_x', 'array_y']].astype(int)
    df['index_col'] = df[['array_x', 'array_y']].apply(
        lambda row: 'x'.join([str(x) for x in row]), axis=1)
    df_idx = df.set_index('index_col')
    df_idx = df_idx.drop(columns=['array_x', 'array_y'])
    df_idx['region_annotation'] = df_idx.idxmax(axis=1)
    stoat_obj.assign_regions(mapping=df_idx['region_annotation'])
    # Save aggregated expression data
    st = stoat_obj.spatial[stoat_obj.table]
    save_df_into_filelike(st.varm['collapsed'].sparse.to_dense(),
        expression_path, 'feather')

### Main body ###
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-i', '--input', dest='input',
        help='path to the zarr input', metavar='ZARR')
    parser.add_argument('-cp', '--classification_path', dest='classification',
        help='path to load the spot classifications from', metavar='FILE')
    parser.add_argument('-ep', '--expression_path', dest='expression',
        help='path to save the aggregated expression data into',
        metavar='FILE')
    parser.add_argument('-mc', '--min_counts', dest='min_counts',
        help='minimum number of counts for a spot to be kept', type=float,
        default=0.0)

    args = parser.parse_args()

    annotate_and_aggregate_expression(
        zarr_path = args.input,
        classification_path = args.classification,
        expression_path = args.expression,
        min_counts_per_spot=args.min_counts,
    )