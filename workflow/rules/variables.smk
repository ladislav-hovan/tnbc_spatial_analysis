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

### Network generation ###
# Priors
MOTIF_PRIOR = join('<priors>', 'motif_prior.tsv')
PPI_PRIOR = join('<priors>', 'ppi_prior.tsv')
# Spot-specific
SPOT_DIR = join('<results>', 'networks', 'spot_specific', '{patient_id}',
    '{slide}')
SPOT_INDEGREES = join(SPOT_DIR, 'indegrees.feather')
SPOT_OUTDEGREES = join(SPOT_DIR, 'outdegrees.feather')