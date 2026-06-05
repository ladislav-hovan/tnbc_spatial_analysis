rule convert_count_format:
    input:
        script = join('<scripts>', 'convert_count_format.R'),
        file = join('<counts>', 'TNBC{patient_id}.RDS'),
    output:
        counts = join('<results>', 'converted_feather', '{patient_id}',
            'counts.feather'),
        spots = join('<results>', 'converted_feather', '{patient_id}',
            'spots.feather'),
    shell:
        """
        {input.script} \
        {input.file} \
        {output.counts} \
        {output.spots}
        """

# rule convert_feather_to_zarr:
#     input:
#         script = join('<scripts>', 'convert_count_format.R'),
#         counts = join('<results>', 'converted_feather', '{patient_id}',
#             'counts.feather'),
#         spots = join('<results>', 'converted_feather', '{patient_id}',
#             'spots.feather'),
#     output:

#     shell:
#         """
#         {input.script} \
#         -ic {input.counts} \
#         -is {input.spots} \
#         """