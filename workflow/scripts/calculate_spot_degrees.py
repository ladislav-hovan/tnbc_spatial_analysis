#!/usr/bin/env python

### Imports ###
from os import rmdir
from os.path import join
from pathlib import Path
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
    computing: Literal['cpu', 'gpu'] = 'cpu',
) -> None:

    # Loading
    stoat_obj = Stoat()
    stoat_obj.load_zarr(zarr_path)
    # Filtering
    stoat_obj.filter_genes(drop_deprecated=True, min_counts=1)
    # stoat_obj.filter_spots(min_counts=1000)
    # Averaging
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
    rmdir(output_dir)


def calculate_spot_degrees(
    zarr_path: Path,
    motif_prior: Path,
    ppi_prior: Path,
    indegrees: Path,
    outdegrees: Path,
    computing: Literal['cpu', 'gpu'] = 'cpu',
) -> None:

    def run_workflow(
        computing: Literal['cpu', 'gpu'] = 'cpu',
    ) -> None:
        execute_stoat_workflow(
            zarr_path=zarr_path,
            motif_prior=motif_prior,
            ppi_prior=ppi_prior,
            indegrees=indegrees,
            outdegrees=outdegrees,
            computing=computing,
        )

    if computing == 'gpu':
        gpu_manager = GpuManager()
        with allocate_gpus(gpu_manager, 1) as gpu_id:
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
    parser.add_argument('-c', '--computing', dest='computing',
        help='platform to use to calculate networks (cpu or gpu)',)

    args = parser.parse_args()

    calculate_spot_degrees(
        zarr_path=args.input,
        indegrees=args.indegrees,
        outdegrees=args.outdegrees,
        computing=args.computing,
    )