import ast
import csv
import coverage
import trace
import os
import re
import sys
from mutpy import commandline
import yaml


from mutations import MutationList, standard_operators
from scripts.assert_script import AssertCounter
from src.runners.unittest_runner import debug_suit

"""
Run's the unittest twice, can't find a way to merge trace and coverage
Ended up just running as a debug to avoid storing results, hope to minimize time and space
"""
# TODO preprocess by removing blank lines for LOC counts?
# TODO keep an eye out for line hits count on updated coverage.py


def create_cover_files():
    # create a trace object to get line hits for source files
    # creates .cover file
    tests_path = os.getcwd() + '\\src\\tests'
    # TODO can't figure out how to ignore the test runner file
    tracer = trace.Trace(count=1, trace=0, ignoredirs=[sys.prefix, sys.exec_prefix, tests_path])
    runner_file = open('src\\runners\\unittest_runner.py', 'r')
    code_str = runner_file.read()
    runner_file.close()
    code = compile(code_str, 'src\\runners\\unittest_runner.py', 'exec')
    tracer.run(code)

    r = tracer.results()
    r.write_results(coverdir='cover')


def create_coverage_data():
    # create a coverage object
    t_path = os.getcwd() + '\\src\\tests\\*'
    r_path = os.getcwd() + '\\src\\runners\\*'
    cov = coverage.Coverage(omit=[t_path, r_path])
    cov.erase()
    cov.start()
    debug_suit()
    # create coverage reports
    cov.stop()
    cov.save()
    #    cov.html_report(show_contexts=True)
    return cov.get_data()


def generate_ast_file(src_file_list, test_src_list):
    modules = []
    src_ast_list = []
    test_ast_list = []
    for src_file in src_file_list:
        modules.append(src_file + '\n')
        with open(src_file) as f:
            src_ast = ast.parse(f.read())
            modules.append(ast.dump(src_ast) + '\n')
            src_ast_list.append(src_ast)

    for test_file in test_src_list:
        modules.append(test_file)
        with open(test_file) as f:
            test_ast = ast.parse(f.read())
            modules.append(ast.dump(test_ast) + '\n')
            test_ast_list.append(test_ast)

    with open('ast_data', 'w') as file:
        file.writelines(modules)

    return src_ast_list, test_ast_list


def create_mutant_dict(src__file_list, src_ast_list):
    mut_dict = {}
    mutant_num = 1
    count = 0
    for file_name in src__file_list:
        mutant = MutationList()
        sorted_ops = sorted(standard_operators, key=lambda cls: cls.name())
        for op in sorted_ops:
            mutant, mutant_num = op().generate_mutants(src_file=file_name, src_ast_module=src_ast_list[count],
                                                       mutation_list=mutant, mutation_number=mutant_num)
        mut_dict[file_name] = mutant
        count += 1
    return mut_dict


def add_dynamic_features(src_file, mutation_list_obj, cov_data, test_ast, ast_filename):
    mutation_dict = mutation_list_obj.mutations
    assert_dict = AssertCounter(ast_filename).get_assert_stats(test_ast)

    with open('cover/src.' + src_file[4:-3] + '.cover', 'r') as file:
        data = file.readlines()

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

        match_obj = re.match(' {4}(\\d+)', data[lineno-1])
        if match_obj:
            num_executed = int(match_obj.group(1))

        coverage_dict = None
        for file in cov_data.measured_files():
            coverage_dict = cov_data.contexts_by_lineno(file)
        if coverage_dict:
            num_test_cover = len(coverage_dict[lineno])
            ctx_class_set = set([])

            for ctx in coverage_dict[lineno]:
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
    sys.argv = ['mut.py', '--target', src, '--unit-test', test,
                '--report', 'REPO', '-q']
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


def mutant_dict_to_csv(mutation_dict, status):
    with open('data.csv', 'w', newline='') as f:
        writer = csv.writer(f)

        col_list = ['source_file', 'lineno', 'ast_depth', 'num_test_cover', 'num_executed', 'num_assert_tm',
                    'num_assert_tc', 'mutant_operator_type', 'function_max_depth', 'function_avg_depth',
                    'class_max_depth', 'lineno_loc', 'loc_list', 'mutation_number', 'status']
        writer.writerow(col_list)

        for src_file in mutation_dict:
            per_src_dict = mutation_dict[src_file].sort_mutants()

            for item in per_src_dict:  # via mutation_number
                m_o = item[1]
                writer.writerow(
                    [m_o.source_file, m_o.lineno, m_o.ast_depth, m_o.num_test_cover, m_o.num_executed, m_o.num_assert_tm,
                     m_o.num_assert_tc, m_o.mutant_operator_type, m_o.function_max_depth, m_o.function_avg_depth,
                     m_o.class_max_depth, m_o.lineno_loc, m_o.loc_list, item[0], status[item[0]-1]])


if __name__ == '__main__':

    create_cover_files()
    covData = create_coverage_data()
    # Generate for each src?

    src_list = ['src/calculator.py']
    test_list = ['src/tests/test_calculator.py']
    t_name = ['test_calculator']

    src_files_ast, test_files_ast = generate_ast_file(src_list, test_list)
    src_mut_dict = create_mutant_dict(src_list, src_files_ast)

    count = 0
    for src_name in src_list:
        add_dynamic_features(src_name, src_mut_dict[src_name], covData, test_files_ast[count], t_name[count])
        count += 1



    run_mut(src_list[0], test_list[0])
    status_list = get_results_from_mut()
    mutant_dict_to_csv(src_mut_dict, status_list)





