# frankenstein-v2

## Acknowledgements and License information
- Metadata from Shelley-Godwin Archive: Creative Commons 1.0
- Text processing: Datamuse API

## About
The main objective of this project is to provide an accessible gold standard text for the authorship attribution of the 19th century novel *Frankenstein*. The text is constructed from the hand annotations of the draft in the Shelley-Godwin Archive (SGA). The TEI .xml files used in the SGA are multifunctional and as such they are not optimized for any single purpose. The files provided in this repository have been constructed with authorship attribution in mind. Some features:
- Two .json list objects: one with stretches of subsequent text by the same author and one with the corresponding authors
- Intelligent word parsing using the Datamuse API and dozens of heuristic rules (unfortunately the SGA annotations do not allow for trivial word parsing; as a result the text in this repo contains fewer parsing errors than the reading text on the SGA website)

As a secondary objective this project presents an initial comparison between a stylometric analysis of *Frankenstein* based on other work by Mary and Percy Shelley and the gold standard hand annotation. The analysis will consist of the following:
- Principal Component Analysis: Influential words in the PCA of other work by Mary and Percy Shelley can be compared to the relative frequency of those words in parts of *Frankenstein* written by Mary and Percy respectively.
- A rolling classification of *Frankenstein* can be attempted and compared to the hand annotation.

The tertiary objective of this project relies on the outcome of the rolling classification of *Frankenstein*. Initial tests show that a rolling classification with sample size of 1000 words and an overlap of 900 identifies an authorial shift to Percy towards the end of the novel. This is in line with the hand attribution by Charles Robinson. Interestingly, the rolling classification does not identify this change at a sample size of 5000 words and an overlap of 4500. This suggests that larger sample size may not always be better in authorship attribution of collaborative texts due to a decrease in resolution at larger sample sizes. In other words, smaller sample sizes may be used to increase resolution at the cost of accuracy.

## Notes on composition
The presented text has been composed so as to resemble the 1818 edition of the novel while maintaining insight in the contribution of Percy Shelley. As such, the text is taken from the 1816-1817 draft up until the last few pages of Chapter 18. From that point onwards the text has been taken from the Fair Copy so that Percy's contributions to those final pages are reflected in the final text. As Robinson (2008, p. 29) notes:

>As we move from the extant *1816-1817 Draft* to the first edition of *1818*, we note the following differences: minor changes that Mary Shelley made to the Draft when she fair-copied it; some substantial changes that Percy Shelley made to the Draft when he wrote out the last twelve-and-three-quarter pages of the Fair Copy;

Furthermore, as Robinson notes (2008, p. 41), the following sections are missing from the 1816-1817 draft:

>from Volume I, the four introductory letters from Walton to his sister Margaret and the first part of Chapter 1; and from Volume II almost half of Chapter 3 and all of Chapter 4.

I have chosen not to replicate these sections from the 1818 version as we do not know who wrote them.

## To do (crucial items in __bold__):
- implement transpositions e.g. c57-0157, c57-0179, c57-0074, c57-0043, c56-0108, c56-0038
  - __needs more testing; check whether I didn't screw up subzone processing__
  - ~~transposition list should be made when a zone is first processed~~
  - ~~when an element or line is encountered with an xml:id in the transposition list~~
    - ~~the contents of that element should not be processed~~
    - ~~the contents of the element corresponding to the first id in the transposition list should be processed~~
      - ~~if the element has a spanTo processing follows the subzone routine~~
      - ~~else (element is a line) --> processLine~~
    - ~~the first id in the transposition list should be moved~~
    - ~~if the original element has a spanTo~~
      - ~~delspan = True~~
      - ~~delspan_id = spanTo id~~
    - ~~else (original element is a line) --> nothing~~
- __displacement not processed correctly in c56-0108 (see picture in article)__
- __why no revision in 57-0097 *he* + *f* + *inds*__
- illustrate/plot sampling effect using actual results (proportion of pbs classifications at different sample sizes)
- check whether macroF1 is better for smaller sample sizes (1500) than larger sample size (4000)
  - should be true if larger sample sizes result in classification that is identical to baseline (majority) classification, because performance is already better than baseline
  - note that macroF1 gives equal importance to performance in both classes, which does not flatter the performance of unbalanced datasets
- add n-gram features
- add POS features
- ~~__implement more intelligent splitting rule of in postProcessing.py and rollingStylo.R__~~
- *morning* is separated into *mor* and *ning* in c57-0101
- ~~implement log file~~
- ~~__composition of final text that resembles 1818 edition while maintaining insight in hand shifts: ch 18 of vol II to c57-0180 element 12 --> ch 7 of vol III from c58-0047 element 7__~~
- implement a check on number of Datamuse API calls that pauses the script for 24 hours
  - record and update daily api calls in a file (so the script "remembers")
- ~~ignore chapter headings, e.g. 56-0081~~
- ~~__remove quotation marks that are within words due to EOL split, e.g. in 56-0068__~~
- __How do we handle notes by the compositor, e.g. 58-0037__
  - ~~use milestone annotation as delspan~~
  - replace all comp annotations with mws annotations in post processing
- add exception list for words that have a deviant spellings/unique words, e.g. *massercring* in 57-0039, *interspered* in 56-0122, *precipieces* in 56-0116, *dissapeared* in c56-0083
- add 1818 edition lookup to regular join/separate algo?
- ~~implement tail text of mod inside of mod, e.g. 57-0039 or mod inside of add, currently only the order of non-hierarchical tags within a mod are handled correctly. What happens in 57-0039 is that only the tail of the nested mod gets printed because all child tags of the nested mod are only checked against the nested mod (the first mod upstream is used)~~
  - ~~include add as a possible upstream parent tag~~
  - ~~for each tag that is the final tag in its immediate parent:~~
    - ~~print the tail text of the immediate parent (as we do now), but also~~
    - ~~check whether the parent is itself nested in add/mod/hi, and if so~~
    - ~~check its position within that parent by comparing the children of the nested add/mod/hi with the children of the parent add/mod/hi:~~
        - ~~if the final tags are identical, the tail text of the parent add/mod/hi should also be printed~~
        - ~~if the final tags are not identical, we don't have to do anything as the printing of the tail text will be handled when the final child (a sister to the nested add/mod/hi) is encountered~~
- ~~implement restoration, see guidelines~~
  - ~~text in non-del tags within a del within a restore (implemented but not tested)~~
  - ~~text in del tags within a restore (implemented and tested)~~
  - ~~text in non-del tags within delSpan? (not encountered/implemented)~~
  - ~~pages: '56-0051', '56-0106', '56-0114', '56-0122', '57-0033', '57-0039'(2x), '57-0057', '57-0082', '57-0087'(2x), '57-0096', '57-0104', '57-0116', '57-0145'(2x), '57-0158', '57-0166'~~
- add fix for 56-0064?
- ~~implement cross-linear modifications (not implemented by website), e.g *their experience & to feelings one another* in 57-0019, see also guidelines~~
  - ~~for deletions it doesn't matter, but for additions it does~~
  - ~~does this occur across pages? (implemented but not tested)~~
  - ~~addspan tags, e.g 56-0056~~
  - ~~different zone on same page, e.g 56-0056~~
  - ~~implement printing of (tail)text within children elements of `<add>` --> we need a processElement function which processes mod, add & hi elements~~
  - ~~ignore references to another zone, processing of this text is already handled by anchors~~
  - needs more testing, pages: '56-0011', '56-0005', '56-0006', '56-0008', '56-0014', '56-0010', '56-0022', '56-0034', '56-0038', '56-0075', '56-0079', '56-0082'(2x), '56-0084', '56-00104', '56-0110', '56-0113', '56-0116'(2x), '56-0128', '57-0013', '57-0015', '57-0019', '57-0031', '57-0030', '57-0039', '57-0043', '57-0045', '57-0070', '57-0077', '57-0111', '57-0146', '57-0147', '57-0148', '57-0168'
- ~~change join/separate algorithm to product of first and second part 56-0022: *in* + *dulged* should be *indulged* because score of dulged is 0~~
- ~~change word scoring algorithm, final score is product of score and frequency instead of average. This prevents the selection of non-words such as *atthis* in stead of *at* and *this* in 56-0032~~
  - ~~fall back on old algorithm if the best score is 0 (due to one word with a score of 0)~~
- ~~add support for subzones from other pages: e.g. `<anchor xml:id="c56-0089.01"/>` in 56-0088 refers to `<addSpan corresp="#c56-0089.01" spanTo="#c56-0089.02"/>` in 56-0089~~
- ~~get latest page files from SGA repo~~
- process text:
  - if curline_par is a number and preceded by a non-number insert a space, e.g. in 58-0001 *th* + *17* --> joined
  - if *th*, *rd*, *st*, *nd* is preceded by a number no space should be inserted
  - ~~remove redundant newlines, spaces~~
  - ~~handle EOL hyphens~~
  - ~~__handle EOL + SOL, e.g. in 56-0068, *in-* + *-supportable*; and SOL hyphens, e.g. in 56-0115, *dis* + *-turb*; in 58-0049, *hideous* + *-ness*__~~
  - __convert & to and in post processing__
  - handle capitalization, punctuation
    - a full stop should be added when the first word of a line starts with an uppercase letter that is not *I*, a name, or part of initials / a title
    - ~~a full stop should also be added before a milestone tag, which represent paragraph breaks~~
    - necessary for POS tagging
- ~~support processing of individual pages (for debugging purposes)~~
- maybe we need a double-checking mechanism after two consecutive JOIN/SEPARATE operations where the first operation's curline_part corresponds to the second operation's prevline_part
  - ~~e.g. in 56-0111 app-SEP-r-JOI-oached --> *app roached*, and~~
  - ~~e.g. in 56-0111 a-SEP-n-JOI-obscure --> *a nobscure* we check all possibilities once more~~
  - ~~implementation:~~
    - ~~register whether previous text also required a JOIN/SEPARATE operation in processText using a global variable~~
    - ~~if so, check whether there are any whitespaces in previous_addition~~
    - ~~if not, use regex to find the 'word' that precedes previous_addition in print_text~~
    - ~~get score for all combos: "a", "b", "c", "ab", "bc", "abc"~~
  - needs more testing / optimization / heuristics
    - ~~if multiple combos have a word with a 0-score, check whether 0-score words exist in previous print_text/1st edition, e.g. in 58-0001 *Lavenz* + *a* + *Geneva*, *Lavenza* (i.e. ab_c) should be chosen~~
      - ~~if for none of the 0-score combos, the 0-score word can be found in print_text/1st edition, fall back on the old algorithm~~
    - ~~if the abc-option has a score higher than a certain threshold, it should always be chosen, e.g. in 56-0036 *on* + *c* + *e* should become *once* rather than *on ce*~~
    - ~~handle punctuation marks or don't consider them in word look-up, e.g. *—"Dam* + *n* + *"the* in 56-0068~~
    - maybe if part_a consists of an uppercase letter that is not I, we should not go through revision process, e.g. *Lavenza* in c58-0001 (names are not well recognized in Datamuse) or *M* + *r* + *.* --> *M r.* in 56-0068.
    - ~~find heuristic that turns *have* + *g* + *one* into *have gone* rather than *have g one* in 56-0032~~
      - ~~check for single consonant in "a" and "b" parts~~
      - ~~if single consonant in "a", then "a_b_c" and "a_bc" are no longer an option~~
      - ~~if single consonant in "b" and "a" score is better than "ab" and "abc" score, then "a_bc" is the only option~~
    - ~~find heuristic that turns *by* + *the* + *desire* into *by the desire* rather than *bythe desire* in 56-0012~~
      - ~~solved through change in scoring algorithm (product instead of average)~~
- ~~printing of tail text needs further adjustment: *Laavenz* instead of *Lavenza* in c58-0001 (nested `<hi>` tags) or the *r* of *Mr* ending up as *M Krempe commenced ran eulogy of himself* in 56-0068~~
- check attribution accuracy
- optimize dataMuse calls
  - word definitions perhaps use `&md=d` to only give scores > 0 to words which have a definition
  - ~~In 56-0028 *they* is split up into *the* and *y* due to higher score of *the* compared to *they*. By incorporating frequency in algorithm this can be prevented: `sp=they&md=f` > `sp=the&md=f` & `sp=y&md=f`~~
  - word context:
    - `sp=sametime` has a higher score than the mean of `sp=same` and `sp=time`, but it has a lower score than the mean of `sp=same&rc=time` and `sp=time&lc=same`
    - ~~maybe even use the word before prevline_part: in 56-0022 the mean score of `sp=be` and `sp=en` is higher than the score of `sp=been`, but when we include the previous word *have* as context, `sp=been&lc=have` has a much higher score than `sp=be&lc=have`. Same with `sp=me&lc=given` and `sp=mean&lc=given` when considering *me* + *an* in 56-0022~~
      - ~~first get left context~~
      - ~~make left context an optional parameter in callDatamuse, so that we don't have to implement it in double-checking mechanism yet~~
  - ~~if curline_part ends in a punctuation mark, ignore that mark when calling datamuse (this prevents incorrect separations)~~
- ~~add text from `<unclear>` and `<damage>` (e.g. 57-0111)~~ and `<retrace>` (e.g. 57-0013) tags
  - ~~__should we process text from `<unclear>`? See example in guidelines__~~
    - ~~only if text is 1 character (these are punctuation marks)~~
    - ~~words are ommitted in 1818 version~~
- ~~add functionality for references to displaced text within same zone:~~
  - ~~scan zone for displacements in processZone,~~
    - ~~look for metamark function="displacement" with an xml:id~~
    - ~~put displacement IDs into list~~
  - ~~check for addSpans with those IDs in both processLine and processZone~~
  - ~~if addSpan with displacement ID is found : put ID in delspan_id, delspan = True and break out~~
  - ~~if metamark="displacement" with id (in either line or zone) is found, processSubZone~~
- implement hand attribution
  - ~~who is *comp*, e.g. in 58-0002 --> TEI ODD: unknown compositor~~
  - ~~Types:~~
    - ~~`<add place="superlinear" hand="#pbs">power</add>` --> processLine~~
    - ~~`<handShift new="#pbs"/>` e.g. in 58-0053 --> processLine, processZone~~
    - ~~`<addSpan hand="#pbs" spanTo="#c56-0026.05"/>` --> processLine, processZone (in processed elements, delspan and skipped lines)~~
  - output:
    - ~~list that consists of consecutive fragments with the same hand~~
    - ~~list with same amount of elements and hand labels that correspond to fragments~~
    - ~~__.json format__~~
    - __ask how hand changes within a word should be handled__
      - allow them
      - or:
        - if only 1 hand change occurs within a word --> the whole word is attributed to the later hand
        - if the hand changes back again within a word, e.g. *[and ][t][his problem]* --> the whole word is attributed to the within-word change, e.g. *[and ][this][ problem]*
- ~~Implement limitations in volume files:~~
  - ~~finish adding fromLine and toLine attributes in volume files~~
  - ~~line counter for use with fromLine and toLine attributes~~
- ~~text within < hi > should not be printed if in < metamark >~~
- ~~add support for delspans that are initiated within other delspans~~
- ~~processLine should probably refactored so it differentiates between different levels of tags, but then we need a solution for tail text~~
  - ~~solution is a processElement function that is called from processLine and itself~~
    - ~~processline first creates a list of top-level children~~
    - ~~for each allowed element type processElement is called~~
    - ~~processElement does the following~~
      - ~~checks whether it is a del, metamark or anchor, if not~~
        - ~~print element text~~
        - ~~create a list of the element's children~~
        - ~~calls itself for each child~~
      - ~~prints element tail text~~
    - ~~this way we solve the tail text problem using recursion~~
    - ~~and we have an elegant solution for cross-line additions~~
    - ~~processLine still handles anchors, delspans etc. providing these are never nested~~
      - ~~anchors and metamarks are sometimes nested; addspan and delspan aren't~~
      - ~~anchors (for all functions) and metamarks need to be handled in processElement~~
  - Needs more testing:
    - ~~run through all files~~
    - hand attribution
      - ~~`<add>`~~
      - ~~`<addSpan>`~~
      - ~~`<handShift>`~~
      - test across pages
    - test restore
    - ~~cross-linear additions~~
    - ~~displacement~~
      - ~~different zone~~
      - ~~different page, 56-0028~~
      - ~~subzone~~
        - ~~on same page, examples: 57-0024, 57-0009~~
        - ~~on different page, examples 56-0088~~
- Do we want to correct shortcomings/mistakes of tei annotations or do we just follow the SGA reading text?
  - ~~using metamarks rather than anchors to reference displacements from another zone e.g. 56-0011 and 57-0103 '56-0012', '56-0025', '56-0031', '56-0039', '56-0045', '56-0048', '56-0058', '56-0059', '56-0060', '56-0063', '56-0069', '56-0071', '56-0071', '56-0076', '56-0077', '56-0079', '56-0082', '56-0083', '56-0087', '56-0088', '56-0093', '56-0099', '56-0111', '56-0112', '56-0113', '56-0115', '57-0005', '57-0010', '57-0012', '57-0021', '57-0022', '57-0037', '57-0037', '57-0038', '57-0040', '57-0041', '57-0041', '57-0042', '57-0049', '57-0059', '57-0074', '57-0098', '57-0159', '57-0161', '57-0169', '57-0183', '57-0183'~~
