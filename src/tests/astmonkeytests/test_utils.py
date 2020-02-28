import ast
import unittest

from src.astmonkey.utils import *
from src.astmonkey.transformers import *

class TestIsDocstring(unittest.TestCase):
    def test_non_docstring_node(self):
        node = ParentChildNodeTransformer().visit(ast.parse(''))

        assert not is_docstring(node)

    def test_module_docstring_node(self):
        node = ParentChildNodeTransformer().visit(ast.parse('"""doc"""'))

        assert is_docstring(node.body[0].value)

    def test_function_docstring_node(self):
        node = ParentChildNodeTransformer().visit(ast.parse('def foo():\n\t"""doc"""'))

        assert is_docstring(node.body[0].body[0].value)

    def test_class_docstring_node(self):
        node = ParentChildNodeTransformer().visit(ast.parse('class X:\n\t"""doc"""'))

        assert is_docstring(node.body[0].body[0].value)
