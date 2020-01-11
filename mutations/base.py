import ast
import re
import os
import sys


class MutationResign(Exception):
    pass


class Mutation:
    def __init__(self, num_test_cover=0, num_executed=0, num_assert_tc=0, num_assert_tm=0, mutant_operator_type=None,
                 source_file=None, lineno=None, num_of_operations=0, mutation_number=None):
        self.num_of_operations = num_of_operations  # if you need to know how many operators applied to mutant
        self.source_file = source_file
        self.lineno = lineno
        self.mutation_number = mutation_number
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
        self.mutations = {}  # TODO ordered set?

    def update_lineno_list(self, lineno):
        if not self.mutation_lineno_list:  # if its empty
            self.mutation_lineno_list = []
            self.mutation_lineno_list.append(lineno)  # add lineno
        else:
            if lineno not in self.mutation_lineno_list:
                self.mutation_lineno_list.append(lineno)

    def display_mutants(self):
        temp_list = []
        for key in self.mutations:
            for i in self.mutations[key]:
                num = i.mutation_number
                line = i.lineno
                ops = i.num_of_operations
                op_type = i.mutant_operator_type
                temp_list = self.display_helper(line, op_type, ops, temp_list, num)
        temp_list = sorted(temp_list, key=lambda mutant: mutant[2])
        for i in temp_list:
            print("{} [{}] {}".format(i[0], i[1], i[2]))

    @staticmethod
    def display_helper(line, op_type, ops, temp_list, num):
        debug_list = temp_list
        for i in range(ops):
            debug_list.append((op_type, line, num))
            num += 1
        return debug_list


class MutationOperator(ast.NodeVisitor):
    def __init__(self):
        self.last_lineno = None
        self.last_parent_node = []
        self.mutation_list = None
        self.filename = None
        self.module = None
        self.mutant_number = None

    def update_mutation_list(self, visitors, node):
        temp_visitors = []
        if visitors:
            for visitor in visitors:
                if visitor(node):
                    temp_visitors.append(visitor)
        visitors = temp_visitors
        if visitors:
            if self.last_lineno in self.mutation_list.mutations.keys():
                self.mutation_list.mutations[self.last_lineno] = self.mutation_list.mutations[self.last_lineno] + \
                                                                 [Mutation(lineno=self.last_lineno,
                                                                           source_file=self.filename,
                                                                           num_of_operations=len(visitors),
                                                                           mutant_operator_type=self.name(),
                                                                           mutation_number=self.mutant_number)]
            else:
                self.mutation_list.mutations[self.last_lineno] = [Mutation(lineno=self.last_lineno,
                                                                           source_file=self.filename,
                                                                           num_of_operations=len(visitors),
                                                                           mutant_operator_type=self.name(),
                                                                           mutation_number=self.mutant_number)]
            self.mutant_number += len(visitors)
            self.mutation_list.update_lineno_list(self.last_lineno)

    def generate_mutants(self, src_file=None, mutation_list=None, mutation_number=None):
        self.mutation_list = mutation_list
        self.filename = src_file
        self.mutant_number = mutation_number

        directory, module_name = os.path.split(src_file)
        module_name = os.path.splitext(module_name)[0]

        path = list(sys.path)
        sys.path.insert(0, directory)
        try:
            self.module = __import__(module_name)
        finally:
            sys.path[:] = path  # restore

        with open(src_file) as f:
            module = ast.parse(f.read())
            self.visit(module)
            return self.mutation_list, self.mutant_number

    def generic_visit(self, node):
        if isinstance(node, ast.Module):
            setattr(node, 'parent', None)
        visitors = self.find_visitors(node)
        self.update_mutation_list(visitors, node)
        self.last_parent_node.append(node)

        for child_node in ast.iter_child_nodes(node):
            if isinstance(child_node, list):
                self.generic_visit_list(child_node)
            elif isinstance(child_node, ast.AST):
                self.generic_visit_real_node(child_node)
        self.last_parent_node.pop()

    def generic_visit_list(self, ast_list):
        for position, value in enumerate(ast_list):
            if isinstance(value, ast.AST):
                self.visit(value)

    def generic_visit_real_node(self, node):
        if hasattr(node, 'lineno'):
            self.last_lineno = node.lineno
        setattr(node, 'parent', self.last_parent_node[-1])
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

    @classmethod
    def name(cls):
        return ''.join([c for c in cls.__name__ if str.isupper(c)])

    @classmethod
    def long_name(cls):
        return ' '.join(map(str.lower, (re.split('([A-Z][a-z]*)', cls.__name__)[1::2])))


if __name__ == "__main__":
    filename = 'calculator.py'
    with open(filename) as t:
        print(t.read())
