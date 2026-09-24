# TNBC spatial analysis pipeline
This Snakemake pipeline analyzes the spatial data from a triple-negative
breast cancer (TNBC) 10x Visium
[dataset](https://zenodo.org/records/14204217).
It uses
[STOAT](https://github.com/ladislav-hovan/stoat)
to generate spatially resolved gene regulatory networks.


## Table of Contents
- [TNBC spatial analysis pipeline](#tnbc-spatial-analysis-pipeline)
  - [Table of Contents](#table-of-contents)
  - [General Information](#general-information)
  - [Features](#features)
  - [Setup](#setup)
  - [Usage](#usage)
  - [Project Status](#project-status)
  - [Room for Improvement](#room-for-improvement)
  - [Acknowledgements](#acknowledgements)
  - [Contact](#contact)
  - [License](#license)


## General Information
This pipeline downloads the ST data from the original paper,
preprocesses it to make it compatible with STOAT and generates
spatially resolved gene regulatory networks.
It also does the downstream analysis.

The entire pipeline is implemented using Snakemake.
It will utilise a GPU to compute networks when available, but can also
use CPUs only.


## Features
The features already available are:
- None so far


## Setup
The requirements are provided in a `requirements.txt` file.


## Usage
Running this Snakemake pipeline is straightforward:

``` bash
pixi run gpu-snakemake --cores=10 --resources gpus=1 --sdm conda
```

Invoking the `snakemake` command like this will use the provided pixi
environment.
However, it is still possible to use a local snakemake installation,
assuming all the dependencies are installed.

The `--sdm conda` selects conda as the dependency manager.
It is not necessary to have conda installed separately as the pixi
environment contains it.

It is assumed that all the input is present and that the settings in the
`config.yaml` file are correct.
Some of the relevant settings are:
- `slide_selection`: the metric to select the best slide for each
patient
- `gpu_ids`: the IDs of GPUs available for calculation
- `filter_ratio_threshold`: the ratio of samples a gene has to be
expressed in to be kept


## Project Status
The project is: _in progress_.


## Room for Improvement
Room for improvement:
- Some code duplication to be removed if possible
- Support for more clustering approaches
- Automated annotation of clusters

To do:
- Data download instead of provided files
- More downstream analysis


## Acknowledgements
Many thanks to the members of the
[Kuijjer group](https://www.kuijjerlab.org/)
at NCMBM/UH for their feedback and support.

This README is based on a template made by
[@flynerdpl](https://www.flynerd.pl/).


## Contact
Created by Ladislav Hovan (ladislav.hovan@ncmbm.uio.no).
Feel free to contact me!


## License
This project is open source and available under the
[GNU General Public License v3](LICENSE).