import ast

from mutations.base import MutationOperator


class AbstractUnaryOperatorDeletion(MutationOperator):
    def mutate_UnaryOp(self, node):
        if isinstance(node.op, self.get_operator_type()):
            return node.operand
        

class ArithmeticOperatorDeletion(AbstractUnaryOperatorDeletion):
    def get_operator_type(self):
        return ast.UAdd, ast.USub


class AbstractArithmeticOperatorReplacement(MutationOperator):
    def should_mutate(self, node):
        raise NotImplementedError()

    def mutate_Add(self, node):
        if self.should_mutate(node):
            return ast.Sub()

    def mutate_Sub(self, node):
        if self.should_mutate(node):
            return ast.Add()

    def mutate_Mult_to_Div(self, node):
        if self.should_mutate(node):
            return ast.Div()

    def mutate_Mult_to_FloorDiv(self, node):
        if self.should_mutate(node):
            return ast.FloorDiv()

    def mutate_Mult_to_Pow(self, node):
        if self.should_mutate(node):
            return ast.Pow()

    def mutate_Div_to_Mult(self, node):
        if self.should_mutate(node):
            return ast.Mult()

    def mutate_Div_to_FloorDiv(self, node):
        if self.should_mutate(node):
            return ast.FloorDiv()

    def mutate_FloorDiv_to_Div(self, node):
        if self.should_mutate(node):
            return ast.Div()

    def mutate_FloorDiv_to_Mult(self, node):
        if self.should_mutate(node):
            return ast.Mult()

    def mutate_Mod(self, node):
        if self.should_mutate(node):
            return ast.Mult()

    def mutate_Pow(self, node):
        if self.should_mutate(node):
            return ast.Mult()


class ArithmeticOperatorReplacement(AbstractArithmeticOperatorReplacement):
    def should_mutate(self, node):
        return not isinstance(node.parent, ast.AugAssign)

    def mutate_USub(self, node):
        return ast.UAdd()

    def mutate_UAdd(self, node):
        return ast.USub()
