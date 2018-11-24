---
layout: post
title:  "Hacking Frankenstein (Part 2): Exploring Percy's contribution"
date:   2018-11-12 01:15:00 +0100
categories: linguistics literature text-mining
---

# Introduction

In my [previous post](http://www.timzee.nl/linguistics/literature/text-mining/2018/05/21/frankenstein1.html), I described how I created hand annotation files for a draft version of Frankenstein. As I explained in that post, I needed those annotations as a baseline for an authorship attribution analysis of Frankenstein: Would such a machine learning approach come to similar conclusions as a painstaking handwriting analysis in terms of Percy Shelley's contribution to his wife's famous novel? This article will make a first attempt at answering that question. But first let's take a closer look at our hand annotation files and see how much and what Percy actually contributed.

# Descriptive statistics of Percy's contribution

First of all we'll need to import both the tokenized text of Frankenstein and the corresponding hand annotations in a statistics program. I'm using [*R*](https://www.r-project.org) because it's free and programmable. We can use it to see how many words were edited or added by Percy.

```python
library(rjson)

text_tokens = fromJSON(file = "./text_list_processed.json")
hand_tokens = fromJSON(file = "./hand_list_processed.json")

hand_df = data.frame(text_tokens, hand_tokens)
num_pbs_words = NROW(hand_df[hand_df$hand_tokens == "pbs",])
prop_pbs_words = num_pbs_words / NROW(hand_df)
```
The code above stores the amount of words that were authored by Percy in `num_pbs_words` and the proportion of words in Percy's hand in `prop_pbs_words`.
```
> num_pbs_words
[1] 7173
> prop_pbs_words
[1] 0.1149133
```
This shows that more than 11% of the 62421 words in the Frankenstein draft were penned by Percy. Surprisingly, this is a bit more than the 4000-5000 words estimated by Charles E. Robinson (2008, p. 25), who created the annotated edition on which our own annotations are based. One explanation for this discrepancy is that, although the final pages of Chapter 18 were (re)written in Percy's hand, much of the text might have been based on an earlier draft by Mary.

As a next step we could take a look at how Percy's contributions are distributed throughout the draft:

```python
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
```

![alt text](https://github.com/timjzee/frankenstein-v2/blob/master/articles/PBS_percentage.png?raw=true "Percentage of Percy's hand")

This plot shows that Percy contributed both shorter additions (represented by the smaller spikes) and longer (> 100 words) stretches of text.


Now let's take a look at what Percy's contribution mostly consists of.
```python
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
```
By looking at the first five rows of `all_freqs`, we'll see what the largest differences between Mary and Percy in terms of word frequency are:
```
> head(all_freqs[, c(1, 3, 5, 6)], 5)
      word  MWSrelFreq PBSrelFreq      freqdif
6336 which 0.005810165 0.01645058  0.010640413
261    and 0.041377063 0.03136763 -0.010009435
5758   the 0.056128729 0.04698174 -0.009146992
2894     i 0.041033160 0.03373763 -0.007295532
3960    of 0.033069070 0.03764115  0.004572084
```
Note that this way of calculating frequency differences favours authorial differences in very frequent words such as *and*, *the*, and *I*, all of which are used less frequently by Percy. This inherent bias of the difference measure makes it even more striking that *which*, a less frequent word for both authors, shows the largest difference, with Percy using it more often.

We're starting to get a better picture of Percy's additions, but if we want to dig deeper, we will need more sophisticated statistical methods.

# Principle Component Analysis

```python
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

```

![alt text](https://github.com/timjzee/frankenstein-v2/blob/master/articles/pca_frankenstein_arrow.png?raw=true "PCA of Frankenstein")
