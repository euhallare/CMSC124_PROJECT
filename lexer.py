"""
LOLCODE Lexer / Tokenizer
CMSC 124 - S-3L | Group EJDB
Milestone 1 - Lexical Analyzer

Tokenizes a .lol source file into a list of classified tokens
based on the LOLCODE language specification.
"""

import re
import sys


# ─── TOKEN TYPES ──────────────────────────────────────────────────────────────

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


# ─── KEYWORDS ─────────────────────────────────────────────────────────────────
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


# ─── TOKEN CLASS ──────────────────────────────────────────────────────────────

class Token:
    def __init__(self, token_type, value, line_num):
        self.token_type = token_type
        self.value      = value
        self.line_num   = line_num

    def __repr__(self):
        return f'Token({self.token_type}, {repr(self.value)}, line={self.line_num})'


# ─── LEXER CLASS ──────────────────────────────────────────────────────────────

class Lexer:
    def __init__(self, source_code):
        self.source_code = source_code
        self.tokens      = []
        self.errors      = []

    def tokenize(self):
        lines = self.source_code.splitlines()
        in_multiline_comment = False
        i = 0

        while i < len(lines):
            raw_line = lines[i]
            line_num = i + 1
            line     = raw_line.strip()

            # ── TLDR closes a multi-line comment ──────────────────────────────
            if in_multiline_comment:
                if re.fullmatch(r'TLDR(\s+BTW.*)?', line) or line == 'TLDR':
                    self.tokens.append(Token(TT_COMMENT, 'TLDR', line_num))
                    in_multiline_comment = False
                else:
                    self.tokens.append(Token(TT_COMMENT, line, line_num))
                i += 1
                continue

            # ── Empty line ────────────────────────────────────────────────────
            if not line:
                self.tokens.append(Token(TT_NEWLINE, '\\n', line_num))
                i += 1
                continue

            # ── OBTW opens a multi-line comment ───────────────────────────────
            if re.fullmatch(r'OBTW(\s+.*)?', line):
                self.tokens.append(Token(TT_COMMENT, line, line_num))
                in_multiline_comment = True
                i += 1
                continue

            # ── Tokenize the line ─────────────────────────────────────────────
            line_tokens = self._tokenize_line(line, line_num)
            self.tokens.extend(line_tokens)
            self.tokens.append(Token(TT_NEWLINE, '\\n', line_num))
            i += 1

        self.tokens.append(Token(TT_EOF, 'EOF', len(lines) + 1))
        return self.tokens

    def _tokenize_line(self, line, line_num):
        tokens = []
        pos    = 0

        while pos < len(line):
            # Skip whitespace
            if line[pos] == ' ':
                pos += 1
                continue

            remaining = line[pos:]

            # ── Inline comment (BTW) ──────────────────────────────────────────
            if re.match(r'^BTW\b', remaining):
                tokens.append(Token(TT_COMMENT, remaining, line_num))
                break  # rest of line is comment

            # ── YARN literal (string in double quotes) ────────────────────────
            yarn_match = re.match(r'^"[^"]*"', remaining)
            if yarn_match:
                tokens.append(Token(TT_YARN, yarn_match.group(), line_num))
                pos += yarn_match.end()
                continue

            # ── NUMBAR literal (float) ────────────────────────────────────────
            numbar_match = re.match(r'^-?[0-9]+\.[0-9]+', remaining)
            if numbar_match:
                tokens.append(Token(TT_NUMBAR, numbar_match.group(), line_num))
                pos += numbar_match.end()
                continue

            # ── NUMBR literal (integer) ───────────────────────────────────────
            numbr_match = re.match(r'^-?[0-9]+(?![.\w])', remaining)
            if numbr_match:
                tokens.append(Token(TT_NUMBR, numbr_match.group(), line_num))
                pos += numbr_match.end()
                continue

            # ── Separator (+) ─────────────────────────────────────────────────
            if remaining[0] == '+':
                tokens.append(Token(TT_SEPARATOR, '+', line_num))
                pos += 1
                continue

            # ── Keywords (longest match first) ────────────────────────────────
            matched_keyword = False
            for kw in KEYWORDS:
                pattern = r'^' + re.escape(kw) + r'(?=\s|$)'
                if re.match(pattern, remaining):
                    tokens.append(Token(TT_KEYWORD, kw, line_num))
                    pos += len(kw)
                    matched_keyword = True
                    break

            if matched_keyword:
                continue

            # ── Identifiers / type literals / troof literals / keywords ───────
            ident_match = re.match(r'^[a-zA-Z][a-zA-Z0-9_]*', remaining)
            if ident_match:
                word = ident_match.group()
                if word in TROOF_LITERALS:
                    tokens.append(Token(TT_TROOF, word, line_num))
                elif word in TYPE_LITERALS:
                    tokens.append(Token(TT_TYPE, word, line_num))
                else:
                    tokens.append(Token(TT_IDENTIFIER, word, line_num))
                pos += ident_match.end()
                continue

            # ── Unknown character ─────────────────────────────────────────────
            self.errors.append(f'Line {line_num}: Unknown token: {repr(remaining[0])}')
            tokens.append(Token(TT_UNKNOWN, remaining[0], line_num))
            pos += 1

        return tokens


# ─── PRETTY PRINTER ───────────────────────────────────────────────────────────

def print_tokens(tokens):
    print(f'\n{"─"*55}')
    print(f'  {"LINE":<6} {"TYPE":<14} {"VALUE"}')
    print(f'{"─"*55}')
    for tok in tokens:
        if tok.token_type in (TT_NEWLINE, TT_EOF):
            continue
        print(f'  {str(tok.line_num):<6} {tok.token_type:<14} {repr(tok.value)}')
    print(f'{"─"*55}\n')


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print('Usage: python3 lexer.py <file.lol>')
        sys.exit(1)

    filepath = sys.argv[1]
    try:
        with open(filepath, 'r') as f:
            source = f.read()
    except FileNotFoundError:
        print(f'Error: File "{filepath}" not found.')
        sys.exit(1)

    lexer  = Lexer(source)
    tokens = lexer.tokenize()

    print(f'\nTokenizing: {filepath}')
    print_tokens(tokens)

    if lexer.errors:
        print('Lexer Errors:')
        for err in lexer.errors:
            print(f'  {err}')
    else:
        print(f'Tokenization complete. {len([t for t in tokens if t.token_type not in (TT_NEWLINE, TT_EOF)])} tokens found.\n')


if __name__ == '__main__':
    main()