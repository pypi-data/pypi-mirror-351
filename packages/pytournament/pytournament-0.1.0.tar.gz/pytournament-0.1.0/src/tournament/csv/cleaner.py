import argparse
import re


def remove_trailing_semicolons(input_file: str, output_file: str) -> None:
    """
    Removes all trailing semicolons from each line in the input file
    and writes the cleaned lines to the output file.

    Args:
        input_file (str): Path to the input file.
        output_file (str): Path to the output file.
    """
    with (
        open(input_file, "r", encoding="utf-8") as infile,
        open(output_file, "w", encoding="utf-8") as outfile,
    ):
        for line in infile:
            # Use regex to remove all trailing semicolons
            cleaned_line = re.sub(r";+$", "", line.rstrip()) + "\n"
            # Write the cleaned line to the output file
            outfile.write(cleaned_line)


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean or modify CSV files.")
    parser.add_argument(
        "operation",
        choices=["remove_trailing_semicolons"],
        help="The cleaning operation to perform.",
    )
    parser.add_argument("input_file", help="Path to the input CSV file.")
    parser.add_argument("output_file", help="Path to the output CSV file.")
    args = parser.parse_args()

    if args.operation == "remove_trailing_semicolons":
        remove_trailing_semicolons(args.input_file, args.output_file)
        print(f"Trailing semicolons removed. Cleaned file saved to {args.output_file}")
    else:
        # print the right usage message:
        parser.print_help()


if __name__ == "__main__":
    main()
