import re
from pathlib import Path

re_line = re.compile(r"(\d*)\.?\s([\.\w]+)\s(.*$)")


def escape_tex_line(line: str):
    return line.replace("_", r"\_")


def unpack_table_entry(line: str):
    "Unpacks a table line entry into the number, contributor name, and the entry value"
    words = line.split()
    num = words[0].replace(".", "").strip().lstrip("0")
    contributor = escape_tex_line(words[1].strip())
    content = escape_tex_line(
        " ".join(words[2:]).strip().replace("[", r"\subtable{").replace("]", "}")
    )
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
    TABLE_HEADER = """\\begin{{DndTable}}[header={table_name}]{{c X}}
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

    def parse_table_entry(self, output_file, line):
        number, _, content = unpack_table_entry(line)
        self._emit_table_row(output_file, content, number)

    def emit_main_file_footer(self, f):
        pass


# Yes, I know have a bad smell from the duplicated code.
# I could refactor into a better design, but I seriously don't care that much.
# This is not a critical library or anything.
class ContributorsAsColumnLineParser:
    "Line parser that outputs contributors as a third table column"

    TABLE_HEADER = """\\begin{{DndTable}}[header={table_name}]{{c X X}}
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

    def parse_table_entry(self, output_file, line):
        number, contributor, content = unpack_table_entry(line)
        self._emit_table_row(output_file, content, contributor, number)

    def emit_main_file_footer(self, f):
        pass


class TableParser:
    "The common parsing algorithm. This code is invariant across all output options."

    def __init__(
        self, line_parser, input_directory="./text/", output_directory="./tex"
    ):
        self._input_directory = Path(input_directory)
        self._output_directory = Path(output_directory)
        self.line_parser = line_parser

    def parse(self):
        self._output_directory.mkdir(exist_ok=True)

        # setup the main tex include file
        main_include_path = Path.joinpath(self._output_directory, "all_tables.tex")

        # iterate and parse all input table files
        with open(main_include_path, "w") as main_include:
            for input_path in sorted(self._input_directory.glob("*.txt")):
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
                        for line in input_file:
                            self.line_parser.parse_table_entry(
                                output_file, line
                            )

                    self.line_parser.parse_table_footer(output_file)

            self.line_parser.emit_main_file_footer(main_include)


# Refactoring to use a template method and dependency injection approach to
# support various output options
if __name__ == "__main__":

    # parser = TableParser(IgnoreContributorsLineParser())
    parser = TableParser(ContributorsAsColumnLineParser())
    parser.parse()
