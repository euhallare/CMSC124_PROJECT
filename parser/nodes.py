"""
LOLCODE Parser — Node class, ParseError, and parser constants
CMSC 124 - S-3L | Group EJDB
"""

from lexer.tokens import TT_NUMBR, TT_NUMBAR, TT_YARN, TT_TROOF


# ── Constants ─────────────────────────────────────────────────────────────────

BINARY_OPS = [
    'SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF',
    'BIGGR OF', 'SMALLR OF',
    'BOTH OF', 'EITHER OF', 'WON OF',
    'BOTH SAEM', 'DIFFRINT',
]

VARIADIC_OPS = ['SMOOSH', 'ALL OF', 'ANY OF']

EXPRESSION_STARTS = BINARY_OPS + VARIADIC_OPS + ['NOT', 'MAEK', 'I IZ']

LITERAL_TYPES = [TT_NUMBR, TT_NUMBAR, TT_YARN, TT_TROOF]

BLOCK_ENDERS = [
    'KTHXBYE', 'BUHBYE', 'OIC', 'NO WAI', 'MEBBE', 'YA RLY',
    'OMG', 'OMGWTF', 'IF U SAY SO', 'IM OUTTA YR',
]


# ── ParseError ────────────────────────────────────────────────────────────────

class ParseError(Exception):
    def __init__(self, message, line_num):
        super().__init__(message)
        self.message  = message
        self.line_num = line_num


# ── Node ──────────────────────────────────────────────────────────────────────

class Node:
    """A node in the parse tree."""

    def __init__(self, label, value=None):
        self.label    = label
        self.value    = value
        self.children = []

    def add(self, child):
        self.children.append(child)
        return child


# ── Printing ──────────────────────────────────────────────────────────────────

def print_tree(node, prefix='', is_last=True, is_root=True):
    """Pretty-print the parse tree."""
    text = node.label
    if node.value is not None:
        text = text + ': ' + str(node.value)

    if is_root:
        print(text)
        child_prefix = ''
    else:
        if is_last:
            print(prefix + '`-- ' + text)
            child_prefix = prefix + '    '
        else:
            print(prefix + '|-- ' + text)
            child_prefix = prefix + '|   '

    count = len(node.children)
    for i in range(count):
        last = (i == count - 1)
        print_tree(node.children[i], child_prefix, last, False)