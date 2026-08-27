#!/usr/bin/env python

### Imports ###
import anndata as ad
import numpy as np
import pandas as pd

from os.path import join
from pathlib import Path
from scipy.sparse import csr_matrix
from sklearn.linear_model import LinearRegression
from spatialdata import SpatialData

### Functions ###
def add_missing_spots(
    spatial_table: ad.AnnData,
) -> ad.AnnData:
    """
    Adds missing spots within range of present spots to the AnnData
    object provided, also performs other transformations (reordering,
    removing NaNs and converting to sparse format).

    Parameters
    ----------
    spatial_table : ad.AnnData
        Table containing the spatial information

    Returns
    -------
    ad.AnnData
        Adjusted table following the modifications
    """

    # Determine the current range of observations
    obs = spatial_table.obs
    row_range = (obs['array_row'].min(), obs['array_row'].max())
    col_range = (obs['array_col'].min(), obs['array_col'].max())
    index = []
    data = {'array_row': [], 'array_col': []}
    # Iterate over all combinations within range
    for r in range(row_range[0], row_range[1] + 1):
        for c in range(col_range[0], col_range[1] + 1):
            # Only valid combinations are even + even or odd + odd
            if r % 2 != c % 2:
                continue
            label = f'{r}x{c}'
            # Skip if already present
            if label in obs.index:
                continue
            index.append(label)
            data['array_row'].append(r)
            data['array_col'].append(c)
    # Create the rudimentary data frame with the extra spots
    df = pd.DataFrame(data, index=index)
    # These spots are not in tissue
    df['in_tissue'] = False
    # Train the relationship of row/col to pixels and predict missing values
    X_train = obs[['array_row', 'array_col']]
    for dim in ['pixel_x', 'pixel_y']:
        model = LinearRegression()
        model.fit(X_train, obs[dim])
        predicted = model.predict(df[['array_row', 'array_col']])
        df[dim] = pd.Series(predicted, index=df.index)
    # Convert to AnnData
    adata = ad.AnnData(pd.DataFrame(index=index,
        columns=spatial_table.var_names), obs=df)
    # Join with the provided object
    spatial_table = ad.concat((spatial_table, adata), join='outer')
    # Fill in the slide name for the new spots
    slide = spatial_table.obs.iloc[0]['slide']
    spatial_table.obs['slide'] = spatial_table.obs['slide'].fillna(slide)
    # Convert to sparse matrix
    spatial_table.X = spatial_table.X.astype(float)
    spatial_table.X[np.isnan(spatial_table.X)] = 0.0
    spatial_table.X = csr_matrix(spatial_table.X)
    # Sort the index properly
    sorted_index = sorted(spatial_table.obs_names, key=lambda x: [
        int(y) for y in x.split('x')])
    spatial_table = spatial_table[sorted_index, :]
    # Move the pixels to obsm table
    # Transform them for proper neighbour calculations
    spatial_table.obsm['spatial'] = np.zeros((spatial_table.n_obs, 2))
    spatial_table.obsm['spatial'][:, 1] = spatial_table.obs['pixel_x'].values
    spatial_table.obsm['spatial'][:, 0] = -((2 * np.sin(np.radians(60)) / 3) *
        spatial_table.obs['pixel_y'].values)

    return spatial_table


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
    adata = ad.AnnData(f_counts, obs=f_spots)
    adata.obs.drop(['new_x', 'new_y'], axis=1, inplace=True)
    adata.obs.rename(
        columns={'x': 'array_row', 'y': 'array_col'},
        inplace=True,
    )
    # Only spots with tissue are present
    adata.obs['in_tissue'] = True
    # Add the missing ones without tissue
    adata = add_missing_spots(adata)
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