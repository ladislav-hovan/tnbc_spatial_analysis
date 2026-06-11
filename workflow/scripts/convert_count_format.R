#!/usr/bin/env Rscript

### Packages ###
library(arrow)

### Functions ###
convert_count_format <- function(
    rds_path,
    output_counts,
    output_spots
) {
    data <- readRDS(rds_path)
    counts <- data$cnts
    spots <- data$spots

    counts <- cbind(names=rownames(counts), data.frame(counts, row.names=NULL))
    write_feather(counts, output_counts)

    spots <- cbind(names=rownames(spots), data.frame(spots, row.names=NULL))
    write_feather(spots, output_spots)
}

### Main body ###
if (sys.nframe() == 0L) {
    library(argparse)

    parser <- ArgumentParser()
    parser$add_argument('-i', '--input', dest='input',
        help='path to the input RDS file', metavar='FILE')
    parser$add_argument('-oc', '--output-counts', dest='output_counts',
        help='path to save the count file into', metavar='FILE')
    parser$add_argument('-os', '--output-spots', dest='output_spots',
        help='path to save the spots file into', metavar='FILE')

    args <- parser$parse_args()

    convert_count_format(
        rds_path=args$input,
        output_counts=args$output_counts,
        output_spots=args$output_spots
    )
}