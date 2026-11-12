"""
LOLCODE Interpreter — Control flow signals and runtime error
CMSC 124 - S-3L | Group EJDB
"""

from .values import LolValue


class RuntimeError_(Exception):
    """A LOLCODE runtime error."""
    def __init__(self, message, line_num=None):
        super().__init__(message)
        self.message  = message
        self.line_num = line_num


class GtfoSignal(Exception):
    """Raised by GTFO to break out of a loop or switch."""
    pass


class FoundYrSignal(Exception):
    """Raised by FOUND YR to return a value from a function."""
    def __init__(self, value: LolValue):
        self.value = value