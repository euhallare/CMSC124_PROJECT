"""
LOLCODE Interpreter — Runtime value types
CMSC 124 - S-3L | Group EJDB
"""

# ── Type constants ────────────────────────────────────────────────────────────

TYPE_NOOB   = 'NOOB'
TYPE_NUMBR  = 'NUMBR'
TYPE_NUMBAR = 'NUMBAR'
TYPE_YARN   = 'YARN'
TYPE_TROOF  = 'TROOF'

VALID_TYPES = {TYPE_NOOB, TYPE_NUMBR, TYPE_NUMBAR, TYPE_YARN, TYPE_TROOF}


# ── LolValue ──────────────────────────────────────────────────────────────────

class LolValue:
    """A LOLCODE runtime value: (python_value, lolcode_type)."""
    __slots__ = ('value', 'type')

    def __init__(self, value, lc_type):
        self.value = value
        self.type  = lc_type

    def __repr__(self):
        return f'LolValue({self.value!r}, {self.type})'


# Singleton for uninitialized variables
NOOB_VALUE = LolValue(None, TYPE_NOOB)