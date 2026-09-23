from pathlib import Path
from time import sleep

compute = 'gpu' if USE_GPU else 'cpu'

rule calculate_spot_degrees:
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
    params:
        min_counts_per_spot = lambda wildcards: wildcards['min_counts'],
    shell:
        """
        {input.script} \
        -i {input.zarr} \
        -mp {input.motif_prior} \
        -pp {input.ppi_prior} \
        -c {compute} \
        -mc {params.min_counts_per_spot} \
        -id {output.indegrees} \
        -od {output.outdegrees}
        """

rule calculate_region_degrees:
    input:
        script = join('<scripts>', 'calculate_region_degrees.py'),
        expression = FN_COLLATED_CLUSTERED_AGG_EXPRESSION,
        motif_prior = MOTIF_PRIOR,
        ppi_prior = PPI_PRIOR,
    output:
        indegrees = REGION_INDEGREES,
        outdegrees = REGION_OUTDEGREES,
    resources:
        gpus = int(USE_GPU),
        threads = 1 if USE_GPU else config['lioness_threads'],
    shell:
        """
        {input.script} \
        -e {input.expression} \
        -mp {input.motif_prior} \
        -pp {input.ppi_prior} \
        -c {compute} \
        -t {resources.threads} \
        -id {output.indegrees} \
        -od {output.outdegrees}
        """

rule calculate_annotated_region_degrees:
    input:
        script = join('<scripts>', 'calculate_region_degrees.py'),
        expression = FN_COLLATED_ANNOTATED_AGG_EXPRESSION,
        motif_prior = MOTIF_PRIOR,
        ppi_prior = PPI_PRIOR,
    output:
        indegrees = ANNOTATED_REGION_INDEGREES,
        outdegrees = ANNOTATED_REGION_OUTDEGREES,
    resources:
        gpus = int(USE_GPU),
        threads = 1 if USE_GPU else config['lioness_threads'],
    shell:
        """
        {input.script} \
        -e {input.expression} \
        -mp {input.motif_prior} \
        -pp {input.ppi_prior} \
        -c {compute} \
        -t {resources.threads} \
        -id {output.indegrees} \
        -od {output.outdegrees}
        """

rule copy_aggregated_expression:
    input:
        expression = ANY_AGG_EXPRESSION,
    output:
        expression = ANY_REGION_EXPRESSION,
    shell:
        """
        cp {input.expression} {output.expression}
        """