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


# TODO preprocess by removing blank lines for LOC counts?


def generate_ast_file(test):
    ast_test = []
    test_file_names = []

    for file in os.listdir('src/tests/' + test):
        if file.startswith('test') and file.endswith('.py'):
            test_file_names.append(file)
            with open('src/tests/' + test + '/' + file) as f:
                ast_test.append(ast.parse(f.read()))

    return ast_test, test_file_names


def create_mutant_list(file, folder):

    src_mod = importlib.import_module('src.' + folder + '.' + file[:-3])

    with open('src/' + folder + '/' + file) as f:
        ast_src = ast.parse(f.read())

    mutant_num = 1
    mutant = MutationList()
    sorted_ops = sorted(standard_operators, key=lambda cls: cls.name())
    for op in sorted_ops:
        mutant, mutant_num = op().generate_mutants(mod=src_mod, src_file=file, src_ast_module=ast_src,
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


def get_results_from_mut(sorted_mutations, repo_name):

    # avoids some import issues in the yaml file
    with open(repo_name, 'r') as file:
        data = file.readlines()
    i = 0
    for line in data:
        if line[0:26] == '  module: &id001 !!python/':
            data[i] = '  module: &id001\n'
            break
        i += 1

    with open(repo_name, 'w') as file:
        file.writelines(data)

    result_list = []

    with open(repo_name) as yaml_file:
        mutation_dict = yaml.load(yaml_file, Loader=yaml.FullLoader)
    global MutPy_time
    MutPy_time += mutation_dict['total_time']
    for i_dict in mutation_dict['mutations']:
        result_list.append(i_dict['status'])
        # result_list.append((i_dict['mutations'][0]['lineno'], i_dict['mutations'][0]['operator']))
    """
    if res != (mut[1].lineno, mut[1].mutant_operator_type):
            print('here', res, (mut[1].lineno, mut[1].mutant_operator_type))
    else:
        #print(res, (mut[1].lineno, mut[1].mutant_operator_type))
        pass

    """

    for mut, res in zip(sorted_mutations, result_list):
        mut[1].status = res


def mutant_dict_to_csv(mutation_ordered, csv_filename):

    with open(csv_filename, 'w', newline='') as f:
        writer = csv.writer(f)

        col_list = ['source_file', 'mutation_number', 'mutant_operator_type', 'lineno', 'ast_depth', 'num_test_cover',
                    'num_executed', 'num_assert_tm',
                    'num_assert_tc', 'function_max_depth', 'function_avg_depth',
                    'class_max_depth', 'lineno_loc', 'loc_list', 'status']
        writer.writerow(col_list)

        for item in mutation_ordered:
            m_o = item[1]
            mutation_number = item[0] # mutations objects on the same line have the same features
            writer.writerow(
                [m_o.source_file, mutation_number, m_o.mutant_operator_type, m_o.lineno, m_o.ast_depth,
                 m_o.num_test_cover, m_o.num_executed, m_o.num_assert_tm, m_o.num_assert_tc, m_o.function_max_depth,
                 m_o.function_avg_depth, m_o.class_max_depth, m_o.lineno_loc, m_o.loc_list, m_o.status])


def run_mut(src, test, out_file, mut_runner):
    src = 'src/' + src
    test = 'src/tests/' + test
    sys.argv = ['mut.py', '--target', src, '--unit-test', test,
                '--report', out_file, '--runner', mut_runner, '-q']
    commandline.main(sys.argv)

def run_mut2(src, test, out_file, mut_runner):
    src = 'src/mutpy/utils.py'
    test = 'src/tests/mutpytests/test_utils.py'
    sys.argv = ['mut.py', '--target', src, '--unit-test', test,
                '--report', 'REPO/MUTPY/REPO_utils',]# '--runner', mut_runner, '-q']
    commandline.main(sys.argv)



MutPy_time = 0

if __name__ == '__main__':
    # TODO Mutpy Bug: crashes on ASTMONKEY/visitors run all

    start_time = time.time()
    src_name = None
    test_name = None
    repo_file = {}
    csv_file = None
    runner = None

    mut_dict = {}

    name = 'mutpy'

    if name == 'bitstring':
        src_name = ['bitstring.py']
        test_name = 'bitstringtests'
        repo_file[src_name[0]] = 'REPO/REPO_BITSTRING'
        csv_file = 'Notebooks/CSV/bitstring_data.csv'
        runner = 'unittest'
    elif name == 'dictset':
        src_name = ['dictset.py']
        test_name = 'dictsettests'
        repo_file[src_name[0]] = 'REPO/REPO_DICTSET'
        csv_file = 'Notebooks/CSV/dictset_data.csv'
        runner = 'unittest'
    elif name == 'astmonkey':
        src_name = ['transformers.py', 'utils.py', 'visitors.py']
        test_name = 'astmonkeytests'
        repo_file = {}
        for s_n in src_name:
            repo_file[s_n] = 'REPO/ASTMONKEY/REPO_' + s_n[:-3]
        csv_file = 'Notebooks/CSV/astmonkey_data.csv'
        runner = 'pytest'
    elif name == 'mutpy':
        src_name = ['commandline.py', 'controller.py', 'coverage.py', 'utils.py', 'views.py']
        test_name = 'mutpytests'
        repo_file = {}
        for s_n in src_name:
            repo_file[s_n] = 'REPO/MUTPY/REPO_' + s_n[:-3]
        csv_file = 'Notebooks/CSV/mutpy_data.csv'
        runner = 'pytest'

    # run_mut(name, test_name, repo_file['utils.py'], runner)
    #run_mut2(name, test_name, repo_file['utils.py'], runner)

    test_ast, test_names = generate_ast_file(test_name)
    assertion_dict = {}
    for names, asts in zip(test_names, test_ast):
        assertion_dict.update(AssertCounter(names).get_assert_stats(asts))

    all_mutations = []
    for s in src_name:
        mut_dict[s] = create_mutant_list(s, name)

    # mutpy tests change the source ast
    # mutpy is also
    cov_dict = Cover(prg_name=name, src_name=src_name, test_name=test_names).run_trace()
    for s in src_name:
        add_dynamic_features(mut_dict[s], assertion_dict, cov_dict[s])
        mutations_sorted = mut_dict[s].sort_mutants()
        get_results_from_mut(mutations_sorted, repo_file[s])
        all_mutations += mutations_sorted

    mutant_dict_to_csv(all_mutations, csv_file)

    print("[*] Feature extraction [{0:.5f} s]".format((time.time() - start_time)))

    print(MutPy_time)
