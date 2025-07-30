"""
Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
SPDX-License-Identifier: Apache-2.0
"""

from typing import Any
import ast
import re
from IPython.core.getipython import get_ipython
from IPython.core.interactiveshell import ExecutionInfo

from .api import ApiHandler
from .registry import TelemetryRegister
from .utils import REGISTRIES


api_handler = ApiHandler()

registries = {registry: TelemetryRegister(registry) for registry in REGISTRIES.keys()}


def strip_magic(code: str) -> str:
    """
    Parse the provided code into an AST (Abstract Syntax Tree).

    Parameters
    ----------

    code : str
        The code to parse.
    Returns
    -------
    str
        The code without IPython magic commands.

    """

    IPYTHON_MAGIC_PATTERN = r"^\s*[%!?]{1,2}|^.*\?{1,2}$"

    code = "\n".join(
        line for line in code.splitlines() if not re.match(IPYTHON_MAGIC_PATTERN, line)
    )

    return code


def capture_registered_calls(info: ExecutionInfo) -> None:
    """
    Use the AST module to parse the code that we are executing & send an API call
    if we detect specific function or method calls.

    Fail silently if we can't parse the code.

    Parameters
    ----------
    info : IPython.core.interactiveshell.ExecutionInfo
        An object containing information about the code being executed.

    Returns
    -------
    None
    """
    code = info.raw_cell

    if code is None:
        return None

    code = strip_magic(code)

    try:
        tree = ast.parse(code)
    except (SyntaxError, IndentationError):
        return None

    user_namespace: dict[str, Any] = get_ipython().user_ns  # type: ignore

    try:
        visitor = CallListener(user_namespace, REGISTRIES, api_handler)
        visitor.visit(tree)
    except Exception:
        # Catch all exceptions to avoid breaking the execution
        # of the code being run.
        return None

    return None


class CallListener(ast.NodeVisitor):
    def __init__(
        self,
        user_namespace: dict[str, Any],
        registries: dict[str, set[str]],
        api_handler: ApiHandler,
    ):
        self.user_namespace = user_namespace
        self.registries = registries
        self._caught_calls: set[str] = set()  # Mostly for debugging
        self.api_handler = api_handler

    def _get_full_name(self, node: ast.AST) -> str | None:
        """Recursively get the full name of a function or method call."""
        if isinstance(node, ast.Attribute):
            return f"{self._get_full_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Name):
            return node.id
        return None

    def safe_eval(self, node: ast.AST) -> Any:
        """Try to evaluate a node, or return the unparsed node if that fails."""
        try:
            return ast.literal_eval(node)
        except (ValueError, SyntaxError):
            return ast.unparse(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if full_name := self._get_full_name(node):
            self._process_api_call(full_name, [], {})

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        full_name = self._get_full_name(node.func)
        func_name = None
        if full_name:
            parts = full_name.split(".")
            if len(parts) == 1:
                # Regular function call
                func_name = f"{full_name}"
            else:
                # Check if the first part is in the user namespace
                instance = self.user_namespace.get(parts[0])
                if instance is None:
                    self.generic_visit(node)
                    return None

                class_name = type(instance).__name__
                if class_name != "module":
                    func_name = f"{class_name}.{'.'.join(parts[1:])}"
                else:
                    func_name = f"{instance.__name__}.{'.'.join(parts[1:])}"

        args = [self.safe_eval(arg) for arg in node.args]
        kwargs = {
            kw.arg: self.safe_eval(kw.value)
            for kw in node.keywords
            if kw.arg is not None
        }

        if func_name:
            self._process_api_call(func_name, args, kwargs)

        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        """Handle subscript operations."""
        full_name = self._get_full_name(node.value)  # Get the object being indexed
        func_name = None
        if full_name:
            parts = full_name.split(".")
            instance = self.user_namespace.get(parts[0])
            if instance is None:
                return None

            class_name = type(instance).__name__
            func_name = f"{class_name}.{'.'.join(parts[1:])}__getitem__"

        if isinstance(node.slice, ast.Name):
            args = self.user_namespace.get(node.slice.id, None)
        else:
            args = ast.unparse(node.slice)

        if func_name:
            self._process_api_call(func_name, [args], {})

        self.generic_visit(node)

    def _process_api_call(
        self, func_name: str, args: list[Any], kwargs: dict[str, Any]
    ) -> None:
        """Process an API call for a matched function name."""
        for registry, registered_funcs in self.registries.items():
            if func_name in registered_funcs:
                self.api_handler.send_api_request(
                    registry,
                    func_name,
                    args,
                    kwargs,
                )
                self._caught_calls |= {func_name}
