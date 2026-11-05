import sys

from lexer import (Lexer, TT_KEYWORD, TT_IDENTIFIER, TT_NUMBR, TT_NUMBAR,
                   TT_YARN, TT_TROOF, TT_TYPE, TT_SEPARATOR, TT_COMMENT,
                   TT_NEWLINE, TT_EOF)


BINARY_OPS = [
    'SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF',
    'BIGGR OF', 'SMALLR OF',
    'BOTH OF', 'EITHER OF', 'WON OF',
    'BOTH SAEM', 'DIFFRINT',
]

VARIADIC_OPS = ['SMOOSH', 'ALL OF', 'ANY OF']

EXPRESSION_STARTS = BINARY_OPS + VARIADIC_OPS + ['NOT', 'MAEK', 'I IZ']

LITERAL_TYPES = [TT_NUMBR, TT_NUMBAR, TT_YARN, TT_TROOF]

BLOCK_ENDERS = ['KTHXBYE', 'BUHBYE', 'OIC', 'NO WAI', 'MEBBE', 'YA RLY',
                'OMG', 'OMGWTF', 'IF U SAY SO', 'IM OUTTA YR']


class ParseError(Exception):
    def __init__(self, message, line_num):
        Exception.__init__(self, message)
        self.message = message
        self.line_num = line_num


class Node:
    def __init__(self, label, value=None):
        self.label = label
        self.value = value
        self.children = []

    def add(self, child):
        self.children.append(child)
        return child


class Parser:
    def __init__(self, tokens):
        self.tokens = []
        for tok in tokens:
            if tok.token_type != TT_COMMENT:
                self.tokens.append(tok)
        self.pos = 0
        self.errors = []
        self.in_function = False
        self.functions_ok = False

    # token helpers

    def peek(self, offset=0):
        index = self.pos + offset
        if index >= len(self.tokens):
            index = len(self.tokens) - 1
        return self.tokens[index]

    def advance(self):
        tok = self.peek()
        if tok.token_type != TT_EOF:
            self.pos += 1
        return tok

    def is_kw(self, value, offset=0):
        tok = self.peek(offset)
        return tok.token_type == TT_KEYWORD and tok.value == value

    def describe(self, tok):
        if tok.token_type == TT_NEWLINE:
            return 'end of line'
        if tok.token_type == TT_EOF:
            return 'end of file'
        return repr(tok.value)

    def expect_kw(self, value):
        if not self.is_kw(value):
            tok = self.peek()
            raise ParseError('expected ' + value + ', found ' + self.describe(tok), tok.line_num)
        return self.advance()

    def expect_type(self, token_type, what):
        tok = self.peek()
        if tok.token_type != token_type:
            raise ParseError('expected ' + what + ', found ' + self.describe(tok), tok.line_num)
        return self.advance()

    def skip_newlines(self):
        while self.peek().token_type == TT_NEWLINE:
            self.advance()

    def end_of_line(self):
        tok = self.peek()
        if tok.token_type == TT_NEWLINE:
            self.skip_newlines()
        elif tok.token_type != TT_EOF:
            raise ParseError('unexpected ' + self.describe(tok) + ', one line can only hold one statement', tok.line_num)

    # program

    def parse(self):
        try:
            return self.parse_program()
        except ParseError as e:
            self.errors.append('Syntax Error (line ' + str(e.line_num) + '): ' + e.message)
            return None

    def parse_program(self):
        root = Node('Program')
        self.skip_newlines()
        while self.is_kw('HOW IZ I'):
            root.add(self.parse_function())

        self.expect_kw('HAI')
        if self.peek().token_type == TT_NUMBAR:
            root.add(Node('Version', self.advance().value))
        self.end_of_line()

        if self.is_kw('WAZZUP'):
            root.add(self.parse_declarations())

        root.add(self.parse_block(['KTHXBYE'], True))
        self.expect_kw('KTHXBYE')
        self.end_of_line()

        while self.is_kw('HOW IZ I'):
            root.add(self.parse_function())

        tok = self.peek()
        if tok.token_type != TT_EOF:
            raise ParseError('only comments or functions can come after KTHXBYE, found ' + self.describe(tok), tok.line_num)
        return root

    def parse_declarations(self):
        node = Node('Declarations')
        self.expect_kw('WAZZUP')
        self.end_of_line()
        while not self.is_kw('BUHBYE'):
            tok = self.peek()
            if tok.token_type == TT_EOF:
                raise ParseError('expected BUHBYE, found end of file', tok.line_num)
            if not self.is_kw('I HAS A'):
                raise ParseError('only variable declarations (I HAS A) are allowed inside WAZZUP, found ' + self.describe(tok), tok.line_num)
            node.add(self.parse_declaration())
        self.expect_kw('BUHBYE')
        self.end_of_line()
        return node

    def parse_declaration(self):
        self.expect_kw('I HAS A')
        name = self.expect_type(TT_IDENTIFIER, 'a variable name')
        decl = Node('Declaration')
        decl.add(Node('Variable', name.value))
        if self.is_kw('ITZ'):
            self.advance()
            init = Node('Initializer')
            init.add(self.parse_expression(True))
            decl.add(init)
        self.end_of_line()
        return decl

    # blocks and statements

    def parse_block(self, terminators, allow_functions=False):
        block = Node('Block')
        old_flag = self.functions_ok
        self.functions_ok = allow_functions
        while True:
            self.skip_newlines()
            tok = self.peek()
            if tok.token_type == TT_EOF:
                raise ParseError('unexpected end of file, expected ' + ' or '.join(terminators), tok.line_num)
            if tok.token_type == TT_KEYWORD and tok.value in terminators:
                break
            if tok.token_type == TT_KEYWORD and tok.value in BLOCK_ENDERS:
                raise ParseError('unexpected ' + tok.value + ', expected ' + ' or '.join(terminators), tok.line_num)
            block.add(self.parse_statement())
        self.functions_ok = old_flag
        return block

    def parse_statement(self):
        tok = self.peek()

        if tok.token_type == TT_KEYWORD:
            kw = tok.value
            if kw == 'VISIBLE':
                return self.parse_print()
            if kw == 'GIMMEH':
                return self.parse_input()
            if kw == 'I HAS A':
                raise ParseError('variables must be declared inside the WAZZUP section', tok.line_num)
            if kw == 'O RLY?':
                return self.parse_if()
            if kw == 'WTF?':
                return self.parse_switch()
            if kw == 'IM IN YR':
                return self.parse_loop()
            if kw == 'GTFO':
                self.advance()
                self.end_of_line()
                return Node('Break')
            if kw == 'FOUND YR':
                return self.parse_return()
            if kw == 'HOW IZ I':
                if not self.functions_ok:
                    raise ParseError('functions can only be defined at the top level of the program', tok.line_num)
                return self.parse_function()
            if kw in EXPRESSION_STARTS:
                return self.parse_expression_statement()
            raise ParseError('unexpected ' + kw, tok.line_num)

        if tok.token_type == TT_IDENTIFIER:
            if self.is_kw('R', 1):
                return self.parse_assignment()
            if self.is_kw('IS NOW A', 1):
                return self.parse_recast()
            return self.parse_expression_statement()

        if tok.token_type in LITERAL_TYPES:
            return self.parse_expression_statement()

        raise ParseError('unexpected ' + self.describe(tok), tok.line_num)

    def parse_print(self):
        self.expect_kw('VISIBLE')
        node = Node('Print')
        node.add(self.parse_expression(True))
        while self.peek().token_type == TT_SEPARATOR and self.peek().value == '+':
            self.advance()
            node.add(self.parse_expression(True))
        if self.peek().token_type == TT_SEPARATOR and self.peek().value == '!':
            self.advance()
            node.add(Node('NoNewline'))
        self.end_of_line()
        return node

    def parse_input(self):
        self.expect_kw('GIMMEH')
        name = self.expect_type(TT_IDENTIFIER, 'a variable name')
        node = Node('Input')
        node.add(Node('Variable', name.value))
        self.end_of_line()
        return node

    def parse_assignment(self):
        name = self.expect_type(TT_IDENTIFIER, 'a variable name')
        self.expect_kw('R')
        node = Node('Assignment')
        node.add(Node('Variable', name.value))
        node.add(self.parse_expression(True))
        self.end_of_line()
        return node

    def parse_recast(self):
        name = self.expect_type(TT_IDENTIFIER, 'a variable name')
        self.expect_kw('IS NOW A')
        type_tok = self.expect_type(TT_TYPE, 'a type (NUMBR, NUMBAR, YARN, TROOF, NOOB)')
        node = Node('Recast')
        node.add(Node('Variable', name.value))
        node.add(Node('Type', type_tok.value))
        self.end_of_line()
        return node

    def parse_expression_statement(self):
        node = Node('ExpressionStatement')
        node.add(self.parse_expression(True))
        self.end_of_line()
        return node

    def parse_return(self):
        tok = self.expect_kw('FOUND YR')
        if not self.in_function:
            raise ParseError('FOUND YR can only be used inside a function', tok.line_num)
        node = Node('Return')
        node.add(self.parse_expression(True))
        self.end_of_line()
        return node

    # flow control

    def parse_if(self):
        node = Node('IfThen')
        self.expect_kw('O RLY?')
        self.end_of_line()

        self.expect_kw('YA RLY')
        self.end_of_line()
        yes_branch = Node('YaRly')
        yes_branch.add(self.parse_block(['NO WAI', 'MEBBE', 'OIC']))
        node.add(yes_branch)

        while self.is_kw('MEBBE'):
            self.advance()
            mebbe = Node('Mebbe')
            mebbe.add(self.parse_expression(True))
            self.end_of_line()
            mebbe.add(self.parse_block(['NO WAI', 'MEBBE', 'OIC']))
            node.add(mebbe)

        if self.is_kw('NO WAI'):
            self.advance()
            self.end_of_line()
            no_branch = Node('NoWai')
            no_branch.add(self.parse_block(['OIC']))
            node.add(no_branch)

        self.expect_kw('OIC')
        self.end_of_line()
        return node

    def parse_switch(self):
        node = Node('Switch')
        self.expect_kw('WTF?')
        self.end_of_line()

        while self.is_kw('OMG'):
            self.advance()
            tok = self.peek()
            if tok.token_type not in LITERAL_TYPES:
                raise ParseError('expected a literal after OMG, found ' + self.describe(tok), tok.line_num)
            self.advance()
            case = Node('Case')
            case.add(Node('Literal ' + tok.token_type, tok.value))
            self.end_of_line()
            case.add(self.parse_block(['OMG', 'OMGWTF', 'OIC']))
            node.add(case)

        if self.is_kw('OMGWTF'):
            self.advance()
            self.end_of_line()
            default = Node('Default')
            default.add(self.parse_block(['OIC']))
            node.add(default)

        self.expect_kw('OIC')
        self.end_of_line()
        return node

    def parse_loop(self):
        self.expect_kw('IM IN YR')
        label = self.expect_type(TT_IDENTIFIER, 'a loop label')
        node = Node('Loop', label.value)

        if self.is_kw('UPPIN') or self.is_kw('NERFIN'):
            op = self.advance()
            node.add(Node('Operation', op.value))
            self.expect_kw('YR')
            var = self.expect_type(TT_IDENTIFIER, 'a variable name')
            node.add(Node('Variable', var.value))

            if self.is_kw('TIL') or self.is_kw('WILE'):
                cond_tok = self.advance()
                cond = Node('Condition', cond_tok.value)
                cond.add(self.parse_expression(True))
                node.add(cond)

        self.end_of_line()
        node.add(self.parse_block(['IM OUTTA YR']))
        self.expect_kw('IM OUTTA YR')
        end_label = self.expect_type(TT_IDENTIFIER, 'a loop label')
        if end_label.value != label.value:
            raise ParseError('loop label ' + end_label.value + ' does not match ' + label.value, end_label.line_num)
        self.end_of_line()
        return node

    # functions

    def parse_function(self):
        tok = self.expect_kw('HOW IZ I')
        if self.in_function:
            raise ParseError('a function cannot be defined inside another function', tok.line_num)
        name = self.expect_type(TT_IDENTIFIER, 'a function name')
        node = Node('Function', name.value)

        params = Node('Parameters')
        if self.is_kw('YR'):
            self.advance()
            param = self.expect_type(TT_IDENTIFIER, 'a parameter name')
            params.add(Node('Parameter', param.value))
            while self.is_kw('AN'):
                self.advance()
                self.expect_kw('YR')
                param = self.expect_type(TT_IDENTIFIER, 'a parameter name')
                params.add(Node('Parameter', param.value))
        node.add(params)
        self.end_of_line()

        self.in_function = True
        node.add(self.parse_block(['IF U SAY SO']))
        self.in_function = False
        self.expect_kw('IF U SAY SO')
        self.end_of_line()
        return node

    def parse_call(self):
        self.expect_kw('I IZ')
        name = self.expect_type(TT_IDENTIFIER, 'a function name')
        node = Node('FunctionCall', name.value)
        if self.is_kw('YR'):
            self.advance()
            node.add(self.parse_expression(False))
            while self.is_kw('AN') and self.is_kw('YR', 1):
                self.advance()
                self.advance()
                node.add(self.parse_expression(False))
        self.expect_kw('MKAY')
        return node

    # expressions
    # top is True only where SMOOSH, ALL OF and ANY OF are allowed,
    # meaning they cannot be the operand of another operation

    def parse_expression(self, top):
        tok = self.peek()

        if tok.token_type in LITERAL_TYPES:
            self.advance()
            return Node('Literal ' + tok.token_type, tok.value)

        if tok.token_type == TT_IDENTIFIER:
            self.advance()
            return Node('Variable', tok.value)

        if tok.token_type == TT_KEYWORD:
            kw = tok.value

            if kw in BINARY_OPS:
                self.advance()
                node = Node('BinaryOp', kw)
                node.add(self.parse_expression(False))
                self.expect_kw('AN')
                node.add(self.parse_expression(False))
                return node

            if kw == 'NOT':
                self.advance()
                node = Node('UnaryOp', kw)
                node.add(self.parse_expression(False))
                return node

            if kw in VARIADIC_OPS:
                if not top:
                    raise ParseError(kw + ' cannot be nested inside another operation', tok.line_num)
                return self.parse_variadic()

            if kw == 'MAEK':
                self.advance()
                node = Node('Typecast')
                node.add(self.parse_expression(False))
                if self.is_kw('A'):
                    self.advance()
                type_tok = self.expect_type(TT_TYPE, 'a type (NUMBR, NUMBAR, YARN, TROOF, NOOB)')
                node.add(Node('Type', type_tok.value))
                return node

            if kw == 'I IZ':
                return self.parse_call()

        raise ParseError('expected an expression, found ' + self.describe(tok), tok.line_num)

    def parse_variadic(self):
        kw_tok = self.advance()
        node = Node('VariadicOp', kw_tok.value)
        node.add(self.parse_expression(False))
        while self.is_kw('AN'):
            self.advance()
            node.add(self.parse_expression(False))
        if kw_tok.value == 'SMOOSH':
            if self.is_kw('MKAY'):
                self.advance()
        else:
            self.expect_kw('MKAY')
        return node


# printing

def print_tree(node, prefix='', is_last=True, is_root=True):
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


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 syntax_analyzer.py <file.lol>')
        sys.exit(1)

    filepath = sys.argv[1]
    try:
        with open(filepath, 'r') as f:
            source = f.read()
    except FileNotFoundError:
        print('Error: File "' + filepath + '" not found.')
        sys.exit(1)

    lexer = Lexer(source)
    tokens = lexer.tokenize()
    if lexer.errors:
        print('Lexer Errors:')
        for err in lexer.errors:
            print('  ' + err)
        sys.exit(1)

    parser = Parser(tokens)
    tree = parser.parse()
    if parser.errors:
        for err in parser.errors:
            print(err)
        sys.exit(1)

    print('Syntax analysis complete. No syntax errors.\n')
    print_tree(tree)


if __name__ == '__main__':
    main()