# R-A-N-D-O-M Design Experience 2022

## *Draft - Experience In Progress*

The compiled list of random tables from the RPG Geek 2022 [R-A-N-D-O-M Design
Experience](https://rpggeek.com/thread/2942480/2022-r-n-d-o-m-design-experience).

## Contributing

Fork the repo and submit pull-requests in the usual way.

### To Compile the Documents

**Requirements:**

* Python 3
* A working Tex environment. I use `texlive-full` in Ubuntu. If you know
what you are doing you could work out the required packages for a minimal Tex
environment by looking at `header.tex`.
* Install the [DND 5e LaTeX Template
package](https://github.com/rpgtex/DND-5e-LaTeX-Template).
* `Make` to use the `Makefile`. Or you could reconstruct the
command line from the Makefile, but remember to compile twice so the layout
and background images work correctly.

### To Add a New Table

1. Create a text file in the `text` directory. It should be named after the
   table name, but without spaces. It must end with the `.txt` extension.
2. In the new text file, the first line is the table name as it should appear in
   the PDF. Each subsequent line is the text for each entry in the table.
   References to sub-tables must have the sub-table name in square brackets.
   This will let you almost copy and paste directly from the RPGG thread.
3. Compile and test.

## Preview

![Preview image of the first page from the PDF](./preview.jpg)
