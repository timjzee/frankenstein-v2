library(stylo)

setwd("/Users/tim/GitHub/frankenstein-v2/analysis")

results = rolling.classify(write.png.file = FALSE, 
                 classification.method = "svm", mfw = 100,
                 training.set.sampling = "normal.sampling",
                 slice.size = 1000, slice.overlap = 900)

svm_classification = as.vector(results$classification.results)
hand_classification = rep("MWS", 709)
hand_classification[709] = "PBS"

confusion_matrix = as.matrix(table(Handwriting = hand_classification, Predicted = svm_classification))

