#!/usr/bin/env Rscript

### Packages ###
library(arrow)
library(data.table)
library(limma)

### Functions ###
load_frame_from_arrow <- function(
    filename
) {
    #' Loading an arrow file into a data frame
    #'
    #' @description Loads an arrow (also known as feather) format file
    #' and converts it into a data frame.
    #'
    #' @param filename Path to the arrow file
    #'
    #' @return Data frame with the data

    frame <- read_feather(filename)
    frame <- data.frame(frame, check.names=FALSE)
    rownames(frame) <- frame[[1]]
    frame <- frame[-1]

    return (frame)
}

load_frame <- function(
    filename,
    sep="\t"
) {
    #' Loading a *sv file into a data frame
    #'
    #' @description Loads a tsv or other delimiter separated values file
    #' and converts it into a data frame.
    #'
    #' @param filename Path to the tsv or other file
    #' @param sep Delimiter separating the values, by default "\t"
    #'
    #' @return Data frame with the data

    frame <- fread(filename, sep=sep, header=TRUE)
    frame <- data.frame(frame, check.names=FALSE)
    rownames(frame) <- frame[[1]]
    frame <- frame[-1]

    return (frame)
}

run_limma <- function(
    data,
    targets,
    groupA,
    groupB,
    outfile
) {
    #' Limma analysis
    #'
    #' @description Performs the Limma analysis using the provided data
    #' and targets files as well as two groups to be compared.
    #'
    #' @param data Path to the input data file
    #' @param targets Path to the input targets file
    #' @param groupA First group for the comparison
    #' @param groupB Second group for the comparison
    #' @param outfile Path to save the analysis results into

    mask <- targets$Condition %in% c(groupA, groupB)
    data_masked <- data[rownames(targets)[mask]]

    Paired <- factor(targets$Paired)
    Condition <- factor(targets$Condition, levels=c(groupA, groupB))
    design <- model.matrix(~ Paired + Condition)

    fit <- lmFit(data_masked, design)
    fit <- eBayes(fit)
    label <- paste0("Condition", toString(groupB))
    results <- topTable(fit, coef=label, number=Inf)

    write.table(results, file=outfile, quote=FALSE, sep='\t', col.names=NA)
}

### Main body ###
if (sys.nframe() == 0L) {
    library(argparse)

    parser <- ArgumentParser()
    parser$add_argument('-d', '--data', dest='data',
        help='path to the input data file', metavar='FILE')
    parser$add_argument('-t', '--targets', dest='targets',
        help='path to the input targets file', metavar='FILE')
    parser$add_argument('-ga', '--groupA', dest='groupA',
        help='name of the first group')
    parser$add_argument('-gb', '--groupB', dest='groupB',
        help='name of the second group')
    parser$add_argument('-o', '--outfile', dest='outfile',
        help='path to save the results into', metavar='FILE')

    args <- parser$parse_args()

    run_limma(
        data=args$data,
        targets=args$targets,
        groupA=args$groupA,
        groupB=args$groupB,
        outfile=args$outfile
    )
}