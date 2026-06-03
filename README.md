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
This pipeline downloads the Visium data from the original paper,
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
Running a Snakemake pipeline is straightforward:

``` bash
snakemake --cores=10 --resources gpus=1
```

It is assumed that all the input is present and that the settings in the
`config.yaml` file are correct.
Some of the relevant settings are:
- `input_dir`: the directory containing the input files


## Project Status
The project is: _in progress_.


## Room for Improvement
Room for improvement:
- Nothing to improve so far since nothing is implemented

To do:
- Data download
- Preprocessing
- Region assignments
- Network generation
- Downstream analysis


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