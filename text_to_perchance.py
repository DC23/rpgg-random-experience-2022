import argparse
from pathlib import Path


def unpack_table_entry(line: str):
    "Unpacks a table line entry into the number, contributor name, and the entry value"
    words = line.split()
    num = words[0].replace(".", "").strip().lstrip("0")
    contributor = words[1].strip()
    content = " ".join(words[2:]).strip()
    return num, contributor, content


class PerchanceLineParser:
    "Line parser that outputs tables in Perchance format"

    FIRST_FILE_TABLE_HEADER = f"title\n  {{name}}\n\noutput\n"
    TABLE_HEADER = f"{{name}}\n"

    def __init__(self):
        pass

    def _escape_title(self, s:str):
        # Yes, it does nothing yet
        return s

    def _escape_line(self, s:str):
        # Yes, it does nothing yet
        return s

    def _emit_table_header(self, f, name, first_table:bool=False):
        name = self._escape_title(name)
        if first_table:
            f.write(self.FIRST_FILE_TABLE_HEADER.format(name=name))
        else:
            f.write(self.TABLE_HEADER.format(name=name))

    def _emit_table_row(self, f, content: str, contributor: str, number: int = 1):
        f.write(f"  {self._escape_line(content)}\n")

    def parse_table_footer(self, f):
        f.write("\n")

    def parse_first_line(self, output_file, line, first_file:bool=False):
        table_name = line.strip()
        self._emit_table_header(output_file, table_name, first_table=first_file)

    def parse_table_entry(self, output_file, line):
        number, contributor, content = unpack_table_entry(line)
        self._emit_table_row(output_file, content, contributor, number)

    def emit_main_file_footer(self, f):
        pass


class TableParser:
    "The common parsing algorithm. This code is invariant across all output options."

    def __init__(
        self, line_parser, input_directory="./text/", output_directory="./perchance/"
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
            the_files = [x[0] for x in sorted(sorted_files, key=lambda x: x[1].lower())]
            if always_first:
                the_files.insert(0, always_first)

            return the_files

        else:
            return sorted(the_files)

    def parse(self):
        self._output_directory.mkdir(exist_ok=True)

        # create the output file path
        output_path = Path.joinpath(self._output_directory, "perchance.txt")

        with open(output_path, "w") as output_file:

            # The first file needs special handling
            first = True

            # iterate and parse all input table files
            for input_path in self._get_input_files(True):
                print(f"* Processing {input_path}")

                with open(input_path) as input_file:
                    self.line_parser.parse_first_line(
                        output_file, input_file.readline(), first_file=first
                    )

                    # render table rows from each of the remaining lines
                    lines = input_file.readlines()

                    # parse the table rows
                    for line in lines:
                        # print(line)
                        self.line_parser.parse_table_entry(output_file, line)

                self.line_parser.parse_table_footer(output_file)

                first = False


if __name__ == "__main__":

    # command line options
    # arg_parser = argparse.ArgumentParser()

    parser = TableParser(PerchanceLineParser())
    parser.parse()
