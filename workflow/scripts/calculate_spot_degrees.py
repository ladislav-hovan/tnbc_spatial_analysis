#!/usr/bin/env python

### Imports ###
from os.path import join
from pathlib import Path
from shutil import rmtree
from stoat import Stoat
from stoat.modules.analysis import collate_degrees
from stoat.modules.utils import weigh_by_distance_and_correlation
from typing import Literal

from gpu_manager import GpuManager, allocate_gpus

### Functions ###
def execute_stoat_workflow(
    zarr_path: Path,
    motif_prior: Path,
    ppi_prior: Path,
    indegrees: Path,
    outdegrees: Path,
    min_counts_per_spot: float = 0.0,
    computing: Literal['cpu', 'gpu'] = 'cpu',
) -> None:
    """
    Executes the STOAT workflow to calculate indegrees and outdegrees
    for spots in a spatial transcriptomics dataset and collates the
    results into the specified output files.

    Parameters
    ----------
    zarr_path : Path
        Path to the zarr input
    motif_prior : Path
        Path to the motif prior file
    ppi_prior : Path
        Path to the PPI prior file
    indegrees : Path
        Path to save the indegrees into
    outdegrees : Path
        Path to save the outdegrees into
    min_counts_per_spot : float, optional
        Minimum number of counts for a spot to be kept, by default 0.0
    computing : Literal['cpu', 'gpu'], optional
        Whether to use CPU or GPU computation, by default 'cpu'
    """

    # Loading zarr
    stoat_obj = Stoat()
    stoat_obj.load_zarr(zarr_path)
    # Filtering genes and spots
    stoat_obj.filter_genes(drop_deprecated=True, min_counts=1)
    stoat_obj.filter_spots(min_counts=min_counts_per_spot)
    # Averaging expression
    stoat_obj.average_expression(
        avg_function=weigh_by_distance_and_correlation,
        kernel='gaussian',
        sigma=0.4,
    )
    stoat_obj.assign_regions(layer='averaged')
    # Network calculation
    output_dir = join(Path(outdegrees).parent, '.tmp')
    stoat_obj.calculate_networks(
        save_dir=output_dir,
        motif_prior=motif_prior,
        ppi_prior=ppi_prior,
        computing=computing,
        modeProcess='intersection',
        save_stoat=False,
        save_degrees=True,
        overwrite_old=True,
    )
    # Collate output files
    collate_degrees(
        stoat_folder=output_dir,
        format='feather',
        output_file=indegrees,
    )
    collate_degrees(
        stoat_folder=output_dir,
        format='feather',
        output_file=outdegrees,
        base_to_match='outdegree_*',
        col_name='Outdegrees',
    )
    # Remove the temporary directory
    rmtree(output_dir)


def calculate_spot_degrees(
    zarr_path: Path,
    motif_prior: Path,
    ppi_prior: Path,
    indegrees: Path,
    outdegrees: Path,
    min_counts_per_spot: float = 0.0,
    computing: Literal['cpu', 'gpu'] = 'cpu',
) -> None:
    """
    Calculates the indegrees and outdegrees of the gene regulatory
    networks from the given spatial transcriptomics data and priors.
    Uses the STOAT algorithm to reconstruct the networks.

    Parameters
    ----------
    zarr_path : Path
        Path to the zarr input
    motif_prior : Path
        Path to the motif prior file
    ppi_prior : Path
        Path to the PPI prior file
    indegrees : Path
        Path to save the indegrees into
    outdegrees : Path
        Path to save the outdegrees into
    min_counts_per_spot : float, optional
        Minimum number of counts for a spot to be kept, by default 0.0
    computing : Literal['cpu', 'gpu'], optional
        Whether to use CPU or GPU computation, by default 'cpu'
    """

    def run_workflow(
        computing: Literal['cpu', 'gpu'] = 'cpu',
    ) -> None:
        """
        Runs the STOT workflow with the given parameters.

        Parameters
        ----------
        computing : Literal['cpu', 'gpu'], optional
            Whether to use CPU or GPU computation, by default 'cpu'
        """

        execute_stoat_workflow(
            zarr_path=zarr_path,
            motif_prior=motif_prior,
            ppi_prior=ppi_prior,
            indegrees=indegrees,
            outdegrees=outdegrees,
            min_counts_per_spot=min_counts_per_spot,
            computing=computing,
        )

    if computing == 'gpu':
        gpu_manager = GpuManager()
        with allocate_gpus(gpu_manager, 1) as gpu_id:
            # Only try to import CUDA if we are using GPU computation
            from cupy.cuda import Device

            with Device(gpu_id[0]):
                run_workflow(computing='gpu')
    else:
        run_workflow()

### Main body ###
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-i', '--input', dest='input',
        help='path to the zarr input', metavar='ZARR')
    parser.add_argument('-mp', '--motif-prior', dest='motif_prior',
        help='path to the motif prior', metavar='FILE')
    parser.add_argument('-pp', '--ppi-prior', dest='ppi_prior',
        help='path to the PPI prior', metavar='FILE')
    parser.add_argument('-id', '--indegrees', dest='indegrees',
        help='path to save the indegrees into', metavar='FILE')
    parser.add_argument('-od', '--outdegrees', dest='outdegrees',
        help='path to save the outdegrees into', metavar='FILE')
    parser.add_argument('-mc', '--min_counts', dest='min_counts',
        help='minimum number of counts for a spot to be kept',
        type=float, default=0.0)
    parser.add_argument('-c', '--computing', dest='computing',
        help='platform to use to calculate networks (cpu or gpu)',)

    args = parser.parse_args()

    calculate_spot_degrees(
        zarr_path=args.input,
        motif_prior=args.motif_prior,
        ppi_prior=args.ppi_prior,
        indegrees=args.indegrees,
        outdegrees=args.outdegrees,
        min_counts_per_spot=args.min_counts,
        computing=args.computing,
    )