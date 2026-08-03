from pathlib import Path
from time import sleep

compute = 'gpu' if USE_GPU else 'cpu'

rule calculate_spot_indegrees:
    input:
        script = join('<scripts>', 'calculate_spot_degrees.py'),
        zarr = CONVERTED_ZARR,
        motif_prior = MOTIF_PRIOR,
        ppi_prior = PPI_PRIOR,
    output:
        indegrees = SPOT_INDEGREES,
        outdegrees = SPOT_OUTDEGREES,
    resources:
        gpus = int(USE_GPU),
    shell:
        """
        {input.script} \
        -i {input.zarr} \
        -mp {input.motif_prior} \
        -pp {input.ppi_prior} \
        -c {compute} \
        -id {output.indegrees} \
        -od {output.outdegrees}
        """