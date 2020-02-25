import ast
from mutations import AbstractArithmeticOperatorReplacement, MutationOperator, MutationResign


# ASR, BCR, CRP, SIR, SVD, SDL
class AssignmentOperatorReplacement(AbstractArithmeticOperatorReplacement):
    def should_mutate(self, node):
        return isinstance(node.parent, ast.AugAssign)

    @classmethod
    def name(cls):
        return 'ASR'


class BreakContinueReplacement(MutationOperator):
    def mutate_Break(self, node):
        return ast.Continue()

    def mutate_Continue(self, node):
        return ast.Break()


def is_docstring(node):
    def_node = node.parent.parent
    return (isinstance(def_node, (ast.FunctionDef, ast.ClassDef, ast.Module)) and def_node.body and
            isinstance(def_node.body[0], ast.Expr) and isinstance(def_node.body[0].value, ast.Str) and
            def_node.body[0].value == node)


class ConstantReplacement(MutationOperator):
    FIRST_CONST_STRING = 'mutpy'
    SECOND_CONST_STRING = 'python'

    def mutate_Num(self, node):
        return ast.Num(n=node.n + 1)

    def mutate_Str(self, node):
        if is_docstring(node):
            return

        if node.s != self.FIRST_CONST_STRING:
            return ast.Str(s=self.FIRST_CONST_STRING)
        else:
            return ast.Str(s=self.SECOND_CONST_STRING)

    def mutate_Str_empty(self, node):
        if not node.s or is_docstring(node):
            return

        return ast.Str(s='')

    @classmethod
    def name(cls):
        return 'CRP'


class SliceIndexRemove(MutationOperator):
    def mutate_Slice_remove_lower(self, node):
        if not node.lower:
            return

        return ast.Slice(lower=None, upper=node.upper, step=node.step)

    def mutate_Slice_remove_upper(self, node):
        if not node.upper:
            return

        return ast.Slice(lower=node.lower, upper=None, step=node.step)

    def mutate_Slice_remove_step(self, node):
        if not node.step:
            return

        return ast.Slice(lower=node.lower, upper=node.upper, step=None)


class SelfVariableDeletion(MutationOperator):
    def mutate_Attribute(self, node):
        try:
            if node.value.id == 'self':
                return ast.Name(id=node.attr, ctx=ast.Load())
            else:
                raise MutationResign()
        except AttributeError:
            raise MutationResign()


class StatementDeletion(MutationOperator):
    def mutate_Assign(self, node):
        return ast.Pass()

    def mutate_Return(self, node):
        return ast.Pass()

    def mutate_Expr(self, node):
        if utils.is_docstring(node.value):
            raise MutationResign()
        return ast.Pass()

    @classmethod
    def name(cls):
        return 'SDL'
