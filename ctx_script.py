import csv
import coverage
import trace
import os
import re
import sys

from mutations import MutationList, standard_operators
from scripts.assert_script import AssertCounter
from src.runners.unittest_runner import debug_suit

"""
Run's the unittest twice, can't find a way to merge trace and coverage
Ended up just running as a debug to avoid storing results, hope to minimize time and space
"""


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


# TODO keep an eye out for line hits count on updated coverage
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


def create_assert_dict(cov_data):
    assert_dict = {}
    unique_filenames = []
    for x in cov_data.measured_contexts():  # x = module.class.test_case
        unique_filenames.append(x.split('.')[0])
    unique_filenames = set(unique_filenames)

    for x in unique_filenames:
        assert_dict.update(AssertCounter(x).assert_dict)
    return assert_dict


def generate_source_files():
    exclude = {'runners', 'tests', '__pycache__'}
    src_include_list = []
    for root, dirs, files in os.walk(top='src', topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude]
        for file_s in files:
            src_include_list.append(file_s)
    return src_include_list


def create_mutant_dict(src__file_list):
    mut_dict = {}
    for file_name in src__file_list:
        mutant = MutationList()
        for op in standard_operators:
            mutant = op().generate_mutants(src_file='src/' + file_name, mutation_list=mutant)
        mut_dict[file_name] = mutant
    return mut_dict


def create_feature_dict(py_files, assert_dict, cov_results):
    src_ftr_dict = {}
    for py_file in py_files:
        ftr_dict = {}
        # per src create ftr_dict
        line_no = 1
        if os.path.exists('cover/src.' + py_file[:-3] + '.cover'):
            with open('cover/src.' + py_file[:-3] + '.cover') as f:
                for line in f:
                    match_obj = re.match(' {4}(\\d+)', line)
                    if match_obj:
                        ftr_dict[line_no] = [int(match_obj.group(1))]
                    line_no += 1
        ctx_assert_dict = merge_ctx_and_assert_dict(py_file, cov_results, assert_dict)
        for x in ctx_assert_dict:
            ftr_dict[x] = ftr_dict[x] + ctx_assert_dict[x]

        src_ftr_dict[py_file] = ftr_dict
    return src_ftr_dict


def merge_ctx_and_assert_dict(ctx_file, ctx_results, assert_dict):
    # TODO what if a line is hit by more than one class
    ctx_hold_dict = dict(ctx_results.contexts_by_lineno(os.getcwd() + '\src\\' + ctx_file))
    ctx_assert_dict = {}

    for ctx_lineno, ctx_methods in ctx_hold_dict.items():
        ctx_assert_dict[ctx_lineno] = [len(ctx_methods), 0, 0]
        for ctx_method in ctx_methods:
            ctx_assert_dict[ctx_lineno][1] = assert_dict[ctx_method][0]
            ctx_assert_dict[ctx_lineno][2] += assert_dict[ctx_method][1]
    return ctx_assert_dict


def update_dyn_ftr(file_list, dyn_dict, mut_dict):
    for file_src in file_list:
        ftr_dict = dyn_dict[file_src]
        mutant_list = mut_dict[file_src]
        org_mut_dict = mutant_list.mutations
        for lineno in org_mut_dict:
            for x in org_mut_dict[lineno]:
                x.update_ftr(ftr_dict[lineno])


def mutant_dict_to_csv(mutation_dict):
    with open('data.csv', 'w', newline='') as f:
        writer = csv.writer(f)

        col_list = ['source_file', 'lineno', 'num_test_cover', 'num_executed', 'num_assert_tm', 'num_assert_tc',
                    'mutant_operator_type']
        writer.writerow(col_list)
        for key in mutation_dict:
            per_src_dict = mutation_dict[key].mutations
            for i in per_src_dict:
                for j in per_src_dict[i]:
                    m_o = j
                    writer.writerow(
                        [m_o.source_file, m_o.lineno, m_o.num_test_cover, m_o.num_executed, m_o.num_assert_tm,
                         m_o.num_assert_tc, m_o.mutant_operator_type])


if __name__ == '__main__':

    # create_cover_files()
    # covData = create_coverage_data()
    # assert_counter_dict = create_assert_dict(covData)
    src_list = generate_source_files()

    # dyn_ftr_dict = create_feature_dict(src_list, assert_counter_dict, covData)

    src_mut_dict = create_mutant_dict(src_list)

    # update_dyn_ftr(src_list, dyn_ftr_dict, src_mut_dict)
    for file in src_mut_dict:
        src_mut_dict[file].display_mutants()

    mutant_dict_to_csv(src_mut_dict)  # to csv
