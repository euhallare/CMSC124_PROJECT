"""
lexer package — re-exports everything so outside code can still do:
    from lexer import Lexer, TT_NEWLINE, TT_EOF, ...
"""

from .tokens import (
    Token,
    TT_KEYWORD, TT_IDENTIFIER, TT_NUMBR, TT_NUMBAR, TT_YARN, TT_TROOF,
    TT_TYPE, TT_SEPARATOR, TT_COMMENT, TT_NEWLINE, TT_EOF, TT_UNKNOWN,
    KEYWORDS, TYPE_LITERALS, TROOF_LITERALS,
)
from .lexer import Lexer, print_tokens

__all__ = [
    'Token',
    'TT_KEYWORD', 'TT_IDENTIFIER', 'TT_NUMBR', 'TT_NUMBAR', 'TT_YARN',
    'TT_TROOF', 'TT_TYPE', 'TT_SEPARATOR', 'TT_COMMENT', 'TT_NEWLINE',
    'TT_EOF', 'TT_UNKNOWN',
    'KEYWORDS', 'TYPE_LITERALS', 'TROOF_LITERALS',
    'Lexer', 'print_tokens',
]