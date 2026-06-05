#!/usr/bin/env Rscript

library(arrow)

args <- commandArgs(TRUE)

data <- readRDS(args[1])
counts <- data$cnts
spots <- data$spots

counts <- cbind(names=rownames(counts), data.frame(counts, row.names=NULL))
write_feather(counts, args[2])

spots <- cbind(names=rownames(spots), data.frame(spots, row.names=NULL))
write_feather(spots, args[3])