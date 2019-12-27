from mutations import MutationList, standard_operators
import os


def mutate():

    exclude = {'runners', 'tests', '__pycache__'}
    for root, dirs, files in os.walk(top='src', topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude]
        for file in files:
            src_file = 'src/' + file
            mutants = MutationList()
            for op in standard_operators:
                mutants = op().generate_mutants(src_file=src_file, mutation_list=mutants)
                mutants.display_mutants()


if __name__ == '__main__':
    mutate()


