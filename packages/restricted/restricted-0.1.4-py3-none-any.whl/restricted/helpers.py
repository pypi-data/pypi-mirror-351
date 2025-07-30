from restricted.core import Restrictor, Executor
from typing import Optional, List


def execute_restricted(
        code:str,
        modules: Optional[List[str]] = None,
        builtins: Optional[List[str]] = None,
        restrict: bool = True,
):
    """
    Parses and optionally validates the given Python code before executing it in a restricted environment.

    This helper function sets up a `Restrictor` with optional custom lists of restricted modules and
    built-in functions, then uses an `Executor` to validate and run the code. If `restrict` is set to
    False, the code will be executed without applying any restrictions.

    :param code: Python source code as a string.
    :param restricted_modules: Optional list of module names to block (defaults will be used if None).
    :param restricted_builtins: Optional list of built-in function names to block (defaults will be used if None).
    :param restrict: Flag to enable or disable code restriction checks. Defaults to True.
    :return: The result of executing the code using the executor's `execute_with_uv` method.
    """

    restrictor = Restrictor(modules=modules, builtins=builtins, action="restrict")
    executor = Executor(code, restrictor=restrictor, restrict=restrict)
    return executor.execute_with_uv()
