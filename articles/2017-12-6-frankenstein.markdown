---
layout: post
title:  "Hacking Frankenstein (Part 1): A gold standard"
date:   2017-12-6 00:14:38 +0100
categories: linguistics literature text-mining
---

# Introduction

A few years ago—when I still wanted to major in English literature—I decided to read *Frankenstein*. Apart from being vaguely interested in the story, I was mainly drawn to it because of the weird 19th century Romantic drama surrounding its inception. Long story short, Percy, a 22 year old poet, meets Mary, the 17 year old daughter of a prominent intellectual; Percy deserts his pregnant wife to party with Mary in continental Europe, where Mary participates in a ghost story competition and writes *Frankenstein*; Back in England, Percy edits and publishes *Frankenstein* before drowning off the coast of Italy.

Intrigued, I looked for an annotated edition of the novel that would provide additional details and context to the creation of Frankenstein. I quickly settled on this edition:

![alt text](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png "Logo Title Text 1")

Interestingly, this edition contains two versions of the story: one version reprints the text of the first edition of the novel from 1818, and the other version was composed by the editor from handwritten drafts of *Frankenstein* that are held at the Oxford University library. However, the editor hadn't stopped there. He had marked Percy's contributions to this draft text in italics, using regular font for Mary's writing:

![alt text](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png "Logo Title Text 1")

The editor, Charles E. Robinson, had based this annotation on a painstaking analysis of the different handwritings and types of ink that were used in the drafts.
These annotations definitely contributed to my reading experience, but after finishing the novel I quickly forgot about them. Last year, however, I was suddenly reminded of them when I was scrambling to find a topic for a course project. The course, which was called "Text mining", was about the application of computer algorithms (or to use another buzzword "machine learning") to 'mine' interesting information from text sources. The course had briefly touched on authorship attribution: feeding linguistic features of a text into computer algorithms to determine its author. I wondered whether it would be possible to use this method to arrive at an annotation of *Frankenstein* that was similar to the hand annotation by Robinson.

During my course project, I encountered a number of problems and questions. In this three part series of articles I'll describe how I eventually solved these problems (by building on other people's work) and found some interesting results.
It is worth noting that these articles are intended 'for dummies' and are definitely written by a dummy; I am by no means a computer programmer or literary scholar.

# Getting a gold standard text

The first problem I encountered, and the topic of this first article, concerns getting a digital version of the hand annotated text by Robinson. This is more difficult than it may seem. Although an ebook version of this text exists, text mining techniques can't deal with the e-book formats (like .azw or .epub) used by Amazon or Google. In order to make Robinson's annotation readable by computers we would need to convert his text into programmable objects. One of the simplest ways to do this would be to create two lists (or *arrays* in programmer talk): one list that splits up the novel into stretches that are written by Mary and Percy respectively, and a second list with the author's names that correspond to those stretches of text. For example, the start of Chapter 14 (in the picture above) would be represented as follows:

| Array 1: | `nothing is more painful` | `than the dead calmness of inaction and certainty which,` | `when the mind ...` |
| --- | --- | --- | --- |
| __Array 2:__ | `Mary Shelley` | `Percy Shelley` | `Mary Shelley` |

Besides, it would probably be illegal to turn the e-book version into raw text and redistribute it online.
