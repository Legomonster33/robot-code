"""Defines transforms which may be performed directly on feature studio code.
"""
import re


def closing_brace(string: str, start: int) -> int:
    curr = string.index("{", start) + 1
    count = 1
    while count > 0:
        if string[curr] == "}":
            count -= 1
        elif string[curr] == "{":
            count += 1
        curr += 1
    return curr


def extract_function(code: str, function_name: str) -> str:
    """Extracts a standard function from a studio.

    Keywords such as export are ignored.
    The algorithm used is relatively simple and may fail if the code is not well-formed.
    For example, do not leave `{` with no corresponding `}` in the code.
    """
    function_start = code.index("function " + function_name)
    end = closing_brace(code, function_start)
    if code.find("precondition", function_start, code.index("{", function_start)) != -1:
        end = closing_brace(code, end)
    return code[function_start:end]


def to_lambda(function: str) -> str:
    """Converts a standard function to a lambda function."""
    result = re.match(r"function (\w+)\(", function)
    if not result:
        raise ValueError("Failed to extract function name from function.")
    name = result.groups()[-1]
    _, _, body = function.partition("(")

    # function myFunction() -> const myFunction = function()
    return "const " + name + " = function(" + body.rstrip("\n ") + ";"
