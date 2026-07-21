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

rule calculate_qc_metrics:
    input:
        script = join('<scripts>', 'calculate_qc_metrics.py'),
        zarr = CONVERTED_ZARR,
    output:
        qc_plot = QC_PLOT,
        joint_qc_plot = JOINT_QC_PLOT,
        data = QC_DATA,
    shell:
        """
        {input.script} \
        -i {input.zarr} \
        -qc {output.qc_plot} \
        -jqc {output.joint_qc_plot} \
        -d {output.data}
        """

sample_df = read_table(join(config['resources'], 'samples_list.tsv'))

rule collate_qc_data:
    input:
        script = join('<scripts>', 'collate_qc_data.py'),
        qc_data = expand(
            QC_DATA,
            zip,
            patient_id=sample_df['patient'],
            slide=sample_df['slide'],
        ),
    output:
        collated = COLLATED_QC_DATA,
    shell:
        """
        {input.script} \
        -qc {input.qc_data} \
        -o {output.collated}
        """

# rule select_best_slides:
