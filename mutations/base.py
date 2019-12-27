import ast
import re


class Mutation:
    def __init__(self, num_test_cover=0, num_executed=0, num_assert_tc=0, num_assert_tm=0, mutant_operator_type=None,
                 source_file=None, lineno=None, col_offset=None, num_of_operations=0):
        self.num_of_operations = num_of_operations  # if you need to know how many operators applied to mutant
        self.source_file = source_file
        self.lineno = lineno
        self.col_offset = col_offset # TODO will this be useful
        # features
        self.mutant_operator_type = mutant_operator_type
        self.num_test_cover = num_test_cover
        self.num_executed = num_executed
        self.num_assert_tc = num_assert_tc
        self.num_assert_tm = num_assert_tm

    def update_ftr(self, ftr_list):
        self.num_test_cover = ftr_list[0]
        self.num_executed = ftr_list[1]
        self.num_assert_tc = ftr_list[2]
        self.num_assert_tm = ftr_list[3]


class MutationList:
    def __init__(self, mutation_lineno_list=None):
        self.mutation_lineno_list = mutation_lineno_list
        self.mutations = {}  # hold mutation objects

    def update_lineno_list(self, lineno):
        if not self.mutation_lineno_list:  # if its empty
            self.mutation_lineno_list = []
            self.mutation_lineno_list.append(lineno)  # add lineno
        else:
            if lineno not in self.mutation_lineno_list:
                self.mutation_lineno_list.append(lineno)

    # TODO replace with creating a csv file
    def display_mutants(self):
        for key in self.mutations:
            if isinstance(self.mutations[key], list):
                for i in self.mutations[key]:
                    file = i.source_file
                    line = i.lineno
                    op_type = i.mutant_operator_type
                    num_test = i.num_test_cover
                    num_exec = i.num_executed
                    tm = i.num_assert_tm
                    tc = i.num_assert_tc
                    self.display_helper(file, line, op_type, num_test, num_exec, tm, tc)
            else:
                file = self.mutations[key].source_file
                line = self.mutations[key].lineno
                op_type = self.mutations[key].mutant_operator_type
                num_test = self.mutations[key].num_test_cover
                num_exec = self.mutations[key].num_executed
                tm = self.mutations[key].num_assert_tm
                tc = self.mutations[key].num_assert_tc
                self.display_helper(file, line, op_type, num_test, num_exec, tm, tc)

    @staticmethod
    def display_helper(file, line, op_type, num_test, num_exec, tm, tc):
        print("Mutation at {}/{}".format(file, line))
        print("\tmutant_operator_type: {}".format(op_type))
        print("\tnum_test_cover: {}".format(num_test))
        print("\tnum_executed: {}".format(num_exec))
        print("\tnum_assert_tm: {}".format(tm))
        print("\tnum_assert_tc: {}\n".format(tc))


class MutationOperator(ast.NodeVisitor):
    def __init__(self):
        self.last_lineno = None
        self.mutation_list = None
        self.filename = None

    def update_mutation_list(self, visitors):
        if visitors:
            if self.last_lineno in self.mutation_list.mutations.keys():
                # TODO may have to flatten the list
                self.mutation_list.mutations[self.last_lineno] = self.mutation_list.mutations[self.last_lineno] + \
                                                                 [Mutation(lineno=self.last_lineno,
                                                                           source_file=self.filename,
                                                                           num_of_operations=len(visitors),
                                                                           mutant_operator_type=self.name())]
            else:
                self.mutation_list.mutations[self.last_lineno] = [Mutation(lineno=self.last_lineno,
                                                                           source_file=self.filename,
                                                                           num_of_operations=len(visitors),
                                                                           mutant_operator_type=self.name())]
            self.mutation_list.update_lineno_list(self.last_lineno)
            # TODO make sure adds more than AOR

    def generate_mutants(self, src_file=None, mutation_list=None):
        self.mutation_list = mutation_list
        self.filename = src_file
        with open(src_file) as f:
            module = ast.parse(f.read())
            self.visit(module)
            return self.mutation_list

    def generic_visit(self, node):
        visitors = self.find_visitors(node)
        self.update_mutation_list(visitors)
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
        if hasattr(node, 'lineno'):
            self.last_lineno = node.lineno
        self.visit(node)

    def find_visitors(self, node):
        method_prefix = 'mutate_' + node.__class__.__name__
        return self.getattrs_like(method_prefix)

    # noinspection SpellCheckingInspection
    def getattrs_like(self, attr_like):
        pattern = re.compile(attr_like + "($|(_\\w+)+$)")
        visitors = []
        for attr in dir(self):
            if pattern.match(attr):
                visitors.append(getattr(self, attr))
        return visitors

    # gives the abbreviations of the mutations, ie. AOR
    @classmethod
    def name(cls):
        return ''.join([c for c in cls.__name__ if str.isupper(c)])

    # gives the long name of the class in lower case
    @classmethod
    def long_name(cls):
        return ' '.join(map(str.lower, (re.split('([A-Z][a-z]*)', cls.__name__)[1::2])))


if __name__ == "__main__":
    filename = 'calculator.py'
    with open(filename) as t:
        print(t.read())
