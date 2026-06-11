#!/usr/bin/env python

### Imports ###
import pandas as pd

from anndata import AnnData
from os.path import join
from pathlib import Path
from spatialdata import SpatialData

### Functions ###
def convert_feather_to_zarr(
    counts_path: Path,
    spots_path: Path,
    slide: str,
    output_dir: Path,
) -> None:
    """
    Converts the feather format files describing the expression counts
    and spots of Visium data to the zarr format.

    Parameters
    ----------
    counts_path : Path
        Path to the file with the expression counts data
    spots_path : Path
        Path to the file with spots data
    slide : str
        Specific slide to extract from the feather data
    output_dir : Path
        Directory where the zarr format data will be saved under the
        name {slide}.zarr
    """

    # Load the two files
    counts = pd.read_feather(counts_path).set_index('names')
    counts.index.name = None
    spots = pd.read_feather(spots_path).set_index('names')
    spots.index.name = None
    # Select only one slide
    mask = (spots['slide'] == slide).values
    f_counts = counts.loc[mask]
    f_spots = spots.loc[mask]
    # Change the spots index to use only the last part
    f_spots.index = [x.split('.')[-1] for x in f_spots.index]
    # Create an AnnData object using the two DataFrames
    adata = AnnData(f_counts, obs=f_spots)
    adata.obs.drop(['new_x', 'new_y'], axis=1, inplace=True)
    adata.obs.rename(
        columns={'x': 'index_row', 'y': 'index_col'},
        inplace=True,
    )
    # Create a SpatialData object with AnnData as the table
    spatial = SpatialData()
    spatial.tables['table'] = adata
    # Save the data in the zarr format
    spatial.write(join(output_dir, f'{slide}.zarr'), overwrite=True)

### Main body ###
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-c', '--counts', dest='counts',
        help='path to the counts file', metavar='FILE')
    parser.add_argument('-s', '--spots', dest='spots',
        help='path to the spots file', metavar='FILE')
    parser.add_argument('-sl', '--slide', dest='slide',
        help='slide to extract from the feather file')
    parser.add_argument('-od', '--output-dir', dest='output_dir',
        help='directory to save the zarr files into', metavar='DIR')

    args = parser.parse_args()

    convert_feather_to_zarr(
        counts_path=args.counts,
        spots_path=args.spots,
        slide=args.slide,
        output_dir=args.output_dir,
    )