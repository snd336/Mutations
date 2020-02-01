import ast


class ClassCounter:

    def __init__(self, name=None, filename=None, begin_lineno=None):
        self.num_assert_tc = 0
        self.loc = None
        self.max_depth = None
        self.name = name
        self.filename = filename
        self.begin_lineno = begin_lineno
        self.end_lineno = None

    def update_loc(self, end_lineno):
        self.end_lineno = end_lineno
        self.loc = self.end_lineno - self.begin_lineno


class FunctionCounter:

    def __init__(self, name=None, class_counter=None, begin_lineno=None):
        self.num_assert_tm = 0
        self.loc = 0
        self.max_depth = 0
        self.name = name
        self.class_counter = class_counter
        self.begin_lineno = begin_lineno
        self.end_lineno = None

    def update_loc(self, end_lineno):
        self.end_lineno = end_lineno
        self.loc = self.end_lineno - self.begin_lineno - 1


class AssertCounter(ast.NodeVisitor):
    def __init__(self, filename=None):
        self.function_dict = {}  # key = name
        self.current_class = None
        self.current_function = None
        self.filename = filename
        self.last_lineno = None
        self.current_class_assert = 0
        self.ast_depth = 0
        self.class_max_depth = 0
        self.function_max_depth = 0

    def get_assert_stats(self, module):
        self.visit(module)
        return self.function_dict  # list of FunctionCounter objects

    def visit_ClassDef(self, node):
        self.current_class = ClassCounter(node.name, self.filename, self.last_lineno)
        self.generic_visit(node)
        self.current_class.update_loc(self.last_lineno)
        self.current_class.max_depth = self.class_max_depth
        self.class_max_depth = self.ast_depth

    def visit_FunctionDef(self, node):
        if node.name[0:5] == "test_":
            self.current_function = FunctionCounter(node.name, self.current_class, self.last_lineno)
            key_name = self.filename + '.' + self.current_class.name + '.' + self.current_function.name
            self.function_dict[key_name] = self.current_function
            self.generic_visit(node)
            self.current_function.update_loc(self.last_lineno)
            self.current_function.max_depth = self.function_max_depth
            self.function_max_depth = self.ast_depth

    def visit_Attribute(self, node):
        if node.attr[0:6] == "assert":
            self.current_function.num_assert_tm += 1
            self.current_class.num_assert_tc += 1

    def generic_visit(self, node):
        for child_node in ast.iter_child_nodes(node):
            if isinstance(child_node, list):
                self.generic_visit_list(child_node)
            elif isinstance(child_node, ast.AST):
                self.generic_visit_real_node(child_node)

    def generic_visit_list(self, ast_list):
        for position, value in enumerate(ast_list):
            if isinstance(value, ast.AST):
                self.visit(value)

    def generic_visit_real_node(self, node):
        self.ast_depth += 1
        if self.ast_depth > self.class_max_depth:
            self.class_max_depth = self.ast_depth
        if self.ast_depth > self.function_max_depth:
            self.function_max_depth = self.ast_depth
        if hasattr(node, 'lineno'):
            self.last_lineno = node.lineno
        self.visit(node)
        self.ast_depth -= 1


if __name__ == '__main__':
    with open('test_calculator' + '.py') as f:
        test_ast = ast.parse(f.read())
    counter = AssertCounter('test_calculator')
    list_temp = counter.get_assert_stats(test_ast)
    for i in list_temp:
        print(i.num_assert_tm, i.class_counter.num_assert_tc)
