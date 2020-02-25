import sys
import time
import yaml


def get_results_from_mut(op):

    with open('REPO' + '_' + op, 'r') as file:
        data = file.readlines()
    i = 0
    for line in data:
        if line[0:26] == '  module: &id001 !!python/':
            data[i] = '  module: &id001\n'
            break
        i += 1

    with open('REPO' + '_' + op, 'w') as file:
        file.writelines(data)

    result_list = []

    with open('REPO' + '_' + op) as yaml_file:
        mutation_dict = yaml.load(yaml_file, Loader=yaml.FullLoader)

        for key in mutation_dict:
            if key == 'mutations':
                for i_dict in mutation_dict[key]:
                    result_list.append(i_dict['status'])

    return result_list


if __name__ == '__main__':

    start_time = time.time()

    ops = {
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
        'LCR',
        'LOD',
        'LOR',
        'ROR',
        'SCI',
        'SIR'}

    for op in ops:
        get_results_from_mut(op)

    print("--- %s seconds ---" % (time.time() - start_time))
