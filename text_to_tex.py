from pathlib import Path

# TABLE_HEADER is used as a format pattern, so curly braces have to be escaped
TABLE_HEADER = """\\begin{{DndTable}}[header={table_name}]{{c X}}
    \\textbf{{Roll}} & \\textbf{{Result}} \\\\\n"""
TABLE_FOOTER = "\\end{DndTable}"


def emit_table_header(f, name):
    f.write(TABLE_HEADER.format(table_name=name))


def emit_table_row(f, line: str, number: int = 1):
    line = line.replace("[", r"\subtable{").replace("]", "}")
    f.write(f"    {number} & {line} \\\\\n")


def emit_table_footer(f):
    f.write(TABLE_FOOTER)


# Yes, I could use click to add command line parsing and then make the Makefile
# much smarter but transforming all text files every build is so fast anyway.
if __name__ == "__main__":
    # ensure output directory exists
    output_directory = Path("./tex")
    output_directory.mkdir(exist_ok=True)

    main_include_path = Path.joinpath(output_directory, "all_tables.tex")

    with open(main_include_path, "w") as main_include:
        for input_path in Path("./text/").glob("*.txt"):
            # create the output file
            output_path = Path.joinpath(
                output_directory, Path(input_path.name).with_suffix(".tex")
            )

            # add this file to the main tex include file
            main_include.write(f"\\input{{{output_path}}}\n")

            with open(output_path, "w") as output_file:
                with open(input_path) as input_file:
                    # get the table name from the first line
                    table_name = input_file.readline().strip()
                    emit_table_header(output_file, table_name)

                    # render table rows from each of the remaining lines
                    row_number = 1
                    for line in input_file:
                        emit_table_row(output_file, line.strip(), row_number)
                        row_number += 1

                emit_table_footer(output_file)
