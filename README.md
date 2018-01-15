# frankenstein-v2

## next steps:
- add text from <unclear> tags
- ~~add functionality for references to displaced text within same zone:~~
  - ~~scan zone for displacements in processZone,~~
    - ~~look for metamark function="displacement" with an xml:id~~
    - ~~put displacement IDs into list~~
  - ~~check for addSpans with those IDs in both processLine and processZone~~
  - ~~if addSpan with displacement ID is found : put ID in delspan_id, delspan = True and break out~~
  - ~~if metamark="displacement" with id (in either line or zone) is found, processSubZone~~
- implement hand attribution
  - Types:
    - `<add place="superlinear" hand="#pbs">power</add>`
    - `<handShift new="#pbs"/>`
    - `<addSpan hand="#pbs" spanTo="#c56-0026.05"/>`
  - output:
    - list that consists of consecutive fragments with the same hand
    - list with same amount of elements and hand labels that correspond to fragments
    - .json format
  - Implement limitations in volume files:
    - ~~finish adding fromLine and toLine attributes in volume files~~
    - line counter for use with fromLine and toLine attributes
    - if (line < fromLine or line > toLine) then ignore-line = True
    - else ignore-line = False
  - ~~text within <hi> should not be printed if in <metamark>~~
  - process text:
    - remove redundant newlines, spaces
    - handle EOL hyphens
    - handle capitalization
