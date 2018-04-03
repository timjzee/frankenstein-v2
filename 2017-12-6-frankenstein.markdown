---
layout: post
title:  "Hacking Frankenstein (Part 1): A gold standard"
date:   2017-12-6 00:14:38 +0100
categories: linguistics literature text-mining
---

A few years ago—when I still wanted to major in English literature—I decided to read *Frankenstein*. Apart from being vaguely interested in the story, I was mainly drawn to it because of the weird 19th century Romantic drama surrounding its inception. Long story short, Percy, a 22 year old poet, meets Mary, the 17 year old daughter of a prominent intellectual; Percy deserts his pregnant wife to party with Mary in continental Europe, where Mary participates in a ghost story competition and writes *Frankenstein*; Back in England, Percy edits and publishes *Frankenstein* before drowning in a lake.

Intrigued, I looked for an annotated edition of the novel that would provide additional details and context to the creation of Frankenstein. I quickly settled on this edition:

![alt text](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png "Logo Title Text 1")

Interestingly, this edition contains two versions of the story: one version reprints the text of the first edition of the novel from 1818, and the other version was composed by the editor from handwritten drafts of *Frankenstein* that are held at the Oxford University library. However, the editor hadn't stopped there. He had marked Percy's contributions to this draft text in italics, using regular font for Mary's writing:

![alt text](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png "Logo Title Text 1")

The editor had based this annotation on a painstaking analysis of the different handwritings and types of ink that were used in the drafts.
These annotations definitely contributed to my reading experience, but after finishing the novel I quickly forgot about them. Last year, however, I was suddenly reminded of them when I was panicking to find a topic for a term paper in a course I was taking. The course, which was called "Text mining", was about the application of computer algorithms (or to use another fancy term "machine learning") to 'mine' interesting information from text sources. The course had briefly touched on authorship attribution: using algorithms to determine the author of a text. I wondered whether it would be possible to use algorithms to arrive at an annotation of *Frankenstein* that was similar to the hand annotation by Robinson.

During my course project, I encountered a number of problems and questions. In this three part series of articles I'll describe how I eventually solved these problems (by building on other people's work) and found some interesting results.
It is worth noting that these articles are intended 'for dummies' and are definitely written by a dummy. I am by no means a good programmer or literary scholar. 
