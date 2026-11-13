"""
LOLCODE Lexer — Token types, constants, and Token class
CMSC 124 - S-3L | Group EJDB
"""

# ── Token Types ───────────────────────────────────────────────────────────────

TT_KEYWORD    = 'KEYWORD'
TT_IDENTIFIER = 'IDENTIFIER'
TT_NUMBR      = 'NUMBR'      # integer literal
TT_NUMBAR     = 'NUMBAR'     # float literal
TT_YARN       = 'YARN'       # string literal
TT_TROOF      = 'TROOF'      # boolean literal (WIN / FAIL)
TT_TYPE       = 'TYPE'       # type literal (NUMBR, NUMBAR, etc. used in typecast)
TT_SEPARATOR  = 'SEPARATOR'  # + used in VISIBLE
TT_COMMENT    = 'COMMENT'
TT_NEWLINE    = 'NEWLINE'
TT_EOF        = 'EOF'
TT_UNKNOWN    = 'UNKNOWN'


# ── Keywords ──────────────────────────────────────────────────────────────────
# Ordered longest-first to avoid partial matches (e.g. "I IZ" before "I HAS A")

KEYWORDS = [
    'BOTH SAEM', 'BOTH OF',
    'EITHER OF',
    'WON OF',
    'ALL OF',
    'ANY OF',
    'SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF',
    'BIGGR OF', 'SMALLR OF',
    'SMOOSH',
    'NOT',
    'DIFFRINT',
    'MAEK',
    'IS NOW A',
    'I HAS A',
    'I IZ',
    'IM IN YR', 'IM OUTTA YR',
    'HOW IZ I',
    'IF U SAY SO',
    'FOUND YR',
    'O RLY?',
    'YA RLY',
    'NO WAI',
    'WTF?',
    'OMG',
    'OMGWTF',
    'UPPIN', 'NERFIN',
    'WAZZUP', 'BUHBYE',
    'HAI', 'KTHXBYE',
    'VISIBLE', 'GIMMEH',
    'ITZ',
    'MEBBE',
    'OIC',
    'GTFO',
    'MKAY',
    'TLDR',
    'TIL', 'WILE',
    'YR',
    'AN',
    'R',
    'A',
]

# Type literals used in typecasting
TYPE_LITERALS = {'TROOF', 'NOOB', 'NUMBR', 'NUMBAR', 'YARN', 'TYPE'}

# Boolean literals
TROOF_LITERALS = {'WIN', 'FAIL'}


# ── Token class ───────────────────────────────────────────────────────────────

class Token:
    """Represents a single token with its type, value, and line number."""

    def __init__(self, token_type, value, line_num):
        self.token_type = token_type
        self.value      = value
        self.line_num   = line_num

    def __repr__(self):
        return f'Token({self.token_type}, {repr(self.value)}, line={self.line_num})'