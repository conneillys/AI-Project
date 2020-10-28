REM Needs pandoc, miktex and to be run as administrator

pandoc Proposal.md -o Proposal.pdf -V geometry:margin=1in -V colorlinks -V urlcolor=NavyBlue --reference-location=block --reference-links -f markdown_github+footnotes+autolink_bare_uris 