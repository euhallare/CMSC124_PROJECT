"""
LOLCODE Interpreter — Environment (variable store)
CMSC 124 - S-3L | Group EJDB
"""

from .values import LolValue, NOOB_VALUE
from .signals import RuntimeError_


class Environment:
    """Holds variables for one scope. Chains to a parent for outer scopes."""

    def __init__(self, parent=None):
        self.vars   = {}
        self.parent = parent
        self.vars['IT'] = NOOB_VALUE

    def get(self, name: str) -> LolValue:
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise RuntimeError_(f'Variable "{name}" is not defined')

    def set(self, name: str, val: LolValue):
        """Set in the nearest scope that already has the name, else local."""
        if name in self.vars:
            self.vars[name] = val
            return
        if self.parent and self.parent.has(name):
            self.parent.set(name, val)
            return
        self.vars[name] = val

    def set_local(self, name: str, val: LolValue):
        """Always set in this scope (used for function parameters)."""
        self.vars[name] = val

    def has(self, name: str) -> bool:
        if name in self.vars:
            return True
        if self.parent:
            return self.parent.has(name)
        return False

    def set_it(self, val: LolValue):
        self.vars['IT'] = val

    def get_it(self) -> LolValue:
        return self.vars.get('IT', NOOB_VALUE)

    def all_vars(self) -> dict:
        """Return a flat dict of all visible variables for the symbol table."""
        result = {}
        if self.parent:
            result.update(self.parent.all_vars())
        result.update(self.vars)
        return result