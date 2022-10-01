SHELL=/bin/sh
TEX_COMPILER=pdflatex
TEX_OPTIONS=--interaction=nonstopmode
TEX=$(TEX_COMPILER) $(TEX_OPTIONS)
TEX_FILES=$(wildcard tex/*.tex) RPGG_RANDOM_Design_Experience_2022.tex
TABLES_A4_CMD=$(TEX) -jobname=RPGG_RANDOM_Design_Experience_2022_a4 "\documentclass[bg=full, 10pt, a4paper, twoside, twocolumn, openany, nodeprecatedcode]{dndbook} \input{RPGG_RANDOM_Design_Experience_2022}"
TABLES_A4_PRINT_CMD=$(TEX) -jobname=RPGG_RANDOM_Design_Experience_2022_a4_print "\documentclass[bg=print, 10pt, a4paper, twoside, twocolumn, openany, nodeprecatedcode]{dndbook} \input{RPGG_RANDOM_Design_Experience_2022}"
TABLES_LETTER_CMD=$(TEX) -jobname=RPGG_RANDOM_Design_Experience_2022_letter "\documentclass[bg=full, 10pt, letterpaper, twoside, twocolumn, openany, nodeprecatedcode]{dndbook} \input{RPGG_RANDOM_Design_Experience_2022}"
TABLES_LETTER_PRINT_CMD=$(TEX) -jobname=RPGG_RANDOM_Design_Experience_2022_letter_print "\documentclass[bg=print, 10pt, letterpaper, twoside, twocolumn, openany, nodeprecatedcode]{dndbook} \input{RPGG_RANDOM_Design_Experience_2022}"


.SILENT:
.IGNORE:

all:  a4 a4_print letter letter_print preview

.PHONY: tex
tex:
	python text_to_tex.py

a4: tex $(TEX_FILES)
	$(TABLES_A4_CMD)
	$(TABLES_A4_CMD)

a4_print: tex $(TEX_FILES)
	$(TABLES_A4_PRINT_CMD)
	$(TABLES_A4_PRINT_CMD)

letter: tex $(TEX_FILES)
	$(TABLES_LETTER_CMD)
	$(TABLES_LETTER_CMD)

letter_print: tex $(TEX_FILES)
	$(TABLES_LETTER_PRINT_CMD)
	$(TABLES_LETTER_PRINT_CMD)

preview: ./RPGG_RANDOM_Design_Experience_2022_letter.pdf
	pdftoppm -jpeg -rx 120 -ry 120 -f 1 -l 1 RPGG_RANDOM_Design_Experience_2022_letter.pdf preview
	mv preview-1.jpg preview.jpg

.PHONY: clean
clean:
	echo Cleaning ...
	rm -rf *.gz *.aux *.log *.out *.bbl *.blg *.bak *.bcf *.xml *.toc tex/
	echo ... done
