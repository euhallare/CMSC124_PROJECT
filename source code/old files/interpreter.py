"""
LOLCODE Interpreter — Semantic Analyzer / Executor
CMSC 124 - S-3L | Group EJDB
Milestone 3 - Semantic Analysis

Walks the AST produced by the parser and executes it.
"""

from syntax_analyzer import Node


# ─────────────────────────────────────────────────────────────────────────────
# LOLCODE value types  (we store Python values + a LOLCODE type tag)
# ─────────────────────────────────────────────────────────────────────────────

TYPE_NOOB   = 'NOOB'
TYPE_NUMBR  = 'NUMBR'
TYPE_NUMBAR = 'NUMBAR'
TYPE_YARN   = 'YARN'
TYPE_TROOF  = 'TROOF'

VALID_TYPES = {TYPE_NOOB, TYPE_NUMBR, TYPE_NUMBAR, TYPE_YARN, TYPE_TROOF}


class LolValue:
    """A LOLCODE runtime value: (python_value, lolcode_type)."""
    __slots__ = ('value', 'type')

    def __init__(self, value, lc_type):
        self.value = value
        self.type  = lc_type

    def __repr__(self):
        return f'LolValue({self.value!r}, {self.type})'


NOOB_VALUE = LolValue(None, TYPE_NOOB)


# ─────────────────────────────────────────────────────────────────────────────
# Runtime exceptions (used for control flow)
# ─────────────────────────────────────────────────────────────────────────────

class RuntimeError_(Exception):
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


# ─────────────────────────────────────────────────────────────────────────────
# Typecasting
# ─────────────────────────────────────────────────────────────────────────────

def _is_numeric_yarn(s: str) -> bool:
    """True if the YARN can be cast to a number (digits, one optional leading
    hyphen, one optional period)."""
    s = s.strip()
    if not s:
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False


def typecast(val: LolValue, to_type: str, explicit: bool = False) -> LolValue:
    """
    Cast val to to_type.
    explicit=True  → MAEK / IS NOW A  (more permissive for NOOB)
    explicit=False → implicit cast inside an operation
    Raises RuntimeError_ on illegal cast.
    """
    if val.type == to_type:
        return val

    # ── NOOB ──────────────────────────────────────────────────────────────
    if val.type == TYPE_NOOB:
        if to_type == TYPE_TROOF:
            return LolValue(False, TYPE_TROOF)   # NOOB → TROOF is always FAIL
        if explicit:
            # explicit cast of NOOB → empty / zero values
            if to_type == TYPE_NUMBR:
                return LolValue(0, TYPE_NUMBR)
            if to_type == TYPE_NUMBAR:
                return LolValue(0.0, TYPE_NUMBAR)
            if to_type == TYPE_YARN:
                return LolValue('', TYPE_YARN)
            if to_type == TYPE_NOOB:
                return NOOB_VALUE
        raise RuntimeError_(f'Cannot implicitly cast NOOB to {to_type}')

    # ── TROOF ─────────────────────────────────────────────────────────────
    if val.type == TYPE_TROOF:
        win = val.value  # True / False
        if to_type == TYPE_NUMBR:
            return LolValue(1 if win else 0, TYPE_NUMBR)
        if to_type == TYPE_NUMBAR:
            return LolValue(1.0 if win else 0.0, TYPE_NUMBAR)
        if to_type == TYPE_YARN:
            return LolValue('WIN' if win else 'FAIL', TYPE_YARN)
        if to_type == TYPE_NOOB:
            return NOOB_VALUE

    # ── NUMBR ─────────────────────────────────────────────────────────────
    if val.type == TYPE_NUMBR:
        n = val.value
        if to_type == TYPE_NUMBAR:
            return LolValue(float(n), TYPE_NUMBAR)
        if to_type == TYPE_YARN:
            return LolValue(str(n), TYPE_YARN)
        if to_type == TYPE_TROOF:
            return LolValue(n != 0, TYPE_TROOF)
        if to_type == TYPE_NOOB:
            return NOOB_VALUE

    # ── NUMBAR ────────────────────────────────────────────────────────────
    if val.type == TYPE_NUMBAR:
        f = val.value
        if to_type == TYPE_NUMBR:
            return LolValue(int(f), TYPE_NUMBR)   # truncate
        if to_type == TYPE_YARN:
            # truncate to 2 decimal places
            return LolValue(f'{f:.2f}', TYPE_YARN)
        if to_type == TYPE_TROOF:
            return LolValue(f != 0.0, TYPE_TROOF)
        if to_type == TYPE_NOOB:
            return NOOB_VALUE

    # ── YARN ──────────────────────────────────────────────────────────────
    if val.type == TYPE_YARN:
        s = val.value
        if to_type == TYPE_NUMBR:
            if _is_numeric_yarn(s):
                return LolValue(int(float(s.strip())), TYPE_NUMBR)
            raise RuntimeError_(f'Cannot cast YARN "{s}" to NUMBR')
        if to_type == TYPE_NUMBAR:
            if _is_numeric_yarn(s):
                return LolValue(float(s.strip()), TYPE_NUMBAR)
            raise RuntimeError_(f'Cannot cast YARN "{s}" to NUMBAR')
        if to_type == TYPE_TROOF:
            return LolValue(s != '', TYPE_TROOF)
        if to_type == TYPE_NOOB:
            return NOOB_VALUE

    raise RuntimeError_(f'Cannot cast {val.type} to {to_type}')


def to_yarn(val: LolValue) -> str:
    """Convert any LolValue to its YARN string representation."""
    v = typecast(val, TYPE_YARN, explicit=True)
    return v.value


def to_troof(val: LolValue) -> bool:
    """Convert any LolValue to Python bool via TROOF cast."""
    v = typecast(val, TYPE_TROOF, explicit=False)
    return v.value


def coerce_arithmetic(a: LolValue, b: LolValue):
    """
    Coerce two values to numeric types for arithmetic.
    Returns (a', b', result_type).
    result_type is NUMBAR if either operand is NUMBAR, else NUMBR.
    """
    # implicit cast to numeric if needed
    if a.type not in (TYPE_NUMBR, TYPE_NUMBAR):
        a = typecast(a, TYPE_NUMBAR if '.' in str(a.value) else TYPE_NUMBR)
    if b.type not in (TYPE_NUMBR, TYPE_NUMBAR):
        b = typecast(b, TYPE_NUMBAR if '.' in str(b.value) else TYPE_NUMBR)

    if a.type == TYPE_NUMBAR or b.type == TYPE_NUMBAR:
        result_type = TYPE_NUMBAR
        a = typecast(a, TYPE_NUMBAR)
        b = typecast(b, TYPE_NUMBAR)
    else:
        result_type = TYPE_NUMBR

    return a, b, result_type


# ─────────────────────────────────────────────────────────────────────────────
# Environment  (variable store + function table)
# ─────────────────────────────────────────────────────────────────────────────

class Environment:
    def __init__(self, parent=None):
        self.vars    = {}           # name → LolValue
        self.parent  = parent
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
        """Always set in this scope (for function parameters)."""
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


# ─────────────────────────────────────────────────────────────────────────────
# Interpreter
# ─────────────────────────────────────────────────────────────────────────────

class Interpreter:
    """
    Walks the AST and executes it.

    output_fn  : callable(str)        — called for every VISIBLE output line
    input_fn   : callable(str) → str  — called for GIMMEH; arg is prompt text
    update_fn  : callable(dict)       — called after each statement to refresh
                                        the symbol table; dict is name→LolValue
    """

    def __init__(self, output_fn=None, input_fn=None, update_fn=None):
        self.output_fn  = output_fn  or print
        self.input_fn   = input_fn   or input
        self.update_fn  = update_fn  or (lambda d: None)
        self.functions  = {}         # name → Node('Function', ...)
        self.env        = None
        self.errors     = []

    # ── public entry point ────────────────────────────────────────────────

    def run(self, tree: Node):
        """Execute the program tree.  Returns the final environment."""
        self.env   = Environment()
        self.errors = []
        try:
            self._exec_program(tree)
        except RuntimeError_ as e:
            msg = f'Runtime Error'
            if e.line_num:
                msg += f' (line {e.line_num})'
            msg += f': {e.message}'
            self.errors.append(msg)
        except Exception as e:
            self.errors.append(f'Unexpected error: {e}')
        return self.env

    # ── program structure ─────────────────────────────────────────────────

    def _exec_program(self, node: Node):
        # collect function definitions first (anywhere in tree)
        for child in node.children:
            if child.label == 'Function':
                self.functions[child.value] = child

        for child in node.children:
            if child.label == 'Declarations':
                self._exec_declarations(child)
            elif child.label == 'Block':
                self._exec_block(child, self.env)
            # Version and Function nodes are skipped here

    def _exec_declarations(self, node: Node):
        for decl in node.children:
            self._exec_declaration(decl, self.env)

    def _exec_declaration(self, node: Node, env: Environment):
        name = node.children[0].value
        if len(node.children) > 1:
            init_node = node.children[1]           # Initializer node
            val = self._eval_expr(init_node.children[0], env)
        else:
            val = NOOB_VALUE
        env.set_local(name, val)
        self._notify_update(env)

    # ── block / statement dispatch ────────────────────────────────────────

    def _exec_block(self, node: Node, env: Environment):
        for stmt in node.children:
            self._exec_stmt(stmt, env)

    def _exec_stmt(self, node: Node, env: Environment):
        label = node.label

        if label == 'Print':
            self._exec_print(node, env)
        elif label == 'Input':
            self._exec_input(node, env)
        elif label == 'Assignment':
            self._exec_assignment(node, env)
        elif label == 'Recast':
            self._exec_recast(node, env)
        elif label == 'ExpressionStatement':
            val = self._eval_expr(node.children[0], env)
            env.set_it(val)
            self._notify_update(env)
        elif label == 'IfThen':
            self._exec_if(node, env)
        elif label == 'Switch':
            self._exec_switch(node, env)
        elif label == 'Loop':
            self._exec_loop(node, env)
        elif label == 'Break':
            raise GtfoSignal()
        elif label == 'Return':
            val = self._eval_expr(node.children[0], env)
            raise FoundYrSignal(val)
        elif label == 'Function':
            # function defined inline in block — register it
            self.functions[node.value] = node
        else:
            raise RuntimeError_(f'Unknown statement type: {label}')

    # ── print ─────────────────────────────────────────────────────────────

    def _exec_print(self, node: Node, env: Environment):
        parts      = []
        no_newline = False
        for child in node.children:
            if child.label == 'NoNewline':
                no_newline = True
            else:
                val = self._eval_expr(child, env)
                parts.append(to_yarn(val))
        text = ''.join(parts)
        if no_newline:
            self.output_fn(text, end='')
        else:
            self.output_fn(text)

    # ── input ─────────────────────────────────────────────────────────────

    def _exec_input(self, node: Node, env: Environment):
        var_name = node.children[0].value
        raw      = self.input_fn(f'Input for {var_name}: ')
        val      = LolValue(str(raw), TYPE_YARN)
        env.set(var_name, val)
        self._notify_update(env)

    # ── assignment ────────────────────────────────────────────────────────

    def _exec_assignment(self, node: Node, env: Environment):
        var_name = node.children[0].value
        val      = self._eval_expr(node.children[1], env)
        if not env.has(var_name):
            raise RuntimeError_(f'Variable "{var_name}" is not defined. Declare it in WAZZUP.')
        env.set(var_name, val)
        env.set_it(val)
        self._notify_update(env)

    # ── recast (IS NOW A) ─────────────────────────────────────────────────

    def _exec_recast(self, node: Node, env: Environment):
        var_name  = node.children[0].value
        to_type   = node.children[1].value
        cur_val   = env.get(var_name)
        new_val   = typecast(cur_val, to_type, explicit=True)
        env.set(var_name, new_val)
        self._notify_update(env)

    # ── if-then ───────────────────────────────────────────────────────────

    def _exec_if(self, node: Node, env: Environment):
        condition = to_troof(env.get_it())

        ya_rly  = None
        no_wai  = None
        mebbes  = []

        for child in node.children:
            if child.label == 'YaRly':
                ya_rly = child
            elif child.label == 'NoWai':
                no_wai = child
            elif child.label == 'Mebbe':
                mebbes.append(child)

        if condition:
            if ya_rly:
                self._exec_block(ya_rly.children[0], env)
        else:
            # check MEBBE branches
            executed = False
            for mebbe in mebbes:
                mebbe_cond = to_troof(self._eval_expr(mebbe.children[0], env))
                if mebbe_cond:
                    self._exec_block(mebbe.children[1], env)
                    executed = True
                    break
            if not executed and no_wai:
                self._exec_block(no_wai.children[0], env)

    # ── switch ────────────────────────────────────────────────────────────

    def _exec_switch(self, node: Node, env: Environment):
        it_val = env.get_it()

        matched = False
        try:
            for child in node.children:
                if child.label == 'Case':
                    if not matched:
                        lit_node = child.children[0]
                        case_val = self._eval_literal(lit_node)
                        if self._values_equal(it_val, case_val):
                            matched = True
                    if matched:
                        self._exec_block(child.children[1], env)
                elif child.label == 'Default':
                    if not matched:
                        matched = True
                    if matched:
                        self._exec_block(child.children[0], env)
        except GtfoSignal:
            pass

    def _values_equal(self, a: LolValue, b: LolValue) -> bool:
        """Equality check for switch-case (no auto typecast per spec)."""
        if a.type != b.type:
            return False
        return a.value == b.value

    # ── loop ──────────────────────────────────────────────────────────────

    def _exec_loop(self, node: Node, env: Environment):
        # parse loop header
        op_node   = None
        var_node  = None
        cond_node = None

        for child in node.children:
            if child.label == 'Operation':
                op_node = child
            elif child.label == 'Variable':
                var_node = child
            elif child.label == 'Condition':
                cond_node = child
            elif child.label == 'Block':
                body = child

        try:
            while True:
                # check condition before executing body
                if cond_node:
                    cond_val = self._eval_expr(cond_node.children[0], env)
                    cond_bool = to_troof(cond_val)
                    if cond_node.value == 'TIL' and cond_bool:
                        break
                    if cond_node.value == 'WILE' and not cond_bool:
                        break

                self._exec_block(body, env)

                # update loop variable
                if op_node and var_node:
                    cur = env.get(var_node.value)
                    cur_num = typecast(cur, TYPE_NUMBR)
                    if op_node.value == 'UPPIN':
                        new_val = LolValue(cur_num.value + 1, TYPE_NUMBR)
                    else:  # NERFIN
                        new_val = LolValue(cur_num.value - 1, TYPE_NUMBR)
                    env.set(var_node.value, new_val)
                    self._notify_update(env)

        except GtfoSignal:
            pass

    # ── expression evaluator ──────────────────────────────────────────────

    def _eval_expr(self, node: Node, env: Environment) -> LolValue:
        label = node.label

        # literals
        if label.startswith('Literal '):
            return self._eval_literal(node)

        if label == 'Variable':
            return env.get(node.value)

        if label == 'BinaryOp':
            return self._eval_binary(node, env)

        if label == 'UnaryOp':
            return self._eval_unary(node, env)

        if label == 'VariadicOp':
            return self._eval_variadic(node, env)

        if label == 'Typecast':
            return self._eval_typecast(node, env)

        if label == 'FunctionCall':
            return self._eval_call(node, env)

        raise RuntimeError_(f'Unknown expression node: {label}')

    # ── literal ───────────────────────────────────────────────────────────

    def _eval_literal(self, node: Node) -> LolValue:
        label = node.label
        raw   = node.value

        if 'NUMBR' in label and 'NUMBAR' not in label:
            return LolValue(int(raw), TYPE_NUMBR)
        if 'NUMBAR' in label:
            return LolValue(float(raw), TYPE_NUMBAR)
        if 'YARN' in label:
            # strip surrounding quotes
            return LolValue(raw[1:-1], TYPE_YARN)
        if 'TROOF' in label:
            return LolValue(raw == 'WIN', TYPE_TROOF)
        raise RuntimeError_(f'Unknown literal type in node: {label}')

    # ── binary op ─────────────────────────────────────────────────────────

    def _eval_binary(self, node: Node, env: Environment) -> LolValue:
        op   = node.value
        left  = self._eval_expr(node.children[0], env)
        right = self._eval_expr(node.children[1], env)

        # arithmetic
        if op in ('SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF',
                  'BIGGR OF', 'SMALLR OF'):
            return self._eval_arithmetic(op, left, right)

        # boolean
        if op == 'BOTH OF':
            return LolValue(to_troof(left) and to_troof(right), TYPE_TROOF)
        if op == 'EITHER OF':
            return LolValue(to_troof(left) or to_troof(right), TYPE_TROOF)
        if op == 'WON OF':
            return LolValue(to_troof(left) != to_troof(right), TYPE_TROOF)

        # comparison
        if op == 'BOTH SAEM':
            return LolValue(self._compare_equal(left, right), TYPE_TROOF)
        if op == 'DIFFRINT':
            return LolValue(not self._compare_equal(left, right), TYPE_TROOF)

        raise RuntimeError_(f'Unknown binary op: {op}')

    def _eval_arithmetic(self, op: str, a: LolValue, b: LolValue) -> LolValue:
        a, b, rtype = coerce_arithmetic(a, b)
        av, bv = a.value, b.value

        if op == 'SUM OF':
            return LolValue(av + bv, rtype)
        if op == 'DIFF OF':
            return LolValue(av - bv, rtype)
        if op == 'PRODUKT OF':
            return LolValue(av * bv, rtype)
        if op == 'QUOSHUNT OF':
            if bv == 0:
                raise RuntimeError_('Division by zero')
            if rtype == TYPE_NUMBR:
                return LolValue(int(av / bv), TYPE_NUMBR)
            return LolValue(av / bv, TYPE_NUMBAR)
        if op == 'MOD OF':
            if bv == 0:
                raise RuntimeError_('Modulo by zero')
            return LolValue(av % bv, rtype)
        if op == 'BIGGR OF':
            return LolValue(max(av, bv), rtype)
        if op == 'SMALLR OF':
            return LolValue(min(av, bv), rtype)
        raise RuntimeError_(f'Unknown arithmetic op: {op}')

    def _compare_equal(self, a: LolValue, b: LolValue) -> bool:
        """
        Equality per spec: integer math for NUMBRs, float for NUMBARs.
        No automatic typecasting for comparison operands.
        """
        if a.type == TYPE_NUMBR and b.type == TYPE_NUMBR:
            return a.value == b.value
        if a.type == TYPE_NUMBAR and b.type == TYPE_NUMBAR:
            return a.value == b.value
        if a.type == TYPE_YARN and b.type == TYPE_YARN:
            return a.value == b.value
        if a.type == TYPE_TROOF and b.type == TYPE_TROOF:
            return a.value == b.value
        # mixed numeric — allow NUMBR vs NUMBAR
        if a.type in (TYPE_NUMBR, TYPE_NUMBAR) and b.type in (TYPE_NUMBR, TYPE_NUMBAR):
            return float(a.value) == float(b.value)
        return False

    # ── unary op ──────────────────────────────────────────────────────────

    def _eval_unary(self, node: Node, env: Environment) -> LolValue:
        op  = node.value
        val = self._eval_expr(node.children[0], env)
        if op == 'NOT':
            return LolValue(not to_troof(val), TYPE_TROOF)
        raise RuntimeError_(f'Unknown unary op: {op}')

    # ── variadic op ───────────────────────────────────────────────────────

    def _eval_variadic(self, node: Node, env: Environment) -> LolValue:
        op = node.value

        if op == 'SMOOSH':
            parts = [to_yarn(self._eval_expr(c, env)) for c in node.children]
            return LolValue(''.join(parts), TYPE_YARN)

        vals = [to_troof(self._eval_expr(c, env)) for c in node.children]

        if op == 'ALL OF':
            return LolValue(all(vals), TYPE_TROOF)
        if op == 'ANY OF':
            return LolValue(any(vals), TYPE_TROOF)

        raise RuntimeError_(f'Unknown variadic op: {op}')

    # ── typecast (MAEK) ───────────────────────────────────────────────────

    def _eval_typecast(self, node: Node, env: Environment) -> LolValue:
        val     = self._eval_expr(node.children[0], env)
        to_type = node.children[1].value
        result  = typecast(val, to_type, explicit=True)
        env.set_it(result)
        return result

    # ── function call ─────────────────────────────────────────────────────

    def _eval_call(self, node: Node, env: Environment) -> LolValue:
        name = node.value
        if name not in self.functions:
            raise RuntimeError_(f'Function "{name}" is not defined')

        func_node = self.functions[name]
        params    = func_node.children[0]  # Parameters node
        body      = func_node.children[1]  # Block node

        # evaluate arguments in caller's environment
        arg_vals = [self._eval_expr(c, env) for c in node.children]

        param_names = [p.value for p in params.children]
        if len(arg_vals) != len(param_names):
            raise RuntimeError_(
                f'Function "{name}" expects {len(param_names)} argument(s), '
                f'got {len(arg_vals)}'
            )

        # create a fresh environment for the function (no access to outer vars)
        func_env = Environment()   # no parent — isolated
        for pname, pval in zip(param_names, arg_vals):
            func_env.set_local(pname, pval)

        result = NOOB_VALUE
        try:
            self._exec_block(body, func_env)
        except FoundYrSignal as ret:
            result = ret.value
        except GtfoSignal:
            result = NOOB_VALUE

        env.set_it(result)
        return result

    # ── notify symbol table ───────────────────────────────────────────────

    def _notify_update(self, env: Environment):
        """Push current variable state to the UI callback."""
        self.update_fn(env.all_vars())


# ─────────────────────────────────────────────────────────────────────────────
# CLI entry point (for quick testing without the GUI)
# ─────────────────────────────────────────────────────────────────────────────

def main():
    import sys
    from lexer import Lexer
    from syntax_analyzer import Parser

    if len(sys.argv) < 2:
        print('Usage: python3 interpreter.py <file.lol>')
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        source = f.read()

    lexer  = Lexer(source)
    tokens = lexer.tokenize()
    if lexer.errors:
        for e in lexer.errors:
            print(e)
        sys.exit(1)

    parser = Parser(tokens)
    tree   = parser.parse()
    if parser.errors:
        for e in parser.errors:
            print(e)
        sys.exit(1)

    interp = Interpreter()
    interp.run(tree)
    if interp.errors:
        for e in interp.errors:
            print(e)


if __name__ == '__main__':
    main()