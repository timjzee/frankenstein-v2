---
layout: post
title:  "Hacking Frankenstein (Part 2): Exploring Percy's contribution"
date:   2018-11-12 01:15:00 +0100
categories: linguistics literature text-mining
---

# Introduction

In my [previous post](http://www.timzee.nl/linguistics/literature/text-mining/2018/05/21/frankenstein1.html), I described how I created hand annotation files for a draft version of Frankenstein. As I explained in that post, I needed those annotations as a baseline for an authorship attribution analysis of Frankenstein: Would such a machine learning approach come to similar conclusions as a painstaking handwriting analysis in terms of Percy Shelley's contribution to his wife's famous novel? This article will make a first attempt at answering that question. But first let's take a closer look at our hand annotation files and see how much and what Percy actually contributed.

# Descriptive statistics of Percy's contribution


Using the statistics programming language *R* we can nicely visualize Percy's contributions throughout *Frankenstein*:

```python
library(rjson)
library(zoo)

hand_tokens = fromJSON(file = "./hand_list_processed.json")
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
