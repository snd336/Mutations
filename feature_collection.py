import ast
import csv
import importlib
import time
import os
import sys
from mutpy import commandline
import yaml

from mutations import MutationList, standard_operators
from scripts.assert_script import AssertCounter
from scripts.trace_script import Cover
from src.runners.unittest_runner import debug_suit


# TODO preprocess by removing blank lines for LOC counts?


def generate_ast_file(src, test):
    ast_test = []
    test_file_names = []

    with open('src/' + src) as f:
        ast_src = ast.parse(f.read())

    if test.endswith('.py'):
        with open('src/tests/' + test) as f:
            ast_test = ast.parse(f.read())
    else:
        for file in os.listdir('src/tests/' + test):
            if file.startswith('test') and file.endswith('.py'):
                test_file_names.append(file)
                with open('src/tests/' + test + '/' + file) as f:
                    ast_test.append(ast.parse(f.read()))

    return ast_src, ast_test, test_file_names


def create_mutant_list(file, file_ast):
    src_mod = importlib.import_module('src.' + file[:-3])

    mutant_num = 1
    mutant = MutationList()
    sorted_ops = sorted(standard_operators, key=lambda cls: cls.name())
    for op in sorted_ops:
        mutant, mutant_num = op().generate_mutants(mod=src_mod, src_file=file, src_ast_module=file_ast,
                                                   mutation_list=mutant, mutation_number=mutant_num)
    return mutant


def add_dynamic_features(mutation_list_obj, assert_dict, cover_dict):
    mutation_dict = mutation_list_obj.mutations
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
                if ctx in assert_dict.keys():
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


def get_results_from_mut(repo_file):
    # avoids some import issues in the yaml file

    with open(repo_file, 'r') as file:
        data = file.readlines()
    i = 0
    for line in data:
        if line[0:26] == '  module: &id001 !!python/':
            data[i] = '  module: &id001\n'
            break
        i += 1

    with open(repo_file, 'w') as file:
        file.writelines(data)

    result_list = []

    with open(repo_file) as yaml_file:
        mutation_dict = yaml.load(yaml_file, Loader=yaml.FullLoader)

        for key in mutation_dict:
            if key == 'mutations':
                for i_dict in mutation_dict[key]:
                    result_list.append(i_dict['status'])

    return result_list


def mutant_dict_to_csv(mutation_list, status, csv_filename):
    with open(csv_filename, 'w', newline='') as f:
        writer = csv.writer(f)

        col_list = ['source_file', 'mutation_number', 'mutant_operator_type', 'lineno', 'ast_depth', 'num_test_cover',
                    'num_executed', 'num_assert_tm',
                    'num_assert_tc', 'function_max_depth', 'function_avg_depth',
                    'class_max_depth', 'lineno_loc', 'loc_list', 'status']
        writer.writerow(col_list)

        per_src_dict = mutation_list.sort_mutants()

        for item in per_src_dict:  # via mutation_number
            m_o = item[1]
            writer.writerow(
                [m_o.source_file, item[0], m_o.mutant_operator_type, m_o.lineno, m_o.ast_depth, m_o.num_test_cover,
                 m_o.num_executed, m_o.num_assert_tm, m_o.num_assert_tc, m_o.function_max_depth, m_o.function_avg_depth,
                 m_o.class_max_depth, m_o.lineno_loc, m_o.loc_list, status[item[0]-1]])


def run_mut(src, test, out_file):
    src = 'src/' + src
    test = 'src/tests/' + test
    sys.argv = ['mut.py', '--target', src, '--unit-test', test,
                '--report', out_file, '-q']
    commandline.main(sys.argv)


if __name__ == '__main__':

    start_time = time.time()
    src_name = None
    test_name = None
    repo_file = None
    csv_file = None

    name = 'dictset'
    if name == 'bitstring':
        src_name = 'bitstring.py'
        test_name = 'bitstringtests'
        repo_file = 'REPO/REPO_BITSTRING'
        csv_file = 'Notebooks/CSV/bitstring_data.csv'
    elif name == 'dictset':
        src_name = 'dictset.py'
        test_name = 'test__dictset.py'
        repo_file = 'REPO/REPO_DICTSET'
        csv_file = 'Notebooks/CSV/dictset_data.csv'

    src_ast, test_ast, test_names = generate_ast_file(src_name, test_name)

    mut_list = create_mutant_list(src_name, src_ast)

    if type(test_ast) == list:
        assertion_dict = {}
        for n, a in zip(test_names, test_ast):
            assertion_dict.update(AssertCounter(n).get_assert_stats(a))

        cov_dict = Cover(src_name=src_name, test_name=test_names).run_trace()

    else:
        assertion_dict = AssertCounter(test_name).get_assert_stats(test_ast)

        cov_dict = Cover(src_name=src_name, test_name=test_name).run_trace()

    add_dynamic_features(mut_list, assertion_dict, cov_dict)
    print("[*] Feature extraction [{0:.5f} s]".format((time.time() - start_time)))

    run_mut(src_name, test_name, repo_file)
    status_list = get_results_from_mut(repo_file)

    mutant_dict_to_csv(mut_list, status_list, csv_file)


