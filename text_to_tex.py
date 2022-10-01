from pathlib import Path

TABLE_HEADER = """\\begin\\{{DndTable}}[header={table_name}]{{c X}}
    \\textbf{{Roll}} & \\textbf{{Result}} \\\\ \n"""
TABLE_FOOTER = "\\end{{DndTable}}"


def emit_table_header(f, name):
    f.write(TABLE_HEADER.format(table_name=name))


# $1$ &  The temporal conflict between \st{Faction} and \st{Faction} brought on by the
def emit_table_row(f, line: str, number: int = 1):
    line = line.replace("[", r"\subtable{").replace("]", "}")
    f.write(f"    {number} & {line}\n")


def emit_table_footer(f):
    f.write(TABLE_FOOTER)


if __name__ == "__main__":
    # ensure output directory exists
    output_directory = Path("./output")
    output_directory.mkdir(exist_ok=True)

    for input_path in Path("./text_tables/").glob("*.txt"):
        # create the output file
        output_path = Path.joinpath(
            output_directory, Path(input_path.name).with_suffix(".tex")
        )
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
