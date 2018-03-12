# frankenstein-v2

## Acknowledgements and License information
- Metadata from Shelley-Godwin Archive: Creative Commons 1.0
- Text processing: Datamuse API

## About
This project presents an accessible gold standard text for the authorship attribution of the 19th century novel *Frankenstein*. The text is constructed from the annotated draft from the Shelley-Godwin Archive (SGA). The TEI .xml files used in the SGA are multifunctional and as such they are not optimized for any single purpose. The files provided in this repository have been constructed with authorship attribution in mind. Some features:
- Two .json list objects: one with stretches of subsequent text by the same author and one with the corresponding authors
- Intelligent word parsing using the Datamuse API and dozens of heuristic rules (unfortunately the SGA annotations do not allow for trivial word parsing; as a result the text in this repo contains fewer parsing errors than the reading text on the SGA website)

## To do:
- ~~implement cross-linear modifications (not implemented by website), e.g *their experience & to feelings one another* in 57-0019, see also guidelines~~
  - ~~for deletions it doesn't matter, but for additions it does~~
  - does this occur across pages? (implemented but not tested)
  - needs more testing
- ~~change join/separate algorithm to product of first and second part 56-0022: *in* + *dulged* should be *indulged* because score of dulged is 0~~
- ~~change word scoring algorithm, final score is product of score and frequency instead of average. This prevents the selection of non-words such as *atthis* in stead of *at* and *this* in 56-0032~~
  - ~~fall back on old algorithm if the best score is 0 (due to one word with a score of 0)~~
- ~~add support for subzones from other pages: e.g. `<anchor xml:id="c56-0089.01"/>` in 56-0088 refers to `<addSpan corresp="#c56-0089.01" spanTo="#c56-0089.02"/>` in 56-0089~~
- ~~get latest page files from SGA repo~~
- process text:
  - if curline_par is a number and preceded by a non-number insert a space, e.g. in 58-0001 *th* + *17* --> joined
  - ~~remove redundant newlines, spaces~~
  - ~~handle EOL hyphens~~
  - handle EOL + SOL, e.g. in 56-0068, *in-* + *-supportable*; and SOL hyphens, e.g. in 56-0115, *dis* + *-turb*
  - handle capitalization, punctuation
    - a full stop should be added when the first word of a line starts with an uppercase letter that is not *I*, a name, or part of initials / a title
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
    - .json format
- ~~Implement limitations in volume files:~~
  - ~~finish adding fromLine and toLine attributes in volume files~~
  - ~~line counter for use with fromLine and toLine attributes~~
- ~~text within < hi > should not be printed if in < metamark >~~
- ~~add support for delspans that are initiated within other delspans~~
- processLine should probably refactored so it differentiates between different levels of tags, but then we need a solution for tail text
- Do we want to correct shortcomings/mistakes of tei annotations or do we just follow the SGA reading text?
  - using metamarks rather than anchors to reference displacements from another zone e.g. ~~56-0011 and 57-0103 '56-0012', '56-0025', '56-0031', '56-0039', '56-0045', '56-0048', '56-0058', '56-0059', '56-0060', '56-0063', '56-0069', '56-0071', '56-0071', '56-0076', '56-0077', '56-0079', '56-0082', '56-0083', '56-0087', '56-0088', '56-0093', '56-0099', '56-0111', '56-0112', '56-0113', '56-0115', '57-0005', '57-0010', '57-0012', '57-0021', '57-0022', '57-0037', '57-0037', '57-0038', '57-0040', '57-0041', '57-0041', '57-0042', '57-0049', '57-0059', '57-0074', '57-0098', '57-0159', '57-0161', '57-0169', '57-0183', '57-0183'~~
