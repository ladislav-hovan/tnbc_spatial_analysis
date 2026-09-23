### Preprocessing ###
# Format conversion
INPUT_RDS = join('<counts>', 'TNBC{patient_id}.RDS')
CONVERTED_COUNTS = join('<results>', 'converted_feather', '{patient_id}',
    'counts.feather')
CONVERTED_SPOTS = join('<results>', 'converted_feather', '{patient_id}',
    'spots.feather')
CONVERTED_ZARR = join('<results>', 'converted_zarr', '{patient_id}',
    '{slide}.zarr')
# Quality control
QC_PLOT = join('<results>', 'qc', '{patient_id}', '{slide}', 'qc_plot.png')
JOINT_QC_PLOT = join('<results>', 'qc', '{patient_id}', '{slide}',
    'joint_qc_plot.png')
QC_DATA = join('<results>', 'qc', '{patient_id}', '{slide}', 'data.tsv')
COLLATED_QC_DATA = join('<results>', 'qc', 'collated_data.tsv')
BEST_SLIDES = join('<results>', 'qc', 'best_slides.tsv')
# Expression clustering
CLUSTERED_DIR =  join('<results>', 'agg_expression', 'clustered',
    'min_{min_counts}_counts', 'resolution_{resolution}')
CLUSTERED_AGG_EXPRESSION = join(CLUSTERED_DIR, '{patient_id}', '{slide}',
    'agg_expression.feather')
CLUSTERED_AGG_EXPRESSION_ALT = join('<results>', 'agg_expression', 'clustered',
    'min_{{min_counts}}_counts', 'resolution_{{resolution}}', '{patient_id}',
    '{slide}', 'agg_expression.feather')
CLUSTERED_CLASSIFICATION = join(CLUSTERED_DIR, '{patient_id}', '{slide}',
    'classification.feather')
COLLATED_CLUSTERED_AGG_EXPRESSION = join(CLUSTERED_DIR,
    'collated_agg_expression.feather')
FN_COLLATED_CLUSTERED_AGG_EXPRESSION = join(CLUSTERED_DIR,
    'ratio_threshold_{ratio_threshold}', 'fn_collated_agg_expression.feather')
# Cluster annotation from reference
ANNOTATED_DIR = join('<results>', 'agg_expression', 'annotated',
    'min_{min_counts}_counts')
ANNOTATED_AGG_EXPRESSION = join(ANNOTATED_DIR, '{patient_id}', '{slide}',
    'agg_expression.feather')
ANNOTATED_AGG_EXPRESSION_ALT = join('<results>', 'agg_expression', 'annotated',
    'min_{{min_counts}}_counts', '{patient_id}', '{slide}',
    'agg_expression.feather')
ANNOTATED_CLASSIFICATION = join('<results>', 'classification', 'original', 
    '{patient_id}', '{slide}', 'classification.feather')
COLLATED_ANNOTATED_AGG_EXPRESSION = join(ANNOTATED_DIR,
    'collated_agg_expression.feather')
FN_COLLATED_ANNOTATED_AGG_EXPRESSION = join(ANNOTATED_DIR,
    'ratio_threshold_{ratio_threshold}', 'fn_collated_agg_expression.feather')

### Network generation ###
# Priors
MOTIF_PRIOR = join('<priors>', 'motif_prior.tsv')
PPI_PRIOR = join('<priors>', 'ppi_prior.tsv')
# Spot-specific
SPOT_DIR = join('<results>', 'networks', 'spot_specific',
    'min_{min_counts}_counts', '{patient_id}', '{slide}')
SPOT_INDEGREES = join(SPOT_DIR, 'indegrees.feather')
SPOT_INDEGREES_ALT = join('<results>', 'networks', 'spot_specific',
    'min_{{min_counts}}_counts', '{patient_id}', '{slide}',
    'indegrees.feather')
SPOT_OUTDEGREES = join(SPOT_DIR, 'outdegrees.feather')
# Region-specific
REGION_DIR = join('<results>', 'networks', 'region_specific', 'clustered',
    'min_{min_counts}_counts', 'resolution_{resolution}',
    'ratio_threshold_{ratio_threshold}')
REGION_EXPRESSION = join(REGION_DIR, 'expression.feather')
REGION_INDEGREES = join(REGION_DIR, 'indegrees.feather')
REGION_OUTDEGREES = join(REGION_DIR, 'outdegrees.feather')
# Annotated region-specific
ANNOTATED_REGION_DIR = join('<results>', 'networks', 'region_specific',
    'annotated', 'min_{min_counts}_counts',
    'ratio_threshold_{ratio_threshold}')
ANNOTATED_REGION_INDEGREES = join(ANNOTATED_REGION_DIR, 'indegrees.feather')
ANNOTATED_REGION_OUTDEGREES = join(ANNOTATED_REGION_DIR, 'outdegrees.feather')
# Copying expression
ANY_AGG_EXPRESSION = join('<results>', 'agg_expression', '{agg_type}',
    '{specification}', 'fn_collated_agg_expression.feather')
ANY_REGION_EXPRESSION = join('<results>', 'networks', 'region_specific',
    '{agg_type}', '{specification}', 'expression.feather')

### Limma comparison ###
METADATA_FILE = join(ANNOTATED_DIR, 'ratio_threshold_{ratio_threshold}',
    'fn_collated_metadata.tsv')
TARGETS_FILE = join('<results>', 'limma', 'min_{min_counts}_counts',
    'ratio_threshold_{ratio_threshold}', '{pairing}', '{column}',
    'targets.tsv')
RESTRICTED_TARGETS_FILE = join('<results>', 'limma', 'min_{min_counts}_counts',
    'ratio_threshold_{ratio_threshold}', '{pairing}',
    '{select_column}={select_value}__{column}', 'targets.tsv')
LIONESS_OUTPUT = join(ANNOTATED_REGION_DIR, '{modality}.feather')
LIMMA_DIR = join('<results>', 'limma', 'min_{min_counts}_counts',
    'ratio_threshold_{ratio_threshold}', '{pairing}', '{column}',
    '{groupA}_{groupB}')

### Limma GSEA ###
LIMMA_GSEA_DIR = join(LIMMA_DIR, '{modality}', 'gsea', '{geneset_name}')
LIMMA_GSEA_CONFIG = join(LIMMA_GSEA_DIR, 'config.yaml')
T_LIMMA_GSEA_RESULTS = join(LIMMA_GSEA_DIR, 'comparison_prerank_GSEA_'
    '{geneset_name}_results.txt')
LIMMA_GSEA_RESULTS = join(LIMMA_GSEA_DIR, 'GSEA_results.txt')
T_LIMMA_GSEA_ENRICHMENT = join(LIMMA_GSEA_DIR, 'comparison_GSEA_{geneset_name}'
    '_basic_enrichment_plot.png')
LIMMA_GSEA_ENRICHMENT = join(LIMMA_GSEA_DIR, 'enrichment_plot.png')
T_LIMMA_GSEA_DOTPLOT = join(LIMMA_GSEA_DIR, 'comparison_GSEA_{geneset_name}'
    '_basic_enrichment_dotplot.png')
LIMMA_GSEA_DOTPLOT = join(LIMMA_GSEA_DIR, 'dotplot.png')