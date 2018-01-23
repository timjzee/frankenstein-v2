# frankenstein-v2

## Acknowledgements and License information
- Metadata from Shelley-Godwin Archive: Creative Commons 1.0
- Text processing: Datamuse API

## next steps:
- ~~support processing of individual pages (for debugging purposes)~~
- maybe we need a double-checking mechanism after two consecutive JOIN/SEPARATE operations where the first operation's curline_part corresponds to the second operation's prevline_part
  - e.g. in 56-0111 app-SEP-r-JOI-oached --> *app roached*, and
  - e.g. in 56-0111 a-SEP-n-JOI-obscure --> *a nobscure* we check all possibilities once more
  - implementation:
    - register whether previous text also required a JOIN/SEPARATE operation in processText using a global variable
    - if so, check whether there are any whitespaces in previous_addition
    - if not, use regex to find the 'word' that precedes previous_addition in print_text
    - get score for all combos: "a", "b", "c", "ab", "bc", "abc"
- printing of tail text needs further adjustment: *Laavenz* instead of *Lavenza* in c58-0001
- check attribution accuracy
- optimize dataMuse calls
  - ~~In 56-0028 *they* is split up into *the* and *y* due to higher score of *the* compared to *they*. By incorporating frequency in algorithm this can be prevented: `sp=they&md=f` > `sp=the&md=f` & `sp=y&md=f`~~
  - word context:
    - `sp=sametime` has a higher score than the mean of `sp=same` and `sp=time`, but it has a lower score than the mean of `sp=same&rc=time` and `sp=time&lc=same`
    - maybe even use the word before prevline_part: in 56-0022 the mean score of `sp=be` and `sp=en` is higher than the score of `sp=been`, but when we include the previous word *have* as context, `sp=been&lc=have` has a much higher score than `sp=be&lc=have`
  - ~~if curline_part ends in a punctuation mark, ignore that mark when calling datamuse (this prevents incorrect separations)~~
- add text from `<unclear>` and `<damage>` (e.g. 57-0111) tags
- ~~add functionality for references to displaced text within same zone:~~
  - ~~scan zone for displacements in processZone,~~
    - ~~look for metamark function="displacement" with an xml:id~~
    - ~~put displacement IDs into list~~
  - ~~check for addSpans with those IDs in both processLine and processZone~~
  - ~~if addSpan with displacement ID is found : put ID in delspan_id, delspan = True and break out~~
  - ~~if metamark="displacement" with id (in either line or zone) is found, processSubZone~~
- implement hand attribution
  - ~~Types:~~
    - ~~`<add place="superlinear" hand="#pbs">power</add>` --> processLine~~
    - ~~`<handShift new="#pbs"/>` --> processLine, processZone~~
    - ~~`<addSpan hand="#pbs" spanTo="#c56-0026.05"/>` --> processLine, processZone (in processed elements, delspan and skipped lines)~~
  - output:
    - ~~list that consists of consecutive fragments with the same hand~~
    - ~~list with same amount of elements and hand labels that correspond to fragments~~
    - .json format
- ~~Implement limitations in volume files:~~
  - ~~finish adding fromLine and toLine attributes in volume files~~
  - ~~line counter for use with fromLine and toLine attributes~~
- ~~text within < hi > should not be printed if in < metamark >~~
- process text:
  - ~~remove redundant newlines, spaces~~
  - ~~handle EOL hyphens~~
  - handle capitalization, punctuation
- ~~add support for delspans that are initiated within other delspans~~
