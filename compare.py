import argparse

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
input_file = args['input_file']
output_file = args['output_file']

if __name__ == '__main__':
    print(input_file, output_file)