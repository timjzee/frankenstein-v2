library(stylo)
library(rjson)

setwd("/Users/tim/GitHub/frankenstein-v2/analysis")

#raw.corpus <- load.corpus(files = "all", corpus.dir = "./pca_texts",
#                          encoding = "UTF-8")

#tokenized.corpus <- txt.to.words.ext(raw.corpus, language = "English.all",
#                                     splitting.rule = "[!(;'?\n^).,>\":= \u2014\u2013]+")
glenarvon = fromJSON(file = "./tokenized_texts/lam_glenarvon.json")
thelastman = fromJSON(file = "./tokenized_texts/mws_the-last-man.json")
stirvyne = fromJSON(file = "./tokenized_texts/pbs_st-irvyne.json")
zastrozzi = fromJSON(file = "./tokenized_texts/pbs_zastrozzi.json")
frankenstein = fromJSON(file = "/Users/tim/GitHub/frankenstein-v2/sga-data/output/text_list_processed_ands.json")
tokenized.corpus = list(glenarvon, thelastman, stirvyne, zastrozzi, frankenstein)
names(tokenized.corpus) = c("lam_glenarvon", "mws_the-last-man", "pbs_st-irvyne", "pbs_zastrozzi", "???_frankenstein")

summary(tokenized.corpus)
sample_size = 4000
sample_shift = 4000
sample_overlap = sample_size - sample_shift

sliced.corpus <- make.samples(tokenized.corpus, sampling = "normal.sampling",
                              sample.overlap = sample_overlap,
                              sample.size = sample_size)

# Temporary list of frequent function words, eventually needs to based on Frankenstein as well 
frequent.features <- fromJSON(file = "./f_words.json")

freqs <- make.table.of.frequencies(sliced.corpus, features = frequent.features)

#pca.results = stylo(frequencies = freqs, analysis.type = "PCR",
#      custom.graph.title = "Lamb vs. the Shelleys",
#      mfw.min = 200, mfw.max = 200,
#      pca.visual.flavour = "loadings",
#      write.png.file = FALSE, gui = FALSE)

#summary(pca.results)
#par(mfrow = c(1, 1))

# check how pca.coordinates are calculated from loadings and frequencies
#freq_table = pca.results$table.with.all.freqs
#load_table = t(pca.results$pca.rotation)
#coor_table = pca.results$pca.coordinates
#sum(freq_table["PBS_zastrozzi.txt_4",] * load_table["PC1",])

# fuck it let's do our own PCA
library(ggbiplot)

samples = as.data.frame(as.matrix.data.frame(freqs))
rnames = rownames(freqs)
cnames = colnames(freqs)
rownames(samples) = rnames
colnames(samples) = cnames
num_franken_samples = (length(frankenstein) - sample_overlap) %/% sample_shift
num_lam_samples = (length(glenarvon) - sample_overlap) %/% sample_shift
num_mws_samples = (length(thelastman) - sample_overlap) %/% sample_shift
num_pbs_samples = (length(stirvyne) - sample_overlap) %/% sample_shift + (length(zastrozzi) - sample_overlap) %/% sample_shift

training_samples = samples[1:(NROW(samples) - num_franken_samples),]
franken_samples = samples[(NROW(training_samples) + 1):NROW(samples),]
authors = c(rep("Lamb", num_lam_samples), 
            rep("Mary Shelley", num_mws_samples),
            rep("Percy Shelley", num_pbs_samples))

training_samples.pca = prcomp(training_samples, center = TRUE, scale. = TRUE)

ggbiplot(training_samples.pca, labels = rownames(training_samples), 
         groups = authors, var.axes = TRUE, var.scale = 0.2, varname.adjust = 10)

frankenstein_sc = scale(franken_samples, center = training_samples.pca$center)

frankenstein_pred = frankenstein_sc %*% training_samples.pca$rotation

training_plusproj.pca = training_samples.pca
training_plusproj.pca$x = rbind(training_plusproj.pca$x, frankenstein_pred)

ggbiplot(training_plusproj.pca, 
#         labels = rownames(rbind(training_samples, franken_samples)), 
         groups = c(authors, rep("Unknown", num_franken_samples)), 
         var.axes = TRUE, var.scale = 0.2, varname.adjust = 10)

# Add analysis in which PCs are trained on just the Shelley's
frequent.features <- fromJSON(file = "./f_words_shelleys.json")
freqs <- make.table.of.frequencies(sliced.corpus, features = frequent.features)

shelley_samples = training_samples[(num_lam_samples + 1):NROW(training_samples),]
shelley_samples.pca = prcomp(shelley_samples, center = TRUE, scale. = TRUE)
frankenstein_sc = scale(franken_samples, center = shelley_samples.pca$center)
frankenstein_pred = frankenstein_sc %*% shelley_samples.pca$rotation

subset_start = 600
subset_end = 617
franken_pred_subset = frankenstein_pred[subset_start:subset_end,]
subset_length = NROW(franken_pred_subset)

shelley_plusproj.pca = shelley_samples.pca
shelley_plusproj.pca$x = rbind(shelley_plusproj.pca$x, franken_pred_subset)

ggbiplot(shelley_plusproj.pca, 
#         labels = rownames(rbind(shelley_samples, franken_samples[subset_start:subset_end,])), 
         ellipse = TRUE,
         groups = c(authors[(num_lam_samples + 1):NROW(training_samples)], rep("Unknown", subset_length)), 
         var.axes = TRUE, var.scale = 0.5, varname.adjust = 10)

ggbiplot(shelley_plusproj.pca, 
#         labels = rownames(rbind(shelley_samples, franken_samples[subset_start:subset_end,])), 
         choices = c(1,3), 
         ellipse = TRUE,
         groups = c(authors[(num_lam_samples + 1):NROW(training_samples)], rep("Unknown", subset_length)), 
         var.axes = TRUE, var.scale = 0.5, varname.adjust = 10)

# based on PC1 & PC3 plot: modal verbs --> PBS; quantifiers --> MWS?

# first visualize which portions of Frankenstein are edited by PBS (graph in rollingStylo.R); amount/percentage of words contributed; most frequently edited/added words
# now let's see how PCA does
# based on PC1 & PC2 of training data (both including and excluding Lamb): most of frankenstein written by MWS
# However, if we look at subset we know was heavily edited by PBS we see that it may form a category of its own
# This begs the question what separates the portions that are heavily edited by PBS from the rest of frankenstein?
# we need a PCA analysis based on samples that are classified according to hand proportion

