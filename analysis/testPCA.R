library(stylo)
library(rjson)

setwd("/Users/tim/GitHub/frankenstein-v2/analysis")

raw.corpus <- load.corpus(files = "all", corpus.dir = "./pca_texts",
                          encoding = "UTF-8")

tokenized.corpus <- txt.to.words.ext(raw.corpus, language = "English.all",
                                     preserve.case = FALSE)
summary(tokenized.corpus)

sliced.corpus <- make.samples(tokenized.corpus, sampling = "normal.sampling",
                              sample.size = 5000)

# Temporary list of frequent function words, eventually needs to based on Frankenstein as well 
frequent.features <- fromJSON(file = "./f_words.json")

freqs <- make.table.of.frequencies(sliced.corpus, features = frequent.features)

stylo(frequencies = freqs, analysis.type = "PCR",
      custom.graph.title = "Lamb vs. the Shelleys",
      mfw.min = 200, mfw.max = 200,
      pca.visual.flavour = "loadings",
      write.png.file = FALSE, gui = FALSE)

par(mfrow = c(1, 1))