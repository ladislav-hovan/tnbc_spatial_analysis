#!/usr/bin/env python

### Imports ###
from pathlib import Path
from stoat import Stoat
from stoat.modules.utils import save_df_into_filelike

### Functions ###
def cluster_and_aggregate_expression(
    zarr_path: Path,
    classification_path: Path,
    expression_path: Path,
    min_counts_per_spot: float = 0.0,
    resolution: float = 1.0,
) -> None:

    # Loadingc zarr
    stoat_obj = Stoat()
    stoat_obj.load_zarr(zarr_path)
    # Filtering genes and spots
    stoat_obj.filter_genes(drop_deprecated=True, min_counts=1)
    stoat_obj.filter_spots(min_counts=min_counts_per_spot)
    # Assigning regions based on expression clustering
    stoat_obj.assign_regions(from_expression=True,
        clustering_opts=dict(resolution=resolution))
    # Save spot classifications
    st = stoat_obj.spatial[stoat_obj.table]
    save_df_into_filelike(st.obs['region_id'], classification_path, 'feather')
    # Save aggregated expression data
    save_df_into_filelike(st.varm['collapsed'].sparse.to_dense(),
        expression_path, 'feather')

### Main body ###
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-i', '--input', dest='input',
        help='path to the zarr input', metavar='ZARR')
    parser.add_argument('-cp', '--classification_path', dest='classification',
        help='path to save the spot classifications into', metavar='FILE')
    parser.add_argument('-ep', '--expression_path', dest='expression',
        help='path to save the aggregated expression data into',
        metavar='FILE')
    parser.add_argument('-mc', '--min_counts', dest='min_counts',
        help='minimum number of counts for a spot to be kept', type=float,
        default=0.0)
    parser.add_argument('-r', '--resolution', dest='resolution',
        help='resolution parameter for clustering', type=float)

    args = parser.parse_args()

    cluster_and_aggregate_expression(
        zarr_path = args.input,
        classification_path = args.classification,
        expression_path = args.expression,
        min_counts_per_spot=args.min_counts,
        resolution=args.resolution,
    )