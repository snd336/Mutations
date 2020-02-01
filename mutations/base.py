import ast
import re
import os
import sys


class MutationResign(Exception):
    pass


class Mutation:
    def __init__(self, num_test_cover=0, num_executed=0, num_assert_tc=0, num_assert_tm=0, mutant_operator_type=None,
                 source_file=None, lineno=None, num_of_operations=0, mutation_number=None, status=None, ast_depth=None):
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
        self.ast_depth = ast_depth
        self.status = status
        self.function_max_depth = None
        self.function_avg_depth = None
        self.class_max_depth = None
        self.lineno_loc = None  # tests loc that touch mutation
        self.loc_list = None

    def update_ftr(self, ftr_list):
        self.num_executed = ftr_list[0]
        self.num_test_cover = ftr_list[1]
        self.num_assert_tm = ftr_list[2]
        self.num_assert_tc = ftr_list[3]
        self.function_max_depth = ftr_list[4]
        self.function_avg_depth = ftr_list[5]
        self.class_max_depth = ftr_list[6]
        self.lineno_loc = ftr_list[7]
        self.loc_list = ftr_list[8]


class MutationList:
    def __init__(self, mutation_lineno_list=None):
        self.mutation_lineno_list = mutation_lineno_list
        self.mutations = {}

    def update_lineno_list(self, lineno):
        if not self.mutation_lineno_list:  # if its empty
            self.mutation_lineno_list = []
            self.mutation_lineno_list.append(lineno)  # add lineno
        else:
            if lineno not in self.mutation_lineno_list:
                self.mutation_lineno_list.append(lineno)

    def sort_mutants(self):
        temp_list = []
        for lineno in self.mutations:
            for i in self.mutations[lineno]:  # each mutation per lineno
                num = i.mutation_number
                ops = i.num_of_operations
                temp_list = self.sort_helper(ops, temp_list, num, i)
        return sorted(temp_list, key=lambda mutant: mutant[0])  # sort by mutation_number

    @staticmethod
    def sort_helper(ops, temp_list, num, mutant_obj):
        debug_list = temp_list
        for i in range(ops):
            debug_list.append((num, mutant_obj))
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
        self.ast_depth = 0

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
                                                                           mutation_number=self.mutant_number,
                                                                           ast_depth=self.ast_depth)]
            else:
                self.mutation_list.mutations[self.last_lineno] = [Mutation(lineno=self.last_lineno,
                                                                           source_file=self.filename,
                                                                           num_of_operations=len(visitors),
                                                                           mutant_operator_type=self.name(),
                                                                           mutation_number=self.mutant_number,
                                                                           ast_depth=self.ast_depth)]
            self.mutant_number += len(visitors)
            self.mutation_list.update_lineno_list(self.last_lineno)

    def generate_mutants(self, src_file=None, src_ast_module=None, mutation_list=None, mutation_number=None):
        self.mutation_list = mutation_list
        self.filename = src_file
        self.mutant_number = mutation_number

        self.visit(src_ast_module)
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
        self.ast_depth += 1
        if hasattr(node, 'lineno'):
            self.last_lineno = node.lineno
        setattr(node, 'parent', self.last_parent_node[-1])
        self.visit(node)
        self.ast_depth -= 1

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
