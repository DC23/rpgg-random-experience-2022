from pathlib import Path


class IgnoreContributorsLineParser:
    "Line parser that completely ignores contributor information"

    # TABLE_HEADER is used as a format pattern, so curly braces have to be escaped
    TABLE_HEADER = """\\begin{{DndTable}}[header={table_name}]{{c X}}
        \\textbf{{Roll}} & \\textbf{{Result}} \\\\\n"""
    TABLE_FOOTER = "\\end{DndTable}"

    def _emit_table_header(self, f, name):
        f.write(self.TABLE_HEADER.format(table_name=name))

    def _emit_table_row(self, f, line: str, number: int = 1):
        line = line.replace("[", r"\subtable{").replace("]", "}")
        f.write(f"    {number} & {line} \\\\\n")

    def parse_table_footer(self, f):
        f.write(self.TABLE_FOOTER)

    def parse_first_line(self, output_file, line):
        table_name = line.strip()
        self._emit_table_header(output_file, table_name)

    def parse_table_entry(self, output_file, row_number, line):
        self._emit_table_row(output_file, line.strip(), row_number)

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
            for input_path in self._input_directory.glob("*.txt"):

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
                        row_number = 1
                        for line in input_file:
                            self.line_parser.parse_table_entry(
                                output_file, row_number, line
                            )
                            row_number += 1

                    self.line_parser.parse_table_footer(output_file)

            self.line_parser.emit_main_file_footer(main_include)


# Refactoring to use a template method and dependency injection approach to
# support various output options
if __name__ == "__main__":

    parser = TableParser(IgnoreContributorsLineParser())
    parser.parse()
