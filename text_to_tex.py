import argparse
import re
from pathlib import Path

re_line = re.compile(r"(\d*)\.?\s([\.\w]+)\s(.*$)")


def escape_tex_line(line: str):
    return line.replace("_", r"\_").replace("&", "\&")


def unpack_table_entry(line: str, escape: bool = True):
    "Unpacks a table line entry into the number, contributor name, and the entry value"
    words = line.split()
    num = words[0].replace(".", "").strip().lstrip("0")
    if escape:
        contributor = escape_tex_line(words[1].strip())
        content = escape_tex_line(
            " ".join(words[2:]).strip().replace("[", r"\subtable{").replace("]", "}")
        )
    else:
        contributor = words[1].strip()
        content = " ".join(words[2:]).strip()

    return num, contributor, content

    # The regex approach is more brittle than the simple text processing version
    """
    match = re_line.match(line)
    if match:
        # extract values
        num, contributor, content = match.groups()

        # clean values
        try:
            num = int(num)
        except ValueError:
            num = num.strip()

        contributor = escape_tex_line(contributor)
        content = escape_tex_line(content.replace("[", r"\subtable{").replace("]", "}"))

        return num, contributor.strip(), content.strip()
    else:
        return None, None, line
    """


class IgnoreContributorsLineParser:
    "Line parser that completely ignores contributor information"

    # TABLE_HEADER is used as a format pattern, so curly braces have to be escaped
    TABLE_HEADER = """
\\subsubsection{{{table_name}}}
\\begin{{DndTable}}[]{{c X}}
\\textbf{{Roll}} & \\textbf{{Result}} \\\\\n"""

    def _emit_table_header(self, f, name):
        f.write(self.TABLE_HEADER.format(table_name=escape_tex_line(name)))

    def _emit_table_row(self, f, content: str, number: int = 1):
        f.write(f"    {number} & {content} \\\\\n")

    def parse_table_footer(self, f):
        f.write("\\end{DndTable}")

    def parse_first_line(self, output_file, line):
        table_name = line.strip()
        self._emit_table_header(output_file, table_name)

    def parse_table_entry(self, output_file, line, row_num):
        number, _, content = unpack_table_entry(line)
        number = row_num if row_num else number
        self._emit_table_row(output_file, content, number)

    def emit_main_file_footer(self, f):
        pass


# Yes, I know have a bad smell from the duplicated code.
# I could refactor into a better design, but I seriously don't care that much.
# This is not a critical library or anything.
class ContributorsAsColumnLineParser:
    "Line parser that outputs contributors as a third table column"

    TABLE_HEADER = """
\\subsubsection{{{table_name}}}
\\begin{{DndTable}}[]{{c X l}}
\\textbf{{Roll}} & \\textbf{{Result}} & \\textbf{{Contributor}}\\\\\n"""

    def _emit_table_header(self, f, name):
        f.write(self.TABLE_HEADER.format(table_name=escape_tex_line(name)))

    def _emit_table_row(self, f, content: str, contributor: str, number: int = 1):
        f.write(f"    {number} & {content} & {contributor}\\\\\n")

    def parse_table_footer(self, f):
        f.write("\\end{DndTable}")

    def parse_first_line(self, output_file, line):
        table_name = line.strip()
        self._emit_table_header(output_file, table_name)

    def parse_table_entry(self, output_file, line, row_num):
        number, contributor, content = unpack_table_entry(line)
        number = row_num if row_num else number
        self._emit_table_row(output_file, content, contributor, number)

    def emit_main_file_footer(self, f):
        pass


class ContributorsAsAppendixLineParser:
    "Line parser that outputs contributors as an appendix"

    def __init__(self):
        self.contributors = {}

    TABLE_HEADER = """
\\subsubsection{{{table_name}}}
\\begin{{DndTable}}[]{{c X}}
\\textbf{{Roll}} & \\textbf{{Result}}\\\\
"""

    def _emit_table_header(self, f, name):
        f.write(self.TABLE_HEADER.format(table_name=escape_tex_line(name)))

    def _emit_table_row(self, f, content: str, contributor: str, number: int = 1):
        f.write(f"    {number} & {content}$^{{{contributor}}}$\\\\\n")

    def parse_table_footer(self, f):
        f.write("\\end{DndTable}")

    def parse_first_line(self, output_file, line):
        table_name = line.strip()
        self._emit_table_header(output_file, table_name)

    def parse_table_entry(self, output_file, line, row_num):
        number, contributor, content = unpack_table_entry(line)
        number = row_num if row_num else number

        # generate and store the unique footnote number for each contributor
        if contributor not in self.contributors:
            self.contributors[contributor] = len(self.contributors) + 1

        contributor = self.contributors[contributor]

        self._emit_table_row(output_file, content, contributor, number)

    def emit_main_file_footer(self, f):
        """
        Emits the contributors chapter.
        Contains a nasty hack to split into multiple tex tables to workaround
        the fact that DndTable does not split over pages or columns.
        The max rows per table is hardcoded based on the current layouts and
        font sizes.
        """
        max_rows_per_table = 60
        row_count = 0
        table_closed = False  # tracks whether the current table is open or closed

        # Start the contributors chapter
        f.write("\\subsection{Contributors}\n")

        for contributor, n in self.contributors.items():
            # for n in range(500):
            #     contributor = str(n)

            # are we starting a new table?
            if row_count == 0:
                f.write("\\begin{DndTable}[]{c X}\n" "")
                table_closed = False

            f.write(f"    {n} & {contributor} \\\\\n")
            row_count += 1

            # is it time to close this table?
            if row_count > max_rows_per_table - 1:
                f.write("\\end{DndTable}\n")
                row_count = 0
                table_closed = True

        if not table_closed:
            f.write("\\end{DndTable}\n")


class TableParser:
    "The common parsing algorithm. This code is invariant across all output options."

    def __init__(
        self, line_parser, input_directory="./text/", output_directory="./tex"
    ):
        self._input_directory = Path(input_directory)
        self._output_directory = Path(output_directory)
        self.line_parser = line_parser

    def _get_input_files(self, sort_by_table_name: bool):
        the_files = list(self._input_directory.glob("*.txt"))
        if sort_by_table_name:
            always_first = None
            sorted_files = []
            # iterate the files and read first line
            for f in the_files:
                # take the always-first file out.
                if f.name[0:4] == "001_":
                    always_first = f
                else:
                    with open(f, "r") as file:
                        sorted_files.append((f, file.readline()))

            # we now have a list of tuples (file name, first line of file)
            # sort by first lines and use that sequence to order the file names
            the_files = [x[0] for x in sorted(sorted_files, key=lambda x: x[1])]
            if always_first:
                the_files.insert(0, always_first)

            return the_files

        else:
            return sorted(the_files)

    def parse(
        self,
        ignore_numbers: bool = True,
        sort_by_table_name: bool = False,
        sort_table_rows: bool = False,
    ):
        self._output_directory.mkdir(exist_ok=True)

        # setup the main tex include file
        main_include_path = Path.joinpath(self._output_directory, "all_tables.tex")

        # iterate and parse all input table files
        with open(main_include_path, "w") as main_include:
            for input_path in self._get_input_files(sort_by_table_name):
                print(f"* Processing {input_path}")

                # create the table tex file path
                output_tex = Path.joinpath(
                    self._output_directory, Path(input_path.name).with_suffix(".tex")
                )

                # add the current table to the main tex include file
                main_include.write(f"\\input{{{output_tex}}}\n")

                with open(output_tex, "w") as output_file:
                    with open(input_path) as input_file:
                        self.line_parser.parse_first_line(
                            output_file, input_file.readline()
                        )

                        # render table rows from each of the remaining lines
                        row_num = 1
                        lines = input_file.readlines()

                        # optionally sort the table rows
                        if sort_table_rows:
                            # unfortunately we have to unpack each line to sort by the entry
                            lines = sorted(
                                lines, key=lambda x: unpack_table_entry(x, False)[2]
                            )

                        # parse the table rows
                        for line in lines:
                            # print(line)
                            self.line_parser.parse_table_entry(
                                output_file, line, row_num if ignore_numbers else None
                            )
                            row_num += 1

                    self.line_parser.parse_table_footer(output_file)

            self.line_parser.emit_main_file_footer(main_include)


# Refactoring to use a template method and dependency injection approach to
# support various output options
if __name__ == "__main__":

    # command line options
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "-i",
        "--ignore-numbers",
        action="store_true",
        help="Ignore the numbers in the text files",
    )
    arg_parser.add_argument(
        "-s",
        "--sort-by-table-name",
        action="store_true",
        help="Sort the tables alphabetically by table name instead of file name. All tables except 001 will be sorted.",
    )
    arg_parser.add_argument(
        "-t",
        "--sort-table-rows",
        action="store_true",
        help="Sort the table rows alphabetically instead of keeping the text file order",
    )
    group = arg_parser.add_mutually_exclusive_group()
    group.add_argument(
        "-n", "--no-contrib", action="store_true", help="Omit contributors"
    )
    group.add_argument(
        "-c",
        "--contrib-column",
        action="store_true",
        help="Contributors in table columns",
    )
    group.add_argument(
        "-a",
        "--contrib-appendix",
        action="store_true",
        help="Contributors in an appendix",
    )
    args = arg_parser.parse_args()

    if args.contrib_column:
        print("Generating tables with contributors in a table column")
        parser = TableParser(ContributorsAsColumnLineParser())
    elif args.contrib_appendix:
        print("Generating tables with contributors in an appendix")
        parser = TableParser(ContributorsAsAppendixLineParser())
    else:
        print("Generating tables without contributor information")
        parser = TableParser(IgnoreContributorsLineParser())

    parser.parse(args.ignore_numbers, args.sort_by_table_name, args.sort_table_rows)
