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
        zarr = directory(CONVERTED_ZARR),
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
        data = temp(QC_DATA),
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

checkpoint select_best_slides:
    input:
        script = join('<scripts>', 'select_best_slides.py'),
        qc = COLLATED_QC_DATA,
    output:
        mapping = BEST_SLIDES,
    shell:
        """
        {input.script} \
        -i {input.qc} \
        -o {output.mapping}
        """

rule cluster_and_aggregate_expression:
    input:
        script = join('<scripts>', 'cluster_and_aggregate_expression.py'),
        zarr = CONVERTED_ZARR,
    output:
        aggregated_expression = CLUSTERED_AGG_EXPRESSION,
        classification = CLUSTERED_CLASSIFICATION,
    params:
        min_counts_per_spot = lambda wildcards: wildcards['min_counts'],
        resolution = lambda wildcards: wildcards['resolution'],
    shell:
        """
        {input.script} \
        -i {input.zarr} \
        -mc {params.min_counts_per_spot} \
        -r {params.resolution} \
        -cp {output.classification} \
        -ep {output.aggregated_expression}
        """

def get_selected_expr_data(wc):
    with checkpoints.select_best_slides.get().output['mapping'].open() as f:
        df = read_table(f)
        return expand(
            CLUSTERED_AGG_EXPRESSION_ALT,
            zip,
            patient_id=df['patient_id'],
            slide=df[config['slide_selection']],
        )

rule collate_agg_expression_data:
    input:
        script = join('<scripts>', 'collate_agg_expression_data.py'),
        agg_expr_files = get_selected_expr_data,
    output:
        collated = COLLATED_CLUSTERED_AGG_EXPRESSION,
    shell:
        """
        {input.script} \
        -ef {input.agg_expr_files} \
        -o {output.collated} \
        -pi -3 \
        -si -2
        """

rule filter_and_normalise_expression:
    input:
        script = join('<scripts>', 'filter_and_normalise_expression.py'),
        collated_expr = COLLATED_CLUSTERED_AGG_EXPRESSION,
    output:
        filtered_expr = FN_COLLATED_CLUSTERED_AGG_EXPRESSION,
    params:
        ratio_threshold = lambda wildcards: wildcards['ratio_threshold'],
    shell:
        """
        {input.script} \
        -i {input.collated_expr} \
        -o {output.filtered_expr} \
        -rt {params.ratio_threshold}
        """

rule annotate_and_aggregate_expression:
    input:
        script = join('<scripts>', 'annotate_and_aggregate_expression.py'),
        zarr = CONVERTED_ZARR,
        classification = ANNOTATED_CLASSIFICATION,
    output:
        aggregated_expression = ANNOTATED_AGG_EXPRESSION,
    params:
        min_counts_per_spot = lambda wildcards: wildcards['min_counts'],
    shell:
        """
        {input.script} \
        -i {input.zarr} \
        -mc {params.min_counts_per_spot} \
        -cp {input.classification} \
        -ep {output.aggregated_expression}
        """

def get_selected_annotated_expr_data(wc):
    with checkpoints.select_best_slides.get().output['mapping'].open() as f:
        df = read_table(f)
        return expand(
            ANNOTATED_AGG_EXPRESSION_ALT,
            zip,
            patient_id=df['patient_id'],
            slide=df[config['slide_selection']],
        )

rule collate_agg_annotated_expression_data:
    input:
        script = join('<scripts>', 'collate_agg_expression_data.py'),
        agg_expr_files = get_selected_annotated_expr_data,
    output:
        collated = COLLATED_ANNOTATED_AGG_EXPRESSION,
    shell:
        """
        {input.script} \
        -ef {input.agg_expr_files} \
        -o {output.collated} \
        -pi -3 \
        -si -2
        """

rule filter_and_normalise_annotated_expression:
    input:
        script = join('<scripts>', 'filter_and_normalise_expression.py'),
        collated_expr = COLLATED_ANNOTATED_AGG_EXPRESSION,
    output:
        filtered_expr = FN_COLLATED_ANNOTATED_AGG_EXPRESSION,
    params:
        ratio_threshold = lambda wildcards: wildcards['ratio_threshold'],
    shell:
        """
        {input.script} \
        -i {input.collated_expr} \
        -o {output.filtered_expr} \
        -rt {params.ratio_threshold}
        """

rule create_region_metadata:
    input:
        script = join('<scripts>', 'create_region_metadata.py'),
        expression = FN_COLLATED_ANNOTATED_AGG_EXPRESSION,
    output:
        metadata = METADATA_FILE,
    shell:
        """
        {input.script} \
        -e {input.expression} \
        -m {output.metadata}
        """

rule process_spot_classification:
    input:
        script = join('<scripts>', 'process_spot_classification.R'),
        all_classes = ALL_ANNOTATIONS,
    output:
        # This ensures that the directory gets created
        output_dir = directory(subpath(ANNOTATED_CLASSIFICATION, ancestor=3)),
        classification_files = expand(
            ANNOTATED_CLASSIFICATION,
            zip,
            patient_id=sample_df['patient'],
            slide=sample_df['slide'],
        ),
    shell:
        """
        {input.script} \
        -i {input.all_classes} \
        -od {output.output_dir}
        """