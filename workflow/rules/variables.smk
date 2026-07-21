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