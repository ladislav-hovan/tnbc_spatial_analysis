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
    '{patient_id}', '{slide}', 'min_{min_counts}_counts',
    'resolution_{resolution}')
CLUSTERED_AGG_EXPRESSION = join(CLUSTERED_DIR, 'agg_expression.feather')
CLUSTERED_AGG_EXPRESSION_ALT = join('<results>', 'agg_expression', 'clustered',
    '{patient_id}', '{slide}', 'min_{{min_counts}}_counts',
    'resolution_{{resolution}}', 'agg_expression.feather')
CLUSTERED_CLASSIFICATION = join(CLUSTERED_DIR, 'classification.feather')
COLLATED_CLUSTERED_AGG_EXPRESSION = join('<results>', 'agg_expression',
    'clustered', 'collated_agg_expression_mc_{min_counts}_r_{resolution}'
    '.feather')
FN_COLLATED_CLUSTERED_AGG_EXPRESSION = join('<results>', 'agg_expression',
    'clustered', 'fn_collated_agg_expression_mc_{min_counts}_'
    'r_{resolution}_rt_{ratio_threshold}.feather')

### Network generation ###
# Priors
MOTIF_PRIOR = join('<priors>', 'motif_prior.tsv')
PPI_PRIOR = join('<priors>', 'ppi_prior.tsv')
# Spot-specific
SPOT_DIR = join('<results>', 'networks', 'spot_specific', '{patient_id}',
    '{slide}', 'min_{min_counts}_counts')
SPOT_INDEGREES = join(SPOT_DIR, 'indegrees.feather')
SPOT_INDEGREES_ALT = join('<results>', 'networks', 'spot_specific',
    '{patient_id}', '{slide}', 'min_{{min_counts}}_counts',
    'indegrees.feather')
SPOT_OUTDEGREES = join(SPOT_DIR, 'outdegrees.feather')
# Region-specific
REGION_DIR = join('<results>', 'networks', 'region_specific',
    'min_{min_counts}_counts', 'resolution_{resolution}',
    'ratio_threshold_{ratio_threshold}')
REGION_INDEGREES = join(REGION_DIR, 'indegrees.feather')
REGION_OUTDEGREES = join(REGION_DIR, 'outdegrees.feather')
