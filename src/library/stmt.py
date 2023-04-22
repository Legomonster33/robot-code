from typing import Self
from src.library import base, expr, utils


class Statements(base.Node):
    def __init__(self, *statements: base.Node) -> None:
        self.statements = statements

    def __iter__(self):
        return self.statements.__iter__()

    def __str__(self) -> str:
        return utils.to_str(self.statements, sep="\n")


class Statement(base.Node):
    def __init__(self, expr: expr.Expr) -> None:
        self.expr = expr

    def __str__(self) -> str:
        return str(self.expr) + ";\n"

    def __iter__(self):
        return [self].__iter__()


class Else(Statement):
    def __init__(self) -> None:
        pass


class If(Statement):
    def __init__(self, test: expr.Expr, or_else: Self | Else | None = None) -> None:
        self.test = test
        self.statements = []

    def __add__(self, statement: Statement) -> Self:
        self.statements.append(statement)
        return self

    def __str__(self) -> str:
        string = "if ({})\n{{\n".format(self.test)
        string += utils.to_str(self.statements)
        return string + "}\n"
