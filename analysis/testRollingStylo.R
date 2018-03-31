library(stylo)

setwd("/Users/tim/GitHub/frankenstein-v2/analysis")

rolling.classify(write.png.file = FALSE, 
                 classification.method = "svm", mfw = 100,
                 training.set.sampling = "normal.sampling",
                 slice.size = 1000, slice.overlap = 900)
