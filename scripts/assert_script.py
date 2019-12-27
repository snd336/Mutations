import ast

"""

filename == test_calculator     i.e. no extension
Creates a dictionary from a filename in the tests directory in the form of
{filename.class.method : [TC, TM], ... }
"""


class AssertCounter(ast.NodeVisitor):
    def __init__(self, filename):
        self.assert_dict = {}
        self.current_method = ''
        self.current_class = ''
        self.current_class_assert = 0
        self.current_class_keys = []
        self.filename = filename
        with open('src\\tests\\' + filename + '.py') as f:
            module = ast.parse(f.read())
            self.filename = filename
            self.visit(module)


    def visit_ClassDef(self, node):
        self.current_class = node.name
        self.generic_visit(node)

        for key in self.current_class_keys:
            self.assert_dict[key][0] = self.current_class_assert

        self.current_class_assert = 0
        self.current_class_keys = []

    def visit_FunctionDef(self, node):
        if node.name[0:5] == "test_":
            self.assert_dict[self.filename + '.' + self.current_class + '.' + node.name] = [0, 0]
            self.current_class_keys.append(self.filename + '.' + self.current_class + '.' + node.name)
            self.current_method = node.name
            self.generic_visit(node)

    def visit_Attribute(self, node):
        if node.attr[0:6] == "assert":
            self.assert_dict[self.filename + '.' + self.current_class + '.' + self.current_method][1] += 1
            self.current_class_assert += 1


if __name__ == '__main__':
    counter = AssertCounter('test_calculator')
    print(counter.assert_dict)
