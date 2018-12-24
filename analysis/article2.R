library(rjson)

text_tokens = fromJSON(file = "/Users/tim/GitHub/frankenstein-v2/sga-data/output/text_list_processed_ands.json")
hand_tokens = fromJSON(file = "/Users/tim/GitHub/frankenstein-v2/sga-data/output/hand_list_processed.json")

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

#
text_stretches = fromJSON(file = "/Users/tim/GitHub/frankenstein-v2/sga-data/output/text_list.json")
hand_stretches = fromJSON(file = "/Users/tim/GitHub/frankenstein-v2/sga-data/output/hand_list.json")
stretches_df = data.frame(text_stretches, hand_stretches)
stretches_df$tokens = regmatches(stretches_df$text_stretches, gregexpr("[a-zA-Z0-9&]+", stretches_df$text_stretches, perl = TRUE))
stretches_df$num_words = sapply(stretches_df$tokens, function(x) length(x))
stretches_df$num_words_log = log10(stretches_df$num_words)
hist(stretches_df[stretches_df$hand_stretches == "pbs",]$num_words_log, xlab = "Contribution length (words)", main = "Histogram of PBS contribution lengths", axes = FALSE)
axis(1, labels = seq(0, 3.5, 0.5), at = seq(0, 3.5, 0.5), cex.axis = 0.8, padj = -0.8)
axis(1, labels = rep(10, 8), at = seq(0, 3.5, 0.5), hadj = 1.25, padj = 0.5)
axis(2, labels = seq(0, 600, 100), at = seq(0, 600, 100))

short_stretches = sum(stretches_df[stretches_df$hand_stretches == "pbs" & stretches_df$num_words < 100,]$num_words)
long_stretches = sum(stretches_df[stretches_df$hand_stretches == "pbs" & stretches_df$num_words >= 100,]$num_words)
short_stretches / (short_stretches + long_stretches)
#

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
#sample_shift = 100
#sample_overlap = sample_size - sample_shift
#num_samples = (length(text_tokens) - sample_overlap) %/% sample_shift
#num_words = (num_samples - 1) * sample_shift + sample_size
#culled_word_tokens = text_tokens[1:num_words]
#word_matrix = rollapply(culled_word_tokens, sample_size, by = sample_shift, c)
#word_groups = split(word_matrix, row(word_matrix))
num_samples = length(text_tokens) %/% sample_size
num_words = num_samples * sample_size
culled_word_tokens = text_tokens[1:num_words]
word_matrix = rollapply(culled_word_tokens, sample_size, by = sample_size, c)
word_groups = split(word_matrix, row(word_matrix))

culled_hand_tokens = hand_tokens[1:num_words]
#hand_matrix = rollapply(culled_hand_tokens, sample_size, by = sample_shift, c)
hand_matrix = rollapply(culled_hand_tokens, sample_size, by = sample_size, c)
hand_groups = split(hand_matrix, row(hand_matrix))
hand_majorities = sapply(hand_groups, function(x) names(which.max(table(x))))

# explain that labels are made to correspond to indices in previous plot
sample_labels = paste(hand_majorities, as.character((sample_size/100)*1:num_samples-(sample_size/100-1)), sep = "_")
names(word_groups) = sample_labels

library(stylo)

# describe why we need function words
all_freqs$mfw = (all_freqs$PBSrelFreq + all_freqs$MWSrelFreq) / 2
all_freqs = all_freqs[order(-all_freqs$mfw),]
mfw = head(all_freqs$word, 200)

function_words = fromJSON(file = "/Users/tim/GitHub/frankenstein-v2/analysis/f_words_frankenstein.json")
freqs = make.table.of.frequencies(word_groups, features = function_words)
samples = as.data.frame(as.matrix.data.frame(freqs))
rnames = rownames(freqs)
cnames = colnames(freqs)
rownames(samples) = rnames
colnames(samples) = cnames

library(ggbiplot)

samples_pca = prcomp(samples, center = TRUE, scale. = TRUE)
ggbiplot(samples_pca, labels = substr(rownames(samples), 5, nchar(rownames(samples))), groups = hand_majorities, var.axes = TRUE, var.scale = 0.2, varname.adjust = 8, ellipse = TRUE, varname.size = 2)

# PCA 2

thelastman = fromJSON(file = "/Users/tim/GitHub/frankenstein-v2/analysis/tokenized_texts/mws_the-last-man.json")
stirvyne = fromJSON(file = "/Users/tim/GitHub/frankenstein-v2/analysis/tokenized_texts/pbs_st-irvyne.json")
zastrozzi = fromJSON(file = "/Users/tim/GitHub/frankenstein-v2/analysis/tokenized_texts/pbs_zastrozzi.json")
glenarvon = fromJSON(file = "/Users/tim/GitHub/frankenstein-v2/analysis/tokenized_texts/lam_glenarvon.json")

training_texts = list(thelastman, 
#                      glenarvon,
                      stirvyne, 
                      zastrozzi)
names(training_texts) = c("mws_the-last-man", 
#                          "lam_glenarvon",
                          "pbs_st-irvyne", 
                          "pbs_zastrozzi")
sample_size = 5000
training_samples = make.samples(training_texts, sampling = "normal.sampling", sample.size = sample_size)

function_words = fromJSON(file = "/Users/tim/GitHub/frankenstein-v2/analysis/f_words_shelleys_franken_compatible.json")
training_freqs = make.table.of.frequencies(training_samples, features = function_words)

training_freqs_df = as.data.frame(as.matrix.data.frame(training_freqs))
rownames(training_freqs_df) = rownames(training_freqs)
colnames(training_freqs_df) = colnames(training_freqs)

author_names = substr(rownames(training_freqs), 1, 3)
#sample_no = substr(rownames(training_freqs), nchar(rownames(training_freqs))-1, nchar(rownames(training_freqs)))
num_train_samples = NROW(training_freqs_df)

training_pca = prcomp(training_freqs_df, center = TRUE, scale. = TRUE)

ggbiplot(training_pca, labels = rep("*", num_train_samples), 
         groups = author_names, var.axes = TRUE, var.scale = 0.2, 
         varname.adjust = 8, ellipse = TRUE, labels.size = 4)

# check rotation of words for pc1
rotation_df = as.data.frame(training_pca$rotation)
rotation_df_ordered = rotation_df[order(-abs(rotation_df$PC1)),]
structure(rotation_df_ordered[1:5, "PC1"], 
          names=rownames(rotation_df_ordered)[1:5])

hand_df_whil = hand_df[hand_df$text_tokens == "while" | hand_df$text_tokens == "whilst",]
hand_df_whil$text_tokens = factor(hand_df_whil$text_tokens)
hand_df_whil$hand_tokens = factor(hand_df_whil$hand_tokens)
whil_counts = table(hand_df_whil$text_tokens, hand_df_whil$hand_tokens)
#whil_counts["mws",] = whil_counts["mws",] / nrow(hand_df[hand_df$hand_tokens == "mws",])
#whil_counts["pbs",] = whil_counts["pbs",] / nrow(hand_df[hand_df$hand_tokens == "pbs",])
whil_counts[, "mws"] = whil_counts[, "mws"] / sum(whil_counts[, "mws"])
whil_counts[, "pbs"] = whil_counts[, "pbs"] / sum(whil_counts[, "pbs"])

#par(mfrow=c(1, 1), mar=c(5, 4, 6, 2))
barplot(whil_counts, main = "Distribution of 'while' / 'whilst' in Frankenstein",
        ylab = "Hand Annotation", col = c("gray", "white"), xpd = FALSE, xlab = "Proportion of variant",
        legend = rownames(whil_counts), horiz = TRUE, names.arg = colnames(whil_counts),
        args.legend = list(x = "top", horiz = TRUE, inset=c(0, -0.12), xpd = TRUE, bty = "n"))

hand_df_pron1 = hand_df[hand_df$text_tokens == "you" | 
                         hand_df$text_tokens == "ye" | 
                         hand_df$text_tokens == "thee" | 
                         hand_df$text_tokens == "thou",]
hand_df_pron1$text_tokens = factor(hand_df_pron1$text_tokens)
hand_df_pron1$hand_tokens = factor(hand_df_pron1$hand_tokens)
pron_counts1 = table(hand_df_pron1$text_tokens, hand_df_pron1$hand_tokens)
#pron_counts1[1,] = pron_counts1[1,] + pron_counts1[2,]
#pron_counts1 = pron_counts1[c(1,3),]
#rownames(pron_counts1) = c("thee/thou", "you")
par(mfrow=c(1, 1), mar=c(5, 4, 6, 2))
pron_counts1[, "mws"] = pron_counts1[, "mws"] / sum(pron_counts1[, "mws"])
pron_counts1[, "pbs"] = pron_counts1[, "pbs"] / sum(pron_counts1[, "pbs"])
barplot(pron_counts1, main = "Distribution of 'thee' / 'thou' / 'ye' / 'you' in Frankenstein",
        ylab = "Hand Annotation", col = c("black", "dark gray", "gray", "white"), xpd = FALSE, xlab = "Proportion of variant",
        legend = rownames(pron_counts1), horiz = TRUE, names.arg = colnames(pron_counts1),
        args.legend = list(x = "top", horiz = TRUE, inset=c(0, -0.2), xpd = TRUE, bty = "n"))


hand_df_pron2 = hand_df[hand_df$text_tokens == "thy" | 
                          hand_df$text_tokens == "thine" | 
                          hand_df$text_tokens == "your",]
hand_df_pron2$text_tokens = factor(hand_df_pron2$text_tokens)
hand_df_pron2$hand_tokens = factor(hand_df_pron2$hand_tokens)
pron_counts2 = table(hand_df_pron2$text_tokens, hand_df_pron2$hand_tokens)
pron_counts2[, "mws"] = pron_counts2[, "mws"] / sum(pron_counts2[, "mws"])
pron_counts2[, "pbs"] = pron_counts2[, "pbs"] / sum(pron_counts2[, "pbs"])
barplot(pron_counts2, main = "Distribution of 'thine' / 'thy' / 'your' in Frankenstein",
        ylab = "Hand Annotation", col = c("dark gray", "gray", "white"), xpd = FALSE, xlab = "Proportion of variant",
        legend = rownames(pron_counts2), horiz = TRUE, names.arg = colnames(pron_counts2),
        args.legend = list(x = "top", horiz = TRUE, inset=c(0, -0.2), xpd = TRUE, bty = "n"))

hand_df_inter = hand_df[hand_df$text_tokens == "o" | 
                          hand_df$text_tokens == "oh" | 
                          hand_df$text_tokens == "ah" | 
                          hand_df$text_tokens == "alas",]
hand_df_inter$text_tokens = factor(hand_df_inter$text_tokens)
hand_df_inter$hand_tokens = factor(hand_df_inter$hand_tokens)
inter_counts = table(hand_df_inter$text_tokens, hand_df_inter$hand_tokens)
inter_counts[, "mws"] = inter_counts[, "mws"] / NROW(hand_df[hand_df$hand_tokens == "mws",]) * 100
inter_counts[, "pbs"] = inter_counts[, "pbs"] / NROW(hand_df[hand_df$hand_tokens == "pbs",]) * 100
barplot(inter_counts, main = "Distribution of 'ah' / 'alas' / 'o' / 'oh' in Frankenstein",
        ylab = "Hand Annotation", col = c("black", "dark gray", "gray", "white"), xpd = FALSE, xlab = "Percentage of respective authors' total word counts",
        legend = rownames(inter_counts), horiz = TRUE, names.arg = colnames(inter_counts),
        args.legend = list(x = "top", horiz = TRUE, inset=c(0, -0.2), xpd = TRUE, bty = "n"))

#

franken_freqs = make.table.of.frequencies(word_groups, features = function_words)
franken_freqs_df = as.data.frame(as.matrix.data.frame(franken_freqs))
rownames(franken_freqs_df) = rownames(franken_freqs)
colnames(franken_freqs_df) = colnames(franken_freqs)

frankenstein_sc = scale(franken_freqs, center = training_pca$center)
frankenstein_pred = frankenstein_sc %*% training_pca$rotation
training_plus_pca = training_pca
training_plus_pca$x = rbind(training_plus_pca$x, frankenstein_pred)
franken_names = paste(substr(rownames(franken_freqs_df), 1, 3), rep("F", num_samples), sep = "-")
franken_nums = substr(rownames(samples), 5, nchar(rownames(franken_freqs_df)))


ggbiplot(training_plus_pca, 
         labels = c(rep("*", num_train_samples), franken_nums), 
         groups = c(author_names, franken_names), var.axes = TRUE, 
#         choices = c(1, 2),
         ellipse = TRUE, var.scale = 0.2, varname.adjust = 8, labels.size = 4)

# what makes some of the pbs-F samples stand out?
# e.g. sample 213
franken_freqs_df["pbs_213",]


# add projection of glenarvon samples to show that positioning of frankenstein samples is actually meaningful


# conclusion: differences between MWS and PBS do not translate very strongly to Frankenstein. reference to hypothesis about collaborative style
# However, we can take a look at some function words that stand out (briefly discuss 'which'). Investigate use of thou/you and thine/your.
