SHELL=/bin/sh
TEX_COMPILER=pdflatex
TEX_OPTIONS=--interaction=nonstopmode
TEX=$(TEX_COMPILER) $(TEX_OPTIONS)
TEX_FILES=$(wildcard *.tex)
VERSION=0.1.0
TABLES_A4_CMD=$(TEX) -jobname=RPGG_RANDOM_Design_Experience_2022_a4_v$(VERSION) "\documentclass[bg=full, 10pt, a4paper, twoside, twocolumn, openany, nodeprecatedcode]{dndbook} \input{RPGG_RANDOM_Design_Experience_2022}"
TABLES_A4_PRINT_CMD=$(TEX) -jobname=RPGG_RANDOM_Design_Experience_2022_a4_print_v$(VERSION) "\documentclass[bg=print, 10pt, a4paper, twoside, twocolumn, openany, nodeprecatedcode]{dndbook} \input{RPGG_RANDOM_Design_Experience_2022}"
TABLES_LETTER_CMD=$(TEX) -jobname=RPGG_RANDOM_Design_Experience_2022_letter_v$(VERSION) "\documentclass[bg=full, 10pt, letterpaper, twoside, twocolumn, openany, nodeprecatedcode]{dndbook} \input{RPGG_RANDOM_Design_Experience_2022}"
TABLES_LETTER_PRINT_CMD=$(TEX) -jobname=RPGG_RANDOM_Design_Experience_2022_letter_print_v$(VERSION) "\documentclass[bg=print, 10pt, letterpaper, twoside, twocolumn, openany, nodeprecatedcode]{dndbook} \input{RPGG_RANDOM_Design_Experience_2022}"

.SILENT:
.IGNORE:

all:  a4 a4_print letter letter_print preview

a4: $(TEX_FILES)
	$(TABLES_A4_CMD)
	$(TABLES_A4_CMD)

a4_print: $(TEX_FILES)
	$(TABLES_A4_PRINT_CMD)
	$(TABLES_A4_PRINT_CMD)

letter: $(TEX_FILES)
	$(TABLES_LETTER_CMD)
	$(TABLES_LETTER_CMD)

letter_print: $(TEX_FILES)
	$(TABLES_LETTER_PRINT_CMD)
	$(TABLES_LETTER_PRINT_CMD)

preview: ./RPGG_RANDOM_Design_Experience_2022_letter_v$(VERSION).pdf
	pdftoppm -jpeg -rx 120 -ry 120 -f 1 -l 1 RPGG_RANDOM_Design_Experience_2022_letter_v$(VERSION).pdf preview
	mv preview-1.jpg preview.jpg

.PHONY: clean
clean:
	echo Cleaning ...
	rm -f *.gz *.aux *.log *.out *.bbl *.blg *.bak *.bcf *.xml *.toc
	echo ... done
