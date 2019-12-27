import coverage
import trace
import os
import re
import sys

from mutations import standard_operators
from mutations import MutationList
from pd_work import given_mutation_dict
from scripts.assert_script import AssertCounter
from src.runners.unittest_runner import debug_suit

"""
Run's the unittest twice, can't find a way to merge trace and coverage
Ended up just running as a debug to avoid storing results, hope to minimize time and space
"""


# .cover
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
    # get assert features for every test file that was used
    counter_dict = {}
    test_ctx_class_list = []
    for x in cov_data.measured_contexts():  # x = module.class.test_case
        temp_list = x.split('.')
        test_ctx_class_list.append(temp_list[0])
    test_ctx_class_list = list(set(test_ctx_class_list))

    for x in test_ctx_class_list:
        counter_dict.update(AssertCounter(x).assert_dict)
    return counter_dict


# returns: list of all .py files in src excluding runners and tests
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


def update_num_executed(cov_src_file, cov_mutants):
    cover_dict = {}
    lineno = 1
    if os.path.exists('cover/src.' + cov_src_file[:-3] + '.cover'):
        with open('cover/src.' + cov_src_file[:-3] + '.cover') as f:
            for line in f:
                match_obj = re.match(' {4}(\\d+)', line)
                if match_obj:
                    cover_dict[lineno] = match_obj.group(1)
                lineno += 1

        # update num_executed
        for key in cover_dict:
            if key in cov_mutants.mutation_lineno_list:
                if isinstance(cov_mutants.mutations[key], list):
                    for k in cov_mutants.mutations[key]:
                        k.num_executed = cover_dict[key]
                else:
                    cov_mutants.mutations[key].num_executed = cover_dict[key]


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
                        ftr_dict[line_no] = match_obj.group(1)
                    line_no += 1
        src_ftr_dict[py_file] = ftr_dict
    merge_ctx_and_assert_dict(assert_dict, cov_results)


def merge_ctx_and_assert_dict(assert_dict, cov_data):
    print(cov_data.measured_contexts())  # test_files
    # print(cov_data.measured_files())  # src_files
    print(assert_dict)


if __name__ == '__main__':

    create_cover_files()
    covData = create_coverage_data()
    assert_counter_dict = create_assert_dict(covData)
    src_list = generate_source_files()

    create_feature_dict(src_list, assert_counter_dict, covData)  # TODO if this works redo update_num_executed()

    # all source code # src_mut_dict['calculator.py'] = mutationList
    src_mut_dict = create_mutant_dict(src_list)

    for src_file, mutants in src_mut_dict.items():
        update_num_executed(src_file, mutants)

        cwd_path = os.getcwd()
        test_ctx_path = cwd_path + '\src\\' + src_file
        if covData.contexts_by_lineno(test_ctx_path):
            ctx_dict = dict(covData.contexts_by_lineno(test_ctx_path))
            for ctx_key in ctx_dict.keys():
                unique_tc_list = []
                if ctx_key in mutants.mutation_lineno_list:
                    if isinstance(mutants.mutations[ctx_key], list):
                        for i in mutants.mutations[ctx_key]:
                            i.num_test_cover = len(ctx_dict[ctx_key])
                    else:
                        mutants.mutations[ctx_key].num_test_cover = len(ctx_dict[ctx_key])

                    for new_key in ctx_dict[ctx_key]:
                        tc_name = new_key.split('.')[2]
                        key_name = 'tests.' + new_key
                        if key_name in assert_counter_dict:
                            if tc_name not in unique_tc_list:
                                if isinstance(mutants.mutations[ctx_key], list):
                                    for i in mutants.mutations[ctx_key]:
                                        i.num_assert_tc += assert_counter_dict[key_name][0]
                                else:
                                    mutants.mutations[ctx_key].num_assert_tc += assert_counter_dict[key_name][0]
                                unique_tc_list.append(tc_name)
                            if isinstance(mutants.mutations[ctx_key], list):
                                for i in mutants.mutations[ctx_key]:
                                    i.num_assert_tm += assert_counter_dict[key_name][1]
                            else:
                                mutants.mutations[ctx_key].num_assert_tm += assert_counter_dict[key_name][1]

    for file in src_mut_dict:
        src_mut_dict[file].display_mutants()
    # given_mutation_dict(src_mut_dict) # to csv
