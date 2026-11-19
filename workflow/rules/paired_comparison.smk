### Imports ###
from lib.helper_functions import get_x_thresh

### Rules ###
rule create_paired_files:
    input:
        script = join('<scripts>', 'create_paired_files.py'),
        metadata = METADATA_FILE,
    output:
        mapfile = PAIRED_MAPFILE,
        adjustment = ADJUSTMENT_FILE,
    wildcard_constraints:
        # Doesn't contain any equal signs - that's reserved for restricted
        pairing = '[^=]+',
    shell:
        """
        {input.script} \
        -m {input.metadata} \
        -p {wildcards.pairing} \
        -c {wildcards.column} \
        -ga {wildcards.groupA} \
        -gb {wildcards.groupB} \
        -om {output.mapfile} \
        -oa {output.adjustment}
        """

rule create_restricted_paired_files:
    input:
        script = join('<scripts>', 'create_paired_files.py'),
        metadata = METADATA_FILE,
    output:
        mapfile = RESTRICTED_PAIRED_MAPFILE,
        adjustment = RESTRICTED_ADJUSTMENT_FILE,
    shell:
        """
        {input.script} \
        -m {input.metadata} \
        -sc {wildcards.select_column} \
        -sv {wildcards.select_value} \
        -p {wildcards.pairing} \
        -c {wildcards.column} \
        -ga {wildcards.groupA} \
        -gb {wildcards.groupB} \
        -om {output.mapfile} \
        -oa {output.adjustment}
        """

rule adjust_lioness_output_for_paired:
    input:
        script = join('<scripts>', 'adjust_lioness_output_for_paired.py'),
        lioness_output = LIONESS_OUTPUT,
        adjustment = ADJUSTMENT_FILE,
    output:
        adjusted_lioness = ADJUSTED_LIONESS_OUTPUT,
    shell:
        """
        {input.script} \
        -il {input.lioness_output} \
        -ia {input.adjustment} \
        -o {output.adjusted_lioness}
        """

rule compare_paired_groups:
    input:
        script = join('<scripts>', 'fill_out_template.py'),
        template = join('<templates>', 'compare_template.yaml'),
        data = ADJUSTED_LIONESS_OUTPUT,
        mapfile = PAIRED_MAPFILE,
    output:
        config = PAIRED_COMPARE_CONFIG,
        t_comparison = temp(T_PAIRED_COMPARE_FILE),
        t_ranks = temp(T_PAIRED_COMPARE_RANKS),
    conda:
        join('..', 'envs', 'sisana_env.yaml')
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
        -s rank_metric mediandiff \
        -s output_dir {params.compare_dir}

        sisana compare {output.config}
        """

rule rename_paired_compare_files:
    input:
        t_comparison = T_PAIRED_COMPARE_FILE,
        t_ranks = T_PAIRED_COMPARE_RANKS,
    output:
        comparison = PAIRED_COMPARE_FILE,
        ranks = PAIRED_COMPARE_RANKS,
    params:
        compare_dir = subpath(output.ranks, parent=True),
    shell:
        """
        mv {input.t_comparison} {output.comparison}
        mv {input.t_ranks} {output.ranks}
        """

rule create_paired_volcanoplot:
    input:
        script = join('<scripts>', 'fill_out_template.py'),
        template = join('<templates>', 'volcano_template.yaml'),
        comparison = PAIRED_COMPARE_FILE,
    output:
        config = PAIRED_VOLCANO_CONFIG,
        t_volcano = temp(T_PAIRED_VOLCANO_PLOT),
    conda:
        join('..', 'envs', 'sisana_env.yaml')
    params:
        diffcol = lambda wildcards: 'difference_of_medians_'
            f'\\({wildcards.groupB}-{wildcards.groupA}\\)',
        x_thresh = lambda wildcards: get_x_thresh('mediandiff',
            wildcards.modality),
        volcano_dir = subpath(output.t_volcano, parent=True),
    shell:
        """
        {input.script} \
        -t {input.template} \
        -o {output.config} \
        -s statsfile {input.comparison} \
        -s diffcol {params.diffcol} \
        -s groupA {wildcards.groupA} \
        -s groupB {wildcards.groupB} \
        -s adjpcol FDR \
        -s x_thresh {params.x_thresh} \
        -s pval_thresh {wildcards.pval} \
        -s difftype mediandiff \
        -s output_dir {params.volcano_dir}

        sisana visualize volcano {output.config} || touch {output.t_volcano}
        """

rule rename_paired_volcano_plot:
    input:
        t_volcano = T_PAIRED_VOLCANO_PLOT,
    output:
        volcano = PAIRED_VOLCANO_PLOT,
    params:
        volcano_dir = subpath(output.volcano, parent=True),
    shell:
        """
        mv {input.t_volcano} {output.volcano}
        """

rule run_gsea_on_paired:
    input:
        script = join('<scripts>', 'fill_out_template.py'),
        template = join('<templates>', 'gsea_template.yaml'),
        ranks = PAIRED_COMPARE_RANKS,
        gmt_file = lambda wildcards: config['gene_sets'].get(
            wildcards.geneset_name),
    output:
        config = PAIRED_GSEA_CONFIG,
        t_gsea = temp(T_PAIRED_GSEA_RESULTS),
        t_enrich_plot = temp(T_PAIRED_GSEA_ENRICHMENT),
        t_dotplot = temp(T_PAIRED_GSEA_DOTPLOT),
    conda:
        join('..', 'envs', 'sisana_env.yaml')
    params:
        gsea_dir = subpath(output.t_gsea, parent=True),
    shell:
        """
        {input.script} \
        -t {input.template} \
        -o {output.config} \
        -s genefile {input.ranks} \
        -s gmtfile {input.gmt_file} \
        -s geneset_name {wildcards.geneset_name} \
        -s output_dir {params.gsea_dir}

        sisana gsea {output.config} || touch {output.t_dotplot}

        cd {params.gsea_dir}
        rm -rf prerank
        rm -f *.log
        rm -f gene_sets.gmt
        rm -f prerank_data.rnk
        """

rule rename_paired_gsea_files:
    input:
        t_gsea = T_PAIRED_GSEA_RESULTS,
        t_enrich_plot = T_PAIRED_GSEA_ENRICHMENT,
        t_dotplot = T_PAIRED_GSEA_DOTPLOT,
    output:
        gsea = PAIRED_GSEA_RESULTS,
        enrich_plot = PAIRED_GSEA_ENRICHMENT,
        dotplot = PAIRED_GSEA_DOTPLOT,
    params:
        gsea_dir = subpath(output.gsea, parent=True),
    shell:
        """
        mv {input.t_gsea} {output.gsea}
        mv {input.t_enrich_plot} {output.enrich_plot}
        mv {input.t_dotplot} {output.dotplot}
        """