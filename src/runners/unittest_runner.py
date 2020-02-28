import unittest
import pytest
import sys
from src.tests.dictsettests.test__dictset import suite as dictset_suit


def debug_suit(prg_name):
    if prg_name == 'dictset':
        suite_obj = dictset_suit()
        suite_obj.debug()
    elif prg_name == 'bitstring':
        tests_path = 'C:\\Users\\steph\\Desktop\\Thesis\\Feature Scripts\\Working\\src\\tests\\bitstringtests'
        loader = unittest.TestLoader()
        suite_obj = unittest.TestSuite(loader.discover(tests_path))
        suite_obj.debug()
    elif prg_name == 'astmonkey':
        old_stdout = sys.stdout
        f = open('nul', 'w')
        sys.stdout = f
        pytest.main(['-x', 'C:\\Users\\steph\\Desktop\\Thesis\\Feature Scripts\\Working\\src\\tests\\astmonkeytests'])
        sys.stdout = old_stdout
    elif prg_name == 'mutpy':
        old_stdout = sys.stdout
        f = open('nul', 'w')
        sys.stdout = f
        pytest.main(['-x', 'C:\\Users\\steph\\Desktop\\Thesis\\Feature Scripts\\Working\\src\\tests\\mutpytests'])
        sys.stdout = old_stdout

if __name__ == '__main__':
    debug_suit('bitstring')
