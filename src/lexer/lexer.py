"""
LOLCODE Lexer — Lexer class
CMSC 124 - S-3L | Group EJDB
Milestone 1 - Lexical Analyzer

Tokenizes a .lol source file into a list of classified tokens
based on the LOLCODE language specification.
"""

import re
import sys

from .tokens import (
    Token,
    TT_KEYWORD, TT_IDENTIFIER, TT_NUMBR, TT_NUMBAR, TT_YARN, TT_TROOF,
    TT_TYPE, TT_SEPARATOR, TT_COMMENT, TT_NEWLINE, TT_EOF, TT_UNKNOWN,
    KEYWORDS, TYPE_LITERALS, TROOF_LITERALS,
)


class Lexer:
    """Tokenizes LOLCODE source code into a list of Token objects."""

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

            # TLDR closes a multi-line comment
            if in_multiline_comment:
                if re.fullmatch(r'TLDR(\s+BTW.*)?', line) or line == 'TLDR':
                    self.tokens.append(Token(TT_COMMENT, 'TLDR', line_num))
                    in_multiline_comment = False
                else:
                    self.tokens.append(Token(TT_COMMENT, line, line_num))
                i += 1
                continue

            # Empty line
            if not line:
                self.tokens.append(Token(TT_NEWLINE, '\\n', line_num))
                i += 1
                continue

            # OBTW opens a multi-line comment
            if re.fullmatch(r'OBTW(\s+.*)?', line):
                self.tokens.append(Token(TT_COMMENT, line, line_num))
                in_multiline_comment = True
                i += 1
                continue

            # Join continued lines (ec06: trailing ...)
            line, continued = self._strip_continuation(line)
            while continued and i + 1 < len(lines):
                i += 1
                nxt, continued = self._strip_continuation(lines[i].strip())
                line = line + ' ' + nxt

            # Tokenize the line
            line_tokens = self._tokenize_line(line, line_num)
            self.tokens.extend(line_tokens)
            self.tokens.append(Token(TT_NEWLINE, '\\n', line_num))
            i += 1

        self.tokens.append(Token(TT_EOF, 'EOF', len(lines) + 1))
        return self.tokens

    def _strip_continuation(self, line):
        """Return (content, continued). A trailing '...' outside a YARN/comment continues the line."""
        i = 0
        in_str = False
        while i < len(line):
            c = line[i]
            if in_str:
                if c == ':' and i + 1 < len(line) and line[i + 1] in ')>o:"':
                    if line[i + 1] == '"' and (i + 2 >= len(line) or line[i + 2] in ' \t\r\n+,'):
                        i += 1
                    else:
                        i += 2
                    continue
                if c == '"':
                    in_str = False
                i += 1
                continue
            if c == '"':
                in_str = True
            elif (line.startswith('BTW', i)
                  and (i == 0 or line[i - 1] == ' ')
                  and (i + 3 == len(line) or line[i + 3] == ' ')):
                return line, False
            elif line.startswith('...', i) and line[i + 3:].strip() == '':
                return line[:i].rstrip(), True
            i += 1
        return line, False

    def _tokenize_line(self, line, line_num):
        tokens = []
        pos    = 0

        while pos < len(line):
            # Skip whitespace
            if line[pos] == ' ':
                pos += 1
                continue

            remaining = line[pos:]

            # Inline comment (BTW)
            if re.match(r'^BTW\b', remaining):
                tokens.append(Token(TT_COMMENT, remaining, line_num))
                break  # rest of line is comment

            # YARN literal — handles LOLCODE escapes AND bare colons
            if remaining.startswith('"'):
                j = 1
                closed = False
                while j < len(remaining):
                    if remaining[j] == ':' and j + 1 < len(remaining) and remaining[j + 1] in ')>:"':
                        if remaining[j + 1] == '"' and (j + 2 >= len(remaining) or remaining[j + 2] in ' \t\r\n+,'):
                            j += 1
                        else:
                            j += 2
                    elif remaining[j] == '"':
                        j += 1
                        closed = True
                        break
                    else:
                        j += 1

                if closed:
                    tokens.append(Token(TT_YARN, remaining[:j], line_num))
                    pos += j
                    continue
                else:
                    self.errors.append(f'Line {line_num}: Unterminated YARN literal')
                    tokens.append(Token(TT_UNKNOWN, remaining, line_num))
                    pos += len(remaining)
                    continue

            # NUMBAR literal (float)
            numbar_match = re.match(r'^-?[0-9]+\.[0-9]+', remaining)
            if numbar_match:
                tokens.append(Token(TT_NUMBAR, numbar_match.group(), line_num))
                pos += numbar_match.end()
                continue

            # NUMBR literal (integer)
            numbr_match = re.match(r'^-?[0-9]+(?![.\w])', remaining)
            if numbr_match:
                tokens.append(Token(TT_NUMBR, numbr_match.group(), line_num))
                pos += numbr_match.end()
                continue

            # Separator (+ between VISIBLE operands, ! suppresses newline)
            if remaining[0] in '+!':
                tokens.append(Token(TT_SEPARATOR, remaining[0], line_num))
                pos += 1
                continue

            # Soft line break (ec01): comma outside YARN/comment acts like a newline
            if remaining[0] == ',':
                tokens.append(Token(TT_NEWLINE, '\\n', line_num))
                pos += 1
                continue

            # Slot accessor 'Z (ec08)
            if remaining.startswith("'Z") and (len(remaining) == 2 or remaining[2] in ' ,'):
                tokens.append(Token(TT_KEYWORD, "'Z", line_num))
                pos += 2
                continue

            # Keywords (longest-first to avoid partial matches)
            matched_keyword = False
            for kw in KEYWORDS:
                pattern = r'^' + re.escape(kw) + r'(?=[\s,]|$)'
                if re.match(pattern, remaining):
                    tokens.append(Token(TT_KEYWORD, kw, line_num))
                    pos += len(kw)
                    matched_keyword = True
                    break

            if matched_keyword:
                continue

            # Identifiers (start with letter, then letters/digits/underscores)
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

            # Unknown token — report error
            self.errors.append(f'Line {line_num}: Unknown token: {repr(remaining[0])}')
            tokens.append(Token(TT_UNKNOWN, remaining[0], line_num))
            pos += 1

        return tokens


# ── Helpers ───────────────────────────────────────────────────────────────────

def print_tokens(tokens):
    """Print the token list in a formatted table."""
    print(f'\n{"─"*55}')
    print(f'  {"LINE":<6} {"TYPE":<14} {"VALUE"}')
    print(f'{"─"*55}')
    for tok in tokens:
        if tok.token_type in (TT_NEWLINE, TT_EOF):
            continue
        print(f'  {str(tok.line_num):<6} {tok.token_type:<14} {repr(tok.value)}')
    print(f'{"─"*55}\n')


# ── CLI entry point ───────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print('Usage: python3 -m lexer <file.lol>')
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
        count = len([t for t in tokens if t.token_type not in (TT_NEWLINE, TT_EOF)])
        print(f'Tokenization complete. {count} tokens found.\n')


if __name__ == '__main__':
    main()