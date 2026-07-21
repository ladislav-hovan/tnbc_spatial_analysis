#!/usr/bin/env python

### Imports ###
import pandas as pd

from pathlib import Path
from stoat import Stoat

### Functions ###
def calculate_qc_metrics(
    zarr_path: Path,
    qc_plot: Path,
    joint_qc_plot: Path,
    data_file: Path,
) -> None:
    """
    Calculates the quality control (QC) metrics for a given zarr store
    and saves them as plots and a small data table.

    Parameters
    ----------
    zarr_path : Path
        Path to the zarr store
    qc_plot : Path
        Path to the resulting QC plot (three separate metrics)
    joint_qc_plot : Path
        Path to the resulting joint QC plot
    data_file : Path
        Path to the resulting data file
    """

    # Load the Stoat object from zarr
    stoat_obj = Stoat()
    stoat_obj.load_zarr(zarr_path)
    # We are only interested in spots with tissue
    st = stoat_obj.spatial[stoat_obj.table]
    st._inplace_subset_obs(st.obs['in_tissue'])
    # Calculate the QC metrics and save the plots
    stoat_obj.calculate_qc_metrics()
    fig,ax = stoat_obj.plot_qc_metrics()
    fig.savefig(qc_plot, dpi=300, bbox_inches='tight')
    ax = stoat_obj.plot_joint_qc_metrics()
    ax.get_figure().savefig(joint_qc_plot, dpi=300, bbox_inches='tight')
    # Create a table containing all the important data
    st_obs = stoat_obj.spatial[stoat_obj.table].obs
    parts = Path(qc_plot).parts
    data = {}
    # Identifying the patient and slide based on the file name
    data['patient_id'] = [parts[-3]]
    data['slide'] = [parts[-2]]
    # Actual QC information
    data['genes_mean'] = ['{:.2f}'.format(st_obs['n_genes_by_counts'].mean())]
    data['genes_median'] = ['{:.2f}'.format(
        st_obs['n_genes_by_counts'].median())]
    data['counts_mean'] = ['{:.2f}'.format(st_obs['total_counts'].mean())]
    data['counts_median'] = ['{:.2f}'.format(st_obs['total_counts'].median())]
    df = pd.DataFrame(data)
    # Save the table into a file
    df.to_csv(data_file, index=False, sep='\t')

### Main body ###
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-i', '--input', dest='input',
        help='path to the zarr input', metavar='ZARR')
    parser.add_argument('-qc', '--qc', dest='qc',
        help='file to save the qc plot to', metavar='FILE')
    parser.add_argument('-jqc', '--joint-qc', dest='joint_qc',
        help='file to save the joint qc plot to', metavar='FILE')
    parser.add_argument('-d', '--data', dest='data',
        help='file to save the qc data to', metavar='FILE')

    args = parser.parse_args()

    calculate_qc_metrics(
        zarr_path=args.input,
        qc_plot=args.qc,
        joint_qc_plot=args.joint_qc,
        data_file=args.data,
    )