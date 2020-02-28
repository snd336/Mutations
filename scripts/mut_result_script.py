import yaml

"""
Some files in MutPy cause MutPy to become buggy.
I've used this script to work around this issue after running MutPy
on a file one operation at a time. This script allowed me to collect
several repo files together to make feature collection run as if
MutPy did not crash.
"""


# Currently only writes what I will need
class JoinRepo:
    def __init__(self):

        self.coverage = None
        self.mutation_score = None
        self.mutations = []
        self.last_mutation_number = 0
        self.number_of_tests = None
        self.targets = None
        self.tests = None
        self.total_time = 0
        self.time_stats = {'create_mutant_module': 0, 'create_target_ast': 0, 'mutate_module': 0,
                           'run_tests_with_mutant': 0}

        self.repo_dict = {'mutations': self.mutations, 'time_stats': self.time_stats, 'total_time': self.total_time}

    def combine_dicts(self, repo_dict):
        self.combine_mutations(repo_dict['mutations'])
        self.combine_time_stats(repo_dict['time_stats'])
        self.combine_total_time(repo_dict['total_time'])

    def combine_mutations(self, mutations):
        for mut in mutations:
            mut['number'] += self.last_mutation_number
        self.mutations += mutations
        if len(mutations) > 0:
            self.last_mutation_number = mutations[-1]['number']

    def combine_time_stats(self, time_stats):
        if 'create_mutant_module' in time_stats:
            self.time_stats['create_mutant_module'] += time_stats['create_mutant_module']
        self.time_stats['create_target_ast'] += time_stats['create_target_ast']
        self.time_stats['mutate_module'] += time_stats['mutate_module']
        if 'run_tests_with_mutant' in time_stats:
            self.time_stats['run_tests_with_mutant'] += time_stats['run_tests_with_mutant']

    def combine_total_time(self, total_time):
        self.repo_dict['total_time'] += total_time

    def write_yaml(self, path):
        with open(path, 'w') as report_file:
            yaml.dump(self.repo_dict, report_file, default_flow_style=False)


def get_results_from_mut(path, join_repo):
    with open(path, 'r') as file:
        data = file.readlines()
    i = 0
    for line in data:
        if line[0:26] == '  module: &id001 !!python/':
            data[i] = '  module: &id001\n'
            break
        i += 1

    with open(path, 'w') as file:
        file.writelines(data)

    with open(path) as yaml_file:
        repo_dict = yaml.load(yaml_file, Loader=yaml.FullLoader)
    join_repo.combine_dicts(repo_dict)


if __name__ == '__main__':

    ops = [
        'AOD',
        'AOR',
        'ASR',
        'BCR',
        'COD',
        'COI',
        'CRP',
        'DDL',
        'EHD',
        'EXS',
        'IHD',
        'IOD',
        'IOP',
        'LCR',
        'LOD',
        'LOR',
        'ROR',
        'SCD',
        'SCI',
        'SIR']

    path = 'C:\\Users\\steph\\Desktop\\Thesis\\Feature Scripts\\Working\\REPO\\ASTMONKEY\\visitor_split\\visitors_'
    joined = JoinRepo()

    for op in ops:
        get_results_from_mut(path + op, joined)

    path = 'C:\\Users\\steph\\Desktop\\Thesis\\Feature Scripts\\Working\\REPO\\ASTMONKEY\\REPO_visitors'
    joined.write_yaml(path)
