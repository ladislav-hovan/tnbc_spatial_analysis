#!/usr/bin/env Rscript

### Packages ###
library(arrow)

### Functions ###
extract_slide = function(
    s
) {
    #' Slide name extraction
    #'
    #' @description Extracts the slide name from a spot name.
    #'
    #' @param s String to extract the slide name from
    #'
    #' @return String with the slide name

    return (strsplit(s, split='.', fixed=TRUE)[[1]][1])
}

process_spot_classification <- function(
    rds_path,
    output_dir
) {
    #' Extraction of spot classification
    #'
    #' @description Extracts the classification probabilities for
    #' individual spots from all the slides into a directory where
    #' they will be saved in suitable subdirectories (patient/slide).
    #' The files are saved in feather format.
    #'
    #' @param rds_path Path to the input RDS file
    #' @param output_dir Path to the directory to save the
    #' classifications into

    data <- readRDS(rds_path)
    table_names <- names(data)

    for (table_name in table_names) {
        data_xy <- data[[table_name]]$xy
        data_pr <- data[[table_name]]$pr
        spot_names <- rownames(data[[table_name]]$spot)
        slide_names <- lapply(spot_names, extract_slide)
        colnames(data_xy) <- c('id', 'array_x', 'array_y')

        for (slide_name in unique(slide_names)) {
            mask = slide_names == slide_name
            slide_df = data.frame(
                cbind(data_xy[mask, c('array_x', 'array_y')], data_pr[mask,])
            )
            slide_dir <- file.path(output_dir, table_name, slide_name)
            output_slide <- file.path(slide_dir, 'classification.feather')
            write_feather(slide_df, output_slide)
        }
    }
}

### Main body ###
if (sys.nframe() == 0L) {
    library(argparse)

    parser <- ArgumentParser()
    parser$add_argument('-i', '--input', dest='input',
        help='path to the input RDS file', metavar='FILE')
    parser$add_argument('-od', '--output-dir', dest='output_dir',
        help='directory to save the output files into', metavar='DIR')

    args <- parser$parse_args()

    process_spot_classification(
        rds_path=args$input,
        output_dir=args$output_dir
    )
}