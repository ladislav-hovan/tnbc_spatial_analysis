#!/usr/bin/env python

### Imports ###
import numpy as np
import pandas as pd

from netZooPy.lioness import Lioness
from netZooPy.panda import Panda
from os import remove
from os.path import join, split
from pathlib import Path
from stoat.modules.utils import save_df_into_filelike
from typing import Literal

from gpu_manager import GpuManager, allocate_gpus

### Functions ###
def execute_lioness_workflow(
    expression_path: Path,
    motif_prior: Path,
    ppi_prior: Path,
    indegrees: Path,
    outdegrees: Path,
    computing: Literal['cpu', 'gpu'] = 'cpu',
    threads: int = 1,
) -> None:
    """
    Executes the LIONESS workflow to reconstruct gene regulatory
    networks and calculates indegrees and outdegrees afterwards.

    Parameters
    ----------
    expression_path : Path
        Path to the expression data file
    motif_prior : Path
        Path to the motif prior file
    ppi_prior : Path
        Path to the PPI prior file
    indegrees : Path
        Path to save the indegrees into
    outdegrees : Path
        Path to save the outdegrees into
    computing : Literal['cpu', 'gpu'], optional
        Whether to use CPU or GPU computation, by default 'cpu'
    threads : int, optional
        Number of threads to use for CPU computation, by default 1
    """

    output_dir = split(indegrees)[0]
    # Run LIONESS
    expr_df = pd.read_feather(expression_path).set_index('index')
    panda_obj = Panda(expr_df, motif_prior, ppi_prior,
        computing=computing, save_memory=False, keep_expression_matrix=True,
        modeProcess='intersection')
    _ = Lioness(panda_obj, computing=computing, save_dir=output_dir,
        save_fmt='npy', ncores=threads)
    # Convert the generated .npy file to .feather with the right index
    tfs = panda_obj.tfs
    genes = panda_obj.genes
    mi = pd.MultiIndex.from_product([genes, tfs], names=['gene', 'tf']
        ).swaplevel()
    npy_path = join(output_dir, 'lioness.npy')
    data = np.load(npy_path)
    df = pd.DataFrame(data, index=mi)
    df.columns = expr_df.columns
    s_df = df.sort_index()
    # Remove the superfluous .npy file
    remove(npy_path)
    # Calculate degrees
    in_df = s_df.groupby('gene').sum()
    out_df = s_df.groupby('tf').sum()
    # Save the results
    save_df_into_filelike(in_df, indegrees, 'feather')
    save_df_into_filelike(out_df, outdegrees, 'feather')


def calculate_region_degrees(
    expression_path: Path,
    motif_prior: Path,
    ppi_prior: Path,
    indegrees: Path,
    outdegrees: Path,
    computing: Literal['cpu', 'gpu'] = 'cpu',
    threads: int = 1,
) -> None:
    """
    Calculates the indegrees and outdegrees of the gene regulatory
    networks from the given expression data and priors. Uses the
    LIONESS algorithm to reconstruct the networks.

    Parameters
    ----------
    expression_path : Path
        Path to the expression data file
    motif_prior : Path
        Path to the motif prior file
    ppi_prior : Path
        Path to the PPI prior file
    indegrees : Path
        Path to save the indegrees into
    outdegrees : Path
        Path to save the outdegrees into
    computing : Literal['cpu', 'gpu'], optional
        Whether to use CPU or GPU computation, by default 'cpu'
    threads : int, optional
        Number of threads to use for CPU computation, by default 1
    """

    def run_workflow(
        computing: Literal['cpu', 'gpu'] = 'cpu',
        threads: int = 1,
    ) -> None:
        """
        Runs the LIONESS workflow with the given parameters.

        Parameters
        ----------
        computing : Literal['cpu', 'gpu'], optional
            Whether to use CPU or GPU computation, by default 'cpu'
        threads : int, optional
            Number of threads to use for CPU computation, by default 1
        """

        execute_lioness_workflow(
            expression_path=expression_path,
            motif_prior=motif_prior,
            ppi_prior=ppi_prior,
            indegrees=indegrees,
            outdegrees=outdegrees,
            computing=computing,
            threads=threads,
        )

    if computing == 'gpu':
        gpu_manager = GpuManager()
        with allocate_gpus(gpu_manager, 1) as gpu_id:
            # Only try to import CUDA if we are using GPU computation
            from cupy.cuda import Device

            with Device(gpu_id[0]):
                run_workflow(computing='gpu')
    else:
        run_workflow(threads=threads)

### Main body ###
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-e', '--expression', dest='expression',
        help='path to the expression file', metavar='FILE')
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
    parser.add_argument('-t', '--threads', dest='threads',
        help='number of threads to use for CPU computation', type=int,
        default=1)

    args = parser.parse_args()

    calculate_region_degrees(
        expression_path=args.expression,
        motif_prior=args.motif_prior,
        ppi_prior=args.ppi_prior,
        indegrees=args.indegrees,
        outdegrees=args.outdegrees,
        computing=args.computing,
        threads=args.threads,
    )