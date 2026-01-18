Repo for analyzing GDPR decisions made by the CJEU in order to draw novel academic insights, according to highest academic rigour standards. Target publication: academic. Approach: expert data scientist legal emiprical.
Files/folders:
/cases-metadata: a file with an overview of all CJEU decisions in the dataset -- name of parties, filename (albeit old folder reference), URLS, articles which decision modifies according to EURLEX
/decisions: decisions as MD files. NB: may contail some odd/Unicode errors making search/replace hard.
coding-agent-instructions.md: our questionnaire filled out by the coders. 43 questions in total. MUST read in full to understand the repo.
/coded-decisions: each file contains lines with answers. Where a judgement contains multiple rulings, possibly more lines (see coding instructions).  each file which is under coded decisions corresponds to MD file of a decision itself in name, plus _coded appended: eg C-00-00.md in /decisions is full judgement text, C-00-00_coded.md in /coded-decisions is a populated answer form. see C-17-22_coded.md for an example.
/scripts will contain data processing scripts - for now, for cleanup. parser.py parses coded decisions into JSON/CSV/DB formats. for now, output is stored in /parsed-coded. viewer.html is meant to facilitate easy data exploration, although it misses export feature.
