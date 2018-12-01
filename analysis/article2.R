library(rjson)

text_tokens = fromJSON(file = "./text_list_processed.json")
hand_tokens = fromJSON(file = "./hand_list_processed.json")

hand_df = data.frame(text_tokens, hand_tokens)
num_pbs_words = NROW(hand_df[hand_df$hand_tokens == "pbs",])
prop_pbs_words = num_pbs_words / NROW(hand_df)

library(zoo)

sample_size = 100
num_samples = length(hand_tokens) %/% sample_size
num_tokens = num_samples * sample_size
culled_hand_tokens = hand_tokens[1:num_tokens]
hand_matrix = rollapply(culled_hand_tokens, sample_size, by = sample_size, c)
hand_groups = split(hand_matrix, row(hand_matrix))
pbs_proportions = sapply(hand_groups, function(x) sum(x == "pbs"))
plot(pbs_proportions, ylim = c(0,100), type = 'l',
     main = "Percy's contribution throughout Frankenstein",
     xlab = "Sample index (Sample size = 100 words)",
     ylab = "% of words in Percy's hand")


mws_freqs = as.data.frame(table(hand_df[hand_df$hand_tokens == "mws",]$text_tokens))
mws_freqs = mws_freqs[order(-mws_freqs$Freq),]
mws_freqs$relFreq = mws_freqs$Freq / table(hand_tokens)["mws"]
names(mws_freqs) = c("word", "MWSFreq", "MWSrelFreq")
pbs_freqs = as.data.frame(table(hand_df[hand_df$hand_tokens == "pbs",]$text_tokens))
pbs_freqs = pbs_freqs[order(-pbs_freqs$Freq),]
pbs_freqs$relFreq = pbs_freqs$Freq / table(hand_tokens)["pbs"]
names(pbs_freqs) = c("word", "PBSFreq", "PBSrelFreq")
all_freqs = merge(mws_freqs, pbs_freqs, by.x = "word", by.y = "word")
all_freqs$freqdif = all_freqs$PBSrelFreq - all_freqs$MWSrelFreq
all_freqs$absfreqdif = abs(all_freqs$freqdif)
all_freqs = all_freqs[order(-all_freqs$absfreqdif),]

head(all_freqs[, c(1, 3, 5, 6)], 5)

sample_size = 400
sample_shift = 100
sample_overlap = sample_size - sample_shift

num_samples = (length(text_tokens) - sample_overlap) %/% sample_shift
num_words = (num_samples - 1) * sample_shift + sample_size
culled_word_tokens = text_tokens[1:num_words]
word_matrix = rollapply(culled_word_tokens, sample_size, by = sample_shift, c)
word_groups = split(word_matrix, row(word_matrix))

culled_hand_tokens = hand_tokens[1:num_words]
hand_matrix = rollapply(culled_hand_tokens, sample_size, by = sample_shift, c)
hand_groups = split(hand_matrix, row(hand_matrix))
hand_majorities = sapply(hand_groups, function(x) names(which.max(table(x))))
# explain that labels are made to correspond to indices in previous plot
sample_labels = paste(hand_majorities, as.character(4*1:num_samples-3), sep = "_")

names(word_groups) = sample_labels

library(stylo)
library(ggbiplot)

# describe why we need function words
all_freqs$mfw = (all_freqs$PBSrelFreq + all_freqs$MWSrelFreq) / 2
all_freqs = all_freqs[order(-all_freqs$mfw),]
mfw = head(all_freqs$word, 200)

function_words = fromJSON(file = "./f_words_frankenstein.json")
freqs = make.table.of.frequencies(word_groups, features = function_words)
samples = as.data.frame(as.matrix.data.frame(freqs))
rnames = rownames(freqs)
cnames = colnames(freqs)
rownames(samples) = rnames
colnames(samples) = cnames

samples_pca = prcomp(samples, center = TRUE, scale. = TRUE)
ggbiplot(samples_pca, labels = rownames(samples), groups = hand_majorities, var.axes = TRUE, var.scale = 0.2, varname.adjust = 8, ellipse = TRUE, varname.size = 2)