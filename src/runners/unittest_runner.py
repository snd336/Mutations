import unittest
import os
from src.tests.test__dictset import suite as dictset_suit



def debug_suit(src_name):
    if src_name == 'dictset.py':
        suite_obj = dictset_suit()
        suite_obj.debug()
    elif src_name == 'bitstring.py':
        tests_path = 'C:\\Users\\steph\\Desktop\\Thesis\\Feature Scripts\\Working\\src\\tests\\bitstringtests'
        loader = unittest.TestLoader()
        suite_obj = unittest.TestSuite(loader.discover(tests_path))
        suite_obj.debug()


def run_suit():
    suite_obj = dictset_suit()
    result = unittest.TestResult()
    suite_obj.run(result)
    print(result.testsRun)


if __name__ == '__main__':
    debug_suit('bitstring.py')
