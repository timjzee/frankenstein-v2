library(stylo)
library(rjson)
library(zoo)

setwd("/Users/tim/GitHub/frankenstein-v2/analysis")

# write(toJSON(tokenized.test.corpus$S_text.txt), "frankenstein_tokenized_r.json")

tokenized.test.corpus = load.corpus.and.parse(corpus.dir = "./test_set",
                                              encoding = "UTF-8",
                                              splitting.rule = "[!(;'?\n^).,>\":= \u2014\u2013]+")
summary(tokenized.test.corpus)

text_tokens = fromJSON(file = "/Users/tim/GitHub/frankenstein-v2/sga-data/output/text_list_processed.json")
length(tokenized.test.corpus$S_text) == length(text_tokens)

tokenized.training.corpus = load.corpus.and.parse(corpus.dir = "./reference_set",
                                                  encoding = "UTF-8")
summary(tokenized.training.corpus)

sample_size = 1500
sample_overlap = 1400
resolution = sample_size - sample_overlap

sliced.test.corpus = make.samples(tokenized.test.corpus, sampling = "normal.sampling",
                              sample.size = sample_size, sample.overlap = sample_overlap)

sliced.training.corpus = make.samples(tokenized.training.corpus, sampling = "normal.sampling",
                                      sample.size = sample_size, sample.overlap = 0)

results = rolling.classify(test.corpus = sliced.test.corpus,
                           training.corpus = sliced.training.corpus,
                           write.png.file = TRUE, 
                           classification.method = "svm", mfw = 100,
                           slice.size = sample_size, slice.overlap = sample_overlap)

svm_classification = as.vector(results$classification.results)

hand_tokens = fromJSON(file = "/Users/tim/GitHub/frankenstein-v2/sga-data/output/hand_list_processed.json")
num_samples = as.integer((length(hand_tokens) - sample_overlap) / resolution)
num_words = (num_samples - 1) * resolution + sample_size
culled_hand_tokens = hand_tokens[1:num_words]
hand_matrix = rollapply(culled_hand_tokens, sample_size, by = resolution, c)
hand_groups = split(hand_matrix, row(hand_matrix))
hand_majorities = sapply(hand_groups, function(x) names(which.max(table(x))))

summary(svm_classification)
summary(hand_majorities)

confusion_matrix = as.matrix(table(Handwriting = hand_majorities, Predicted = svm_classification))
confusion_matrix

num_classes = nrow(confusion_matrix)
diag = diag(confusion_matrix)
rowsums = apply(confusion_matrix, 1, sum)
colsums = apply(confusion_matrix, 2, sum)
p = rowsums / num_samples
q = colsums / num_samples
accuracy = sum(diag) / num_samples
accuracy

precision = diag / colsums 
recall = diag / rowsums 
f1 = 2 * precision * recall / (precision + recall)
data.frame(precision, recall, f1)

macroPrecision = mean(precision)
macroRecall = mean(recall)
macroF1 = mean(f1)
data.frame(macroPrecision, macroRecall, macroF1)

### baseline for comparison ###

baseline_classification = rep("mws", num_samples)

confusion_matrix = as.matrix(table(Handwriting = hand_majorities, Predicted = baseline_classification))
confusion_matrix = cbind(confusion_matrix, pbs = c(0, 0))
confusion_matrix

num_classes = nrow(confusion_matrix)
diag = diag(confusion_matrix)
rowsums = apply(confusion_matrix, 1, sum)
colsums = apply(confusion_matrix, 2, sum)
p = rowsums / num_samples
q = colsums / num_samples
accuracy = sum(diag) / num_samples
accuracy

precision = c(diag["mws"] / colsums["mws"], 1)
names(precision) = c("mws", "pbs")
recall = diag / rowsums 
f1 = 2 * precision * recall / (precision + recall)
data.frame(precision, recall, f1)

macroPrecision = mean(precision)
macroRecall = mean(recall)
macroF1 = mean(f1)
data.frame(macroPrecision, macroRecall, macroF1)

## some descriptive analysis

hand_df = data.frame(text_tokens, hand_tokens)
pbs_freqs = as.data.frame(table(hand_df[hand_df$hand_tokens == "pbs",]$text_tokens))
pbs_freqs = pbs_freqs[order(-pbs_freqs$Freq),]
pbs_freqs$relFreq = pbs_freqs$Freq / table(hand_tokens)["pbs"]
mws_freqs = as.data.frame(table(hand_df[hand_df$hand_tokens == "mws",]$text_tokens))
mws_freqs = mws_freqs[order(-mws_freqs$Freq),]
mws_freqs$relFreq = mws_freqs$Freq / table(hand_tokens)["mws"]


