# Preprocessing
INPUT_RDS = join('<counts>', 'TNBC{patient_id}.RDS')
CONVERTED_COUNTS = join('<results>', 'converted_feather', '{patient_id}',
    'counts.feather')
CONVERTED_SPOTS = join('<results>', 'converted_feather', '{patient_id}',
    'spots.feather')
CONVERTED_ZARR = directory(join('<results>', 'converted_zarr', '{patient_id}',
    '{slide}.zarr'))