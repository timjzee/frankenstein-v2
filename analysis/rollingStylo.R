library(stylo)
library(rjson)
library(zoo)

setwd("/Users/tim/GitHub/frankenstein-v2/analysis")

# tokenized.test.corpus = load.corpus.and.parse(corpus.dir = "./test_set",
#                                              encoding = "UTF-8",
#                                              splitting.rule = "[!(;'?\n^).,>\":= \u2014\u2013]+")
#summary(tokenized.test.corpus)
# write(toJSON(tokenized.test.corpus$S_text.txt), "frankenstein_tokenized_r.json")

text_tokens = fromJSON(file = "/Users/tim/GitHub/frankenstein-v2/sga-data/output/text_list_processed_ands.json")
tokenized.test.corpus = list(text_tokens)
names(tokenized.test.corpus) = c("S_text")
length(tokenized.test.corpus$S_text) == length(text_tokens)

# tokenized.training.corpus = load.corpus.and.parse(corpus.dir = "./reference_set",
#                                                  encoding = "UTF-8")
thelastman = fromJSON(file = "./tokenized_texts/mws_the-last-man.json")
stirvyne = fromJSON(file = "./tokenized_texts/pbs_st-irvyne.json")
zastrozzi = fromJSON(file = "./tokenized_texts/pbs_zastrozzi.json")
tokenized.training.corpus = list(thelastman, stirvyne, zastrozzi)
names(tokenized.training.corpus) = c("mws_the-last-man", "pbs_st-irvyne", "pbs_zastrozzi")

summary(tokenized.training.corpus)

sample_size = 800
sample_overlap = 700
resolution = sample_size - sample_overlap

sliced.test.corpus = make.samples(tokenized.test.corpus, sampling = "normal.sampling",
                              sample.size = sample_size, sample.overlap = sample_overlap)

sliced.training.corpus = make.samples(tokenized.training.corpus, sampling = "normal.sampling",
                                      sample.size = sample_size, sample.overlap = 0)

function_words = fromJSON(file = "./f_words_shelleys.json")

results = rolling.classify(test.corpus = sliced.test.corpus,
                           training.corpus = sliced.training.corpus,
                           write.png.file = FALSE, 
                           classification.method = "svm", features = function_words,
                           milestone.points = c(60214), milestone.labels = c("Fair Copy"),
                           slice.size = sample_size, slice.overlap = sample_overlap)

svm_classification = as.vector(results$classification.results)

hand_tokens = fromJSON(file = "/Users/tim/GitHub/frankenstein-v2/sga-data/output/hand_list_processed.json")
num_samples = as.integer((length(hand_tokens) - sample_overlap) / resolution)
num_words = (num_samples - 1) * resolution + sample_size
culled_hand_tokens = hand_tokens[1:num_words]
hand_matrix = rollapply(culled_hand_tokens, sample_size, by = resolution, c)
hand_groups = split(hand_matrix, row(hand_matrix))
hand_majorities = sapply(hand_groups, function(x) names(which.max(table(x))))
pbs_proportions = sapply(hand_groups, function(x) sum(x == "pbs") / sample_size)

norm_score = 0.5 + results$classification.scores[, 1] / (2 * max(results$classification.scores))
scorenames = results$classification.rankings[, 1]
norm_scores = data.frame(norm_score, scorenames, pbs_proportions)
norm_scores$majority_proportions = 1:nrow(norm_scores)
norm_scores[norm_scores$pbs_proportions > 0.5,]$majority_proportions = norm_scores[norm_scores$pbs_proportions > 0.5,]$pbs_proportions
norm_scores[norm_scores$pbs_proportions < 0.5,]$majority_proportions = 1 - norm_scores[norm_scores$pbs_proportions < 0.5,]$pbs_proportions

norm_scores$pbs_scores = 1:nrow(norm_scores)
norm_scores[norm_scores$scorenames == "pbs",]$pbs_scores = norm_scores[norm_scores$scorenames == "pbs",]$norm_score
norm_scores[norm_scores$scorenames == "mws",]$pbs_scores = 1 - norm_scores[norm_scores$scorenames == "mws",]$norm_score
norm_scores$mws_scores = 1 - norm_scores$pbs_scores
# Correlation between Normalized PBS scores & Proportion of PBS hand
cor(norm_scores$pbs_scores, pbs_proportions)
plot(norm_scores$pbs_scores, col = "grey", ylim = c(0,1))
lines(x = c(0, length(norm_scores$pbs_proportions)), y = c(0.5, 0.5), col = "red", lty = 2)
lines(norm_scores$pbs_proportions, col = "black")
# Correlation between Majority scores & Majority Proportion
cor(norm_scores$norm_score, norm_scores$majority_proportions)


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
proportion_pbs = colsums["pbs"] / num_samples
proportion_pbs

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

# subtract relFreq in pbs_freqs from relFreq in mws_freqs, and then sort by largest difference
