import argparse
import ast


def get_file_pairs(input_file):
    """Returns a list of filename pairs from each row of input_file"""
    with open(input_file, 'r') as file:
        file_pairs = []
        line_counter = 0
        for line in file:
            line_counter += 1
            file_pair = line.split()
            try:
                file_pairs.append((file_pair[0], file_pair[1]))
            except IndexError:
                print(
                    "INCORRECT INPUT in file: {}, line: {}".format(
                        input_file,
                        line_counter,
                    ))
                continue
    return file_pairs


def main():
    arg_parser = argparse.ArgumentParser(
        description="Checks python code for plagiarism")

    arg_parser.add_argument("input_file",
                            metavar="INPUT",
                            help="File with pairs of filenames required for check",
                            )
    arg_parser.add_argument("output_file",
                            metavar="OUTPUT",
                            help="Output file for similarity score for each pair",
                            )

    args = vars(arg_parser.parse_args())
    input_file = args["input_file"]
    output_file = args["output_file"]
    compare_file_pairs = get_file_pairs(input_file)


if __name__ == "__main__":
    main()
