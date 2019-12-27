import pandas as pd
import csv


def given_mutation_dict(mutation_dict):
    with open('some.csv', 'w', newline='') as f:
        writer = csv.writer(f)

        col_list = ['source_file', 'lineno', 'num_test_cover', 'num_executed', 'num_assert_tm', 'num_assert_tc',
                    'mutant_operator_type']
        writer.writerow(col_list)
        for key in mutation_dict:
            per_src_dict = mutation_dict[key].mutations
            for i in per_src_dict:
                if isinstance(per_src_dict[i], list):
                    for j in per_src_dict[i]:
                        m_o = j
                        writer.writerow(
                            [m_o.source_file, m_o.lineno, m_o.num_test_cover, m_o.num_executed, m_o.num_assert_tm,
                             m_o.num_assert_tc, m_o.mutant_operator_type])
                else:
                    m_o = per_src_dict[i]
                    writer.writerow(
                        [m_o.source_file, m_o.lineno, m_o.num_test_cover, m_o.num_executed, m_o.num_assert_tm,
                         m_o.num_assert_tc, m_o.mutant_operator_type])


if __name__ == '__main__':
    pass
