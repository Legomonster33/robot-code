import warnings
import enum as std_enum
from typing import Iterable
from library import arg, base, expr, stmt, utils

__all__ = [
    "Predicate",
    "UiPredicate",
    "UiTestPredicate",
]


class CallableType(std_enum.StrEnum):
    FUNCTION = "function"
    PREDICATE = "predicate"


class _Callable(stmt.BlockStatement):
    def __init__(
        self,
        name: str,
        *,
        callable_type: CallableType,
        arguments: Iterable[arg.Argument] = [],
        statements: Iterable[stmt.Statement | expr.Expr] = [],
        return_type: str | None = None,
        export: bool = True,
        is_lambda: bool = False,
        parent: base.ParentNode,
    ) -> None:
        super().__init__(parent=parent)
        self.add(*statements)

        self.name = name
        self.callable_type = callable_type
        self.arguments = arguments
        self.return_type = return_type
        self.export = export
        self.is_lambda = is_lambda

    def __call__(self, args: dict[str, str] = {}) -> expr.Expr:
        """Generates an expression which represents a call to the corresponding predicate or function.

        parameters: A list of tuples mapping argument names to the identifier to use.
        """
        arg_dict = dict(
            (argument.name, argument.default_parameter) for argument in self.arguments
        )
        for arg_name, parameter in args:
            if arg_name not in arg_dict:
                raise ValueError(
                    "{} did not match any arguments in predicate.".format(arg_name)
                )
            arg_dict[arg_name] = parameter

        return expr.Id("{}({})".format(self.name, ", ".join(arg_dict.values())))

    def arg_preamble(self) -> str:
        if self.is_lambda:
            return "const {} = function".format(self.name)
        return self.callable_type + " " + self.name

    def __str__(self) -> str:
        string = utils.export(self.export) + self.arg_preamble()
        string += "({})".format(utils.to_str(self.arguments))
        if self.return_type is not None:
            string += " returns " + self.return_type
        string += "\n{\n"
        string += self.children_str(tab=True, sep="\n")
        string += "}"
        if self.is_lambda:
            string += ";"
        string += "\n"
        return string


class Function(_Callable):
    def __init__(
        self,
        name: str,
        *,
        arguments: Iterable[arg.Argument] = [],
        return_type: str | None = None,
        statements: Iterable[stmt.Statement | expr.Expr] = [],
        export: bool = True,
        is_lambda: bool = False,
        parent: base.ParentNode,
    ) -> None:
        super().__init__(
            name,
            callable_type=CallableType.FUNCTION,
            arguments=arguments,
            return_type=return_type,
            statements=statements,
            export=export,
            is_lambda=is_lambda,
            parent=parent,
        )


class Predicate(_Callable):
    def __init__(
        self,
        name: str,
        *,
        parent: base.ParentNode,
        arguments: Iterable[arg.Argument] = [],
        statements: Iterable[stmt.Statement | expr.Expr] = [],
        export: bool = True,
    ) -> None:
        super().__init__(
            name,
            parent=parent,
            callable_type=CallableType.PREDICATE,
            arguments=arguments,
            statements=statements,
            export=export,
        )

        if self.arguments == []:
            warnings.warn("Predicate has 0 arguments.")

    def __str__(self) -> str:
        string = utils.export(self.export)
        string += "predicate {}({})\n{{\n".format(
            self.name, utils.to_str(self.arguments)
        )
        string += self.children_str(tab=True, sep="\n")
        string += "}\n"
        return string


class UiPredicate(Predicate):
    """
    A predicate defining elements for use in the UI.

    name: The name of the predicate. To match convention, the word `Predicate` is always automatically appended.
    """

    def __init__(
        self,
        name: str,
        *statements: stmt.Statement | expr.Expr,
        **kwargs,
    ) -> None:
        super().__init__(
            name + "Predicate",
            arguments=arg.definition_arg,
            statements=statements,
            **kwargs,
        )


class UiTestPredicate(Predicate):
    def __init__(
        self, name: str, *statements: stmt.Statement | expr.Expr, **kwargs
    ) -> None:
        super().__init__(
            name, arguments=arg.definition_arg, statements=statements, **kwargs
        )


# def test_predicate(
#     name: str,
#     *,
#     arguments: Iterable[arg.Argument] = [],
#     statements: Iterable[stmt.Statement | expr.Expr],
#     parent: base.ParentNode,
#     export: bool = True,
# ) -> expr.Expr:
#     """Adds a predicate to parent with the given statements.

#     Returns an expression which calls the predicate.
#     """
#     return Predicate(
#         name, parent=parent, arguments=arguments, statements=statements, export=export
#     )()
