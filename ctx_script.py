import ast
import csv
import importlib
import time

import coverage
import trace
import os
import re
import sys


from mutpy import commandline
import yaml


from mutations import MutationList, standard_operators
from scripts.assert_script import AssertCounter
from scripts.trace_script import Cover
from src.runners.unittest_runner import debug_suit


# TODO preprocess by removing blank lines for LOC counts?


def generate_ast_file(src, test):

    with open('src/' + src) as f:
        ast_src = ast.parse(f.read())

    with open('src/tests/' + test) as f:
        ast_test = ast.parse(f.read())

    return ast_src, ast_test


def create_mutant_list(file, file_ast):
    src_mod = importlib.import_module('src.' + file[:-3])

    mutant_num = 1
    mutant = MutationList()
    sorted_ops = sorted(standard_operators, key=lambda cls: cls.name())
    for op in sorted_ops:
        mutant, mutant_num = op().generate_mutants(mod=src_mod, src_file=file, src_ast_module=file_ast,
                                                   mutation_list=mutant, mutation_number=mutant_num)
    return mutant


def add_dynamic_features(mutation_dict, assert_dict, cover_dict):

    for lineno in mutation_dict.keys():

        num_executed = 0
        num_test_cover = 0
        num_assert_tm = 0
        num_assert_tc = 0
        class_max_depth = 0
        function_max_depth = 0
        function_avg_depth = 0
        lineno_loc = 0
        loc_list = []

        if lineno in cover_dict.keys():
            num_executed = cover_dict[lineno].count
            ctx_list = cover_dict[lineno].ctx
            num_test_cover = len(ctx_list)
            ctx_class_set = set([])

            for ctx in ctx_list:
                function_counter_object = assert_dict[ctx]
                num_assert_tm += function_counter_object.num_assert_tm
                if function_counter_object.max_depth > function_max_depth:
                    function_max_depth = function_counter_object.max_depth
                function_avg_depth += function_counter_object.max_depth
                lineno_loc += function_counter_object.loc
                loc_list.append(str(function_counter_object.begin_lineno) + ':'
                                + str(function_counter_object.end_lineno))
                ctx_class_set.add(function_counter_object.class_counter)

            if num_test_cover != 0:
                function_avg_depth /= num_test_cover

            for ctx_class in ctx_class_set:
                num_assert_tc += ctx_class.num_assert_tc
                if ctx_class.max_depth > class_max_depth:
                    class_max_depth = ctx_class.max_depth

        ftr_list = [num_executed, num_test_cover, num_assert_tm, num_assert_tc, function_max_depth, function_avg_depth,
                    class_max_depth, lineno_loc, loc_list]

        for mut_obj in mutation_dict[lineno]:
            mut_obj.update_ftr(ftr_list)


def run_mut(src, test):
    src = 'src/' + src
    test = 'src/tests/' + test
    sys.argv = ['mut.py', '--target', src, '--unit-test', test,
                '--report', 'REPO']  # , '-q']
    commandline.main(sys.argv)


def get_results_from_mut():
    # avoids some import issues in the yaml file

    with open('REPO', 'r') as file:
        data = file.readlines()
    i = 0
    for line in data:
        if line[0:26] == '  module: &id001 !!python/':
            data[i] = '  module: &id001\n'
            break
        i += 1

    with open('REPO', 'w') as file:
        file.writelines(data)

    result_list = []

    with open('REPO') as yaml_file:
        mutation_dict = yaml.load(yaml_file, Loader=yaml.FullLoader)

        for key in mutation_dict:
            if key == 'mutations':
                for i_dict in mutation_dict[key]:
                    result_list.append(i_dict['status'])

    return result_list


def mutant_dict_to_csv(mutation_list, status):
    with open('data.csv', 'w', newline='') as f:
        writer = csv.writer(f)

        col_list = ['source_file', 'lineno', 'ast_depth', 'num_test_cover', 'num_executed', 'num_assert_tm',
                    'num_assert_tc', 'mutant_operator_type', 'function_max_depth', 'function_avg_depth',
                    'class_max_depth', 'lineno_loc', 'loc_list', 'mutation_number', 'status']
        writer.writerow(col_list)

        per_src_dict = mutation_list.sort_mutants()

        for item in per_src_dict:  # via mutation_number
            m_o = item[1]
            writer.writerow(
                [m_o.source_file, m_o.lineno, m_o.ast_depth, m_o.num_test_cover, m_o.num_executed, m_o.num_assert_tm,
                 m_o.num_assert_tc, m_o.mutant_operator_type, m_o.function_max_depth, m_o.function_avg_depth,
                 m_o.class_max_depth, m_o.lineno_loc, m_o.loc_list, item[0], status[item[0]-1]])


if __name__ == '__main__':

    start_time = time.time()

    print("0--- %s seconds ---" % (time.time() - start_time))

    src_list = ['dictset.py']
    test_list = ['test__dictset.py']

    for src_name, test_name in zip(src_list, test_list):
        print("1--- %s seconds ---" % (time.time() - start_time))
        src_ast, test_ast = generate_ast_file(src_name, test_name)
        print("2--- %s seconds ---" % (time.time() - start_time))
        src_mut_list = create_mutant_list(src_name, src_ast)
        print("3--- %s seconds ---" % (time.time() - start_time))
        mut_dict_src = src_mut_list.mutations
        assertion_dict = AssertCounter(test_name).get_assert_stats(test_ast)
        print("4--- %s seconds ---" % (time.time() - start_time))
        cov_dict = Cover(src_name=src_name, test_name=test_name).run_trace()
        print("5--- %s seconds ---" % (time.time() - start_time))
        add_dynamic_features(mut_dict_src, assertion_dict, cov_dict)
        # run_mut(src_name, test_name)
        print("6--- %s seconds ---" % (time.time() - start_time))
        status_list = get_results_from_mut()
        print("7--- %s seconds ---" % (time.time() - start_time))
        mutant_dict_to_csv(src_mut_list, status_list)
        print("8--- %s seconds ---" % (time.time() - start_time))

    # TODO changes frequently
    print("--- %s seconds ---" % (time.time() - start_time))







