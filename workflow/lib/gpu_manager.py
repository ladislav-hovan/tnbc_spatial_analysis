# Adapted from code by MuhammedHasan on GitHub
# https://github.com/snakemake/snakemake/issues/281

import random
import time

from collections import Counter
from contextlib import contextmanager
from pathlib import Path
from pytools.persistent_dict import PersistentDict  # Consider persidict
from typing import Generator, Iterable, Optional

class GpuManager:
    """
    Manages GPUs keep track of which GPUs are free and which are
    allocated.
    """

    def __init__(
        self,
        gpus: Optional[Iterable] = None,
        identifier: str = '.gpu_manager',
        container_dir: Path = '.snakemake',
    ):
        """
        Initiates a GPU manager. Stores the values in a persistent
        dictionary with Counter objects, so label duplicates are
        possible.

        Parameters
        ----------
        gpus : Optional[Iterable], optional
            Iterable of GPU IDs to use, can contain duplicates, or None
            to not overwrite currently stored GPU IDs, by default None
        identifier : str, optional
            Identifier for the persistent dictionary,
            by default '.gpu_manager'
        container_dir : Path, optional
            Path to the directory which will contain the dictionary,
            by default '.snakemake'
        """

        self._gpus = PersistentDict(identifier, container_dir=container_dir,
            safe_sync=True)
        if gpus is not None:
            self.free_gpus = Counter(gpus)
            self.allocated_gpus = Counter()
            self.locked = False


    @property
    def free_gpus(
        self,
    ):
        return self._gpus.fetch('free_gpus')


    @free_gpus.setter
    def free_gpus(
        self,
        value: Counter,
    ):
        self._gpus.store('free_gpus', value)


    @property
    def allocated_gpus(
        self,
    ):
        return self._gpus.fetch('allocated_gpus')


    @allocated_gpus.setter
    def allocated_gpus(
        self,
        value: Counter,
    ):
        self._gpus.store('allocated_gpus', value)


    @property
    def locked(
        self,
    ):
        return self._gpus.fetch('locked')


    @locked.setter
    def locked(
        self,
        value: bool,
    ):
        self._gpus.store('locked', value)


    def acquire(
        self,
        num_gpus: int,
    ) -> list:
        """
        Provides the requested number of available GPU labels from the
        managed pool.

        Parameters
        ----------
        num_gpus : int
            The number of GPUs to acquire

        Returns
        -------
        list
            The list of allocated GPU labels

        Raises
        ------
        ValueError
            If the number of GPUs to allocate exceeds the number of
            available GPUs
        """

        while self.locked:
            time.sleep(1)

        self.locked = True

        if self.free_gpus.total() < num_gpus:
            raise ValueError(
                f'Cannot allocate {num_gpus} GPUs,'
                f' only {self.free_gpus.total()} available'
            )

        gpus = random.sample(list(self.free_gpus.keys()), k=num_gpus,
            counts=list(self.free_gpus.values()))

        self.free_gpus = self.free_gpus - Counter(gpus)
        self.allocated_gpus = self.allocated_gpus + Counter(gpus)

        self.locked = False

        return gpus


    def release(
        self,
        gpus: Iterable,
    ):
        """
        Returns the provided GPU labels back to the available pool.

        Parameters
        ----------
        gpus : Iterable
            An Iterable of GPU labels to be made available again
        """

        while self.locked:
            time.sleep(1)

        self.locked = True

        self.free_gpus = self.free_gpus + Counter(gpus)
        self.allocated_gpus = self.allocated_gpus - Counter(gpus)

        self.locked = False


@contextmanager
def allocate_gpus(
    gpu_manager: GpuManager,
    num_gpus: int,
) -> Generator:
    """
    Allocates several GPUs from the GPU manager and releases them when
    done.

    Parameters
    ----------
    gpu_manager : GpuManager
        The GPU manager
    num_gpus : int
        The number of GPUs to allocate

    Yields
    ------
    list
        The list of allocated GPUs
    """

    gpus = gpu_manager.acquire(num_gpus)

    try:
        yield gpus
    finally:
        gpu_manager.release(gpus)