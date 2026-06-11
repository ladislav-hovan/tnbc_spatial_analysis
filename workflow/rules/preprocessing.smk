rule convert_count_format:
    input:
        script = join('<scripts>', 'convert_count_format.R'),
        file = INPUT_RDS,
    output:
        counts = CONVERTED_COUNTS,
        spots = CONVERTED_SPOTS,
    shell:
        """
        {input.script} \
        -i {input.file} \
        -oc {output.counts} \
        -os {output.spots}
        """

rule convert_feather_to_zarr:
    input:
        script = join('<scripts>', 'convert_feather_to_zarr.py'),
        counts = CONVERTED_COUNTS,
        spots = CONVERTED_SPOTS,
    output:
        zarr = CONVERTED_ZARR,
    params:
        zarr_dir = subpath(output.zarr, parent=True),
    shell:
        """
        {input.script} \
        -c {input.counts} \
        -s {input.spots} \
        -sl {wildcards.slide} \
        -od {params.zarr_dir}
        """