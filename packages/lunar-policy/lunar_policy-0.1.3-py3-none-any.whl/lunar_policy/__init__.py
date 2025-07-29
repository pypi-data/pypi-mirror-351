from .data import Path, SnippetData
from .check import Check
from .result import Op, CheckStatus, AssertionResult
from .variables import variable, variable_or_default

__version__ = "0.1.3"

__all__ = [
    # Loading Data
    "Path",
    "SnippetData",

    # Making Assertions
    "Check",

    # Result Types
    "Op",
    "CheckStatus",
    "AssertionResult",

    # Snippet Variables
    "variable",
    "variable_or_default"
]
