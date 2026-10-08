### Imports ###
from lib.helper_functions import get_difftype, get_x_thresh

### Rules ###
rule create_targets_file:
    input:
        script = join('<scripts>', 'create_targets_file.py'),
        metadata = METADATA_FILE,
    output:
        targets_file = TARGETS_FILE,
    wildcard_constraints:
        # Doesn't contain any equal signs - that's reserved for restricted
        column = '[a-zA-Z0-9_]+',
    shell:
        """
        {input.script} \
        -m {input.metadata} \
        -p {wildcards.pairing} \
        -c {wildcards.column} \
        -o {output.targets_file}
        """

rule create_restricted_targets_file:
    input:
        script = join('<scripts>', 'create_targets_file.py'),
        metadata = METADATA_FILE,
    output:
        targets_file = RESTRICTED_TARGETS_FILE,
    shell:
        """
        {input.script} \
        -m {input.metadata} \
        -p {wildcards.pairing} \
        -sc {wildcards.select_column} \
        -sv {wildcards.select_value} \
        -c {wildcards.column} \
        -o {output.targets_file}
        """

rule run_limma:
    input:
        script = join('<scripts>', 'run_limma.R'),
        data_file = LIONESS_OUTPUT,
        targets_file = TARGETS_FILE,
    output:
        limma_results = LIMMA_RESULTS,
    shell:
        """
        {input.script} \
        -d {input.data_file} \
        -t {input.targets_file} \
        -ga {wildcards.groupA} \
        -gb {wildcards.groupB} \
        -o {output.limma_results}
        """

rule create_limma_rankfile:
    input:
        limma_results = LIMMA_RESULTS,
    output:
        limma_ranks = LIMMA_RANKS,
    run:
        import pandas as pd

        data = pd.read_table(input['limma_results'], index_col=0)
        data['t'].sort_values(ascending=False).to_csv(output['limma_ranks'],
            sep='\t', header=False)

rule run_gsea_on_limma:
    input:
        script = join('<scripts>', 'fill_out_template.py'),
        template = join('<templates>', 'gsea_template.yaml'),
        ranks = LIMMA_RANKS,
        gmt_file = lambda wildcards: config['gene_sets'].get(
            wildcards.geneset_name),
    output:
        config = LIMMA_GSEA_CONFIG,
        t_gsea = temp(T_LIMMA_GSEA_RESULTS),
        t_enrich_plot = temp(T_LIMMA_GSEA_ENRICHMENT),
        t_dotplot = temp(T_LIMMA_GSEA_DOTPLOT),
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

rule rename_limma_gsea_files:
    input:
        t_gsea = T_LIMMA_GSEA_RESULTS,
        t_enrich_plot = T_LIMMA_GSEA_ENRICHMENT,
        t_dotplot = T_LIMMA_GSEA_DOTPLOT,
    output:
        gsea = LIMMA_GSEA_RESULTS,
        enrich_plot = LIMMA_GSEA_ENRICHMENT,
        dotplot = LIMMA_GSEA_DOTPLOT,
    params:
        gsea_dir = subpath(output.gsea, parent=True),
    shell:
        """
        mv {input.t_gsea} {output.gsea}
        mv {input.t_enrich_plot} {output.enrich_plot}
        mv {input.t_dotplot} {output.dotplot}
        """

rule convert_limma_results_for_volcano_plot:
    input:
        script = join('<scripts>',
            'convert_limma_results_for_volcano_plot.py'),
        results = LIMMA_RESULTS,
    output:
        adjusted_results = join(LIMMA_DIR, '{modality}',
            'results_volcano.tsv'),
    shell:
        """
        {input.script} \
        -i {input.results} \
        -m logFC "logFC_({wildcards.groupB}-{wildcards.groupA})" \
        -o {output.adjusted_results}
        """

rule create_limma_volcano_plot:
    input:
        script = join('<scripts>', 'fill_out_template.py'),
        template = join('<templates>', 'volcano_template.yaml'),
        comparison = LIMMA_VOLCANO_RESULTS,
    output:
        config = LIMMA_VOLCANO_CONFIG,
        t_volcano = temp(T_LIMMA_VOLCANO_PLOT),
    conda:
        join('..', 'envs', 'sisana_env.yaml')
    params:
        diffcol = (lambda wildcards: f'logFC_({wildcards.groupB}-'
            f'{wildcards.groupA})'),
        volcano_dir = subpath(output.t_volcano, parent=True),
    shell:
        """
        {input.script} \
        -t {input.template} \
        -o {output.config} \
        -s statsfile {input.comparison} \
        -s diffcol "{params.diffcol}" \
        -s groupA {wildcards.groupA} \
        -s groupB {wildcards.groupB} \
        -s adjpcol adj.P.Val \
        -s x_thresh 1.5 \
        -s pval_thresh {wildcards.pval} \
        -s difftype median \
        -s output_dir {params.volcano_dir}

        sisana visualize volcano {output.config} || touch {output.t_volcano}
        """

rule rename_limma_volcano_plot:
    input:
        t_volcano = T_LIMMA_VOLCANO_PLOT,
    output:
        volcano = LIMMA_VOLCANO_PLOT,
    params:
        volcano_dir = subpath(output.volcano, parent=True),
    shell:
        """
        mv {input.t_volcano} {output.volcano}
        """