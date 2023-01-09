import argparse
import ast
from typing import Union


class DocstringDeleter(ast.NodeTransformer):
    """Deletes docstrings from class, function definitions"""

    def __visit_node(self, node):
        self.generic_visit(node)
        if ast.get_docstring(node) is not None:
            node.body.pop(0)
            if not node.body:
                node.body.append(ast.Pass())  # not creating invalid code
        return node

    def visit_ClassDef(self, node):
        return DocstringDeleter.__visit_node(self, node)

    def visit_AsyncFunctionDef(self, node):
        return DocstringDeleter.__visit_node(self, node)

    def visit_FunctionDef(self, node):
        return DocstringDeleter.__visit_node(self, node)


class OrderNormalizer(ast.NodeTransformer):
    """
    Rewrites modules, classes, functions body
    by ordering ast nodes by their types.
    Helps to work properly on code with shuffled lines
    """

    def __init__(self, sort_by_structure=False):
        self.sort_by_structure = sort_by_structure

    def __normalize_node(self, node: Union[
        ast.Module,
        ast.ClassDef,
        ast.FunctionDef,
        ast.AsyncFunctionDef,
    ]):
        nodes = {}
        for child in node.body:
            tp_name = str(type(child))
            if tp_name in nodes:
                nodes[tp_name].append(child)
            else:
                nodes[tp_name] = [child]
        new_body = []
        for type_name in sorted(nodes):
            if hasattr(nodes[type_name][0], "name"):
                nodes[type_name] = sorted(
                    nodes[type_name], key=lambda nd: nd.name)

            new_body += nodes[type_name]
        node.body = new_body
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node):
        return self.__normalize_node(node)

    def visit_FunctionDef(self, node):
        return self.__normalize_node(node)

    def visit_AsyncFunctionDef(self, node):
        return self.__normalize_node(node)

    def visit_Module(self, node):
        return self.__normalize_node(node)


class NameNormalizer(ast.NodeTransformer):
    """
    Changes name for vars and definitions
    to first character of previous one
    """

    def __def_name_change(self, node: Union[
        ast.ClassDef,
        ast.FunctionDef,
        ast.AsyncFunctionDef,
    ]):
        node.name = node.name[0]
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node):
        return self.__def_name_change(node)

    def visit_FunctionDef(self, node):
        return self.__def_name_change(node)

    def visit_AsyncFunctionDef(self, node):
        return self.__def_name_change(node)

    def visit_Name(self, node):
        new_name = node.id[0]
        node.id = new_name
        self.generic_visit(node)
        return node


def preprocess_code(code):
    """
    Normalizes code by conversion to ast, deletes docstrings,
    changes names, gives order for code blocks
    """

    try:
        tree = ast.parse(code)
        tree = DocstringDeleter().visit(tree)
        tree = NameNormalizer().visit(tree)
        tree = OrderNormalizer().visit(tree)
    except SyntaxError:
        print("SyntaxError while parsing, "
              "usage of not preprocessed code")
        return code
    return ast.unparse(tree)


def levenshtein_dist(s1, s2):
    """Counts levenshtein distance from 2 strings"""

    n, m = len(s1), len(s2)
    if n > m:
        s1, s2 = s2, s1
        n, m = m, n

    current_row = range(n + 1)
    for i in range(1, m + 1):
        previous_row, current_row = current_row, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
            if s1[j - 1] != s2[i - 1]:
                change += 1
            current_row[j] = min(add, delete, change)
    max_len = max(n, m)
    return current_row[n] / max_len


def compare_pair(file_name1, file_name2, output_file):
    """Prints levenshtein distance for preprocessed codes"""

    with open(file_name1, 'r') as f1, \
            open(file_name2, 'r') as f2, \
            open(output_file, 'a') as o:
        code1 = f1.read()
        code2 = f2.read()
        diff = levenshtein_dist(
            preprocess_code(code1),
            preprocess_code(code2),
        )
        print(diff, file=o)
        print("PROCESSED PAIR : ", file_name1, file_name2)


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

    for file_pair in compare_file_pairs:
        compare_pair(file_pair[0], file_pair[1], output_file)


if __name__ == "__main__":
    main()
