### Helper functions ###
def get_difftype(
    metric: str,
) -> str:
    """
    Converts the name of the metric to a difference type.

    Parameters
    ----------
    metric : str
        Name of the metric

    Returns
    -------
    str
        Inferred difference type
    """

    if 'median' in metric:
        return 'median'
    else:
        return 'mean'

def get_x_thresh(
    metric: str,
    modality: str,
) -> float:
    """
    Provides a threshold for the difference significance based
    on the name of the metric and the modality.

    Parameters
    ----------
    metric : str
        Name of the metric
    modality : str
        Modality of the data

    Returns
    -------
    float
        Threshold for the difference
    """

    if metric == 'meandiff':
        return 1.5
    elif metric == 'mediandiff':
        if modality == 'expression':
            return 0.5
        elif modality == 'indegree':
            return 5
        elif modality == 'outdegree':
            return 100
    # "Sensible" default
    return 2

### Rules ###
rule create_mapfile:
    input:
        script = join('<scripts>', 'create_mapfile.py'),
        metadata = METADATA_FILE,
    output:
        mapfile = MAPFILE,
    wildcard_constraints:
        # Doesn't contain any equal signs - that's reserved for restricted
        column = '[a-zA-Z0-9_]+',
    shell:
        """
        {input.script} \
        -m {input.metadata} \
        -c {wildcards.column} \
        -o {output.mapfile}
        """

rule create_restricted_mapfile:
    input:
        script = join('<scripts>', 'create_mapfile.py'),
        metadata = METADATA_FILE,
    output:
        mapfile = RESTRICTED_MAPFILE,
    shell:
        """
        {input.script} \
        -m {input.metadata} \
        -sc {wildcards.select_column} \
        -sv {wildcards.select_value} \
        -c {wildcards.column} \
        -o {output.mapfile}
        """

rule convert_lioness_output:
    input:
        script = join('<scripts>', 'convert_lioness_output.py'),
        lioness_output = LIONESS_OUTPUT,
    output:
        converted_lioness_output = temp(CONVERTED_LIONESS_OUTPUT),
    shell:
        """
        {input.script} \
        -i {input.lioness_output} \
        -o {output.converted_lioness_output}
        """

rule compare_groups:
    input:
        script = join('<scripts>', 'fill_out_template.py'),
        template = join('<templates>', 'compare_template.yaml'),
        data = CONVERTED_LIONESS_OUTPUT,
        mapfile = MAPFILE,
    output:
        config = COMPARE_CONFIG,
        t_comparison = temp(T_COMPARE_FILE),
        t_ranks = temp(T_COMPARE_RANKS),
    params:
        compare_dir = subpath(output.t_ranks, parent=True),
    shell:
        """
        {input.script} \
        -t {input.template} \
        -o {output.config} \
        -s datafile {input.data} \
        -s mapfile {input.mapfile} \
        -s datatype {wildcards.modality} \
        -s groupA {wildcards.groupA} \
        -s groupB {wildcards.groupB} \
        -s test {wildcards.test} \
        -s rank_metric {wildcards.metric} \
        -s output_dir {params.compare_dir}

        sisana compare {output.config}
        """

rule rename_compare_files:
    input:
        t_comparison = T_COMPARE_FILE,
        t_ranks = T_COMPARE_RANKS,
    output:
        comparison = COMPARE_FILE,
        ranks = COMPARE_RANKS,
    params:
        compare_dir = subpath(output.ranks, parent=True),
    shell:
        """
        mv {input.t_comparison} {output.comparison}
        mv {input.t_ranks} {output.ranks}
        """

rule create_volcanoplot:
    input:
        script = join('<scripts>', 'fill_out_template.py'),
        template = join('<templates>', 'volcano_template.yaml'),
        comparison = COMPARE_FILE,
    output:
        config = VOLCANO_CONFIG,
        t_volcano = temp(T_VOLCANO_PLOT),
    params:
        diffcol = lambda wildcards: 'difference_of_'
            f'{get_difftype(wildcards.metric)}s_'
            f'\\({wildcards.groupB}-{wildcards.groupA}\\)',
        x_thresh = lambda wildcards: get_x_thresh(wildcards.metric,
            wildcards.modality),
        difftype = lambda wildcards: get_difftype(wildcards.metric),
        volcano_dir = subpath(output.t_volcano, parent=True),
    shell:
        """
        {input.script} \
        -t {input.template} \
        -o {output.config} \
        -s statsfile {input.comparison} \
        -s diffcol {params.diffcol} \
        -s x_thresh {params.x_thresh} \
        -s pval_thresh {wildcards.pval} \
        -s difftype {params.difftype} \
        -s output_dir {params.volcano_dir}

        sisana visualize volcano {output.config} || touch {output.t_volcano}
        """

rule rename_volcano_plot:
    input:
        t_volcano = T_VOLCANO_PLOT,
    output:
        volcano = VOLCANO_PLOT,
    params:
        volcano_dir = subpath(output.volcano, parent=True),
    shell:
        """
        mv {input.t_volcano} {output.volcano}
        """