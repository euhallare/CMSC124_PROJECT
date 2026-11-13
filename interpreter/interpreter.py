#LOLCODE Interpreter — Interpreter class (AST executor)
#Milestone 3 - Semantic Analysis


import sys

from parser.nodes import Node
from .values import LolValue, NOOB_VALUE, TYPE_NUMBR, TYPE_NUMBAR
from .signals import RuntimeError_, GtfoSignal, FoundYrSignal
from .typecasting import typecast, to_yarn, to_troof, coerce_arithmetic
from .environment import Environment


class Interpreter:
    """
    Walks the AST and executes it.

    output_fn  : callable(str)        — called for every VISIBLE output line
    input_fn   : callable(str) → str  — called for GIMMEH; arg is prompt text
    update_fn  : callable(dict)       — called after each statement to refresh
                                        the symbol table; dict is name→LolValue
    """

    def __init__(self, output_fn=None, input_fn=None, update_fn=None):
        self.output_fn = output_fn or print
        self.input_fn  = input_fn  or input
        self.update_fn = update_fn or (lambda d: None)
        self.functions = {}   # name → Node('Function', ...)
        self.env       = None
        self.errors    = []

    #Public entry point
    def run(self, tree: Node):
        """Execute the program tree. Returns the final environment."""
        self.env    = Environment()
        self.errors = []
        try:
            self._exec_program(tree)
        except RuntimeError_ as e:
            msg = 'Runtime Error'
            if e.line_num:
                msg += f' (line {e.line_num})'
            msg += f': {e.message}'
            self.errors.append(msg)
        except Exception as e:
            self.errors.append(f'Unexpected error: {e}')
        return self.env

    #Program structure

    def _exec_program(self, node: Node):
        #collect all function definitions first
        for child in node.children:
            if child.label == 'Function':
                self.functions[child.value] = child

        for child in node.children:
            if child.label == 'Declarations':
                self._exec_declarations(child)
            elif child.label == 'Block':
                self._exec_block(child, self.env)
            #version and Function nodes are skipped here

    def _exec_declarations(self, node: Node):
        for decl in node.children:
            self._exec_declaration(decl, self.env)

    def _exec_declaration(self, node: Node, env: Environment):
        name = node.children[0].value
        if len(node.children) > 1:
            init_node = node.children[1]   # Initializer node
            val = self._eval_expr(init_node.children[0], env)
        else:
            val = NOOB_VALUE
        env.set_local(name, val)
        self._notify_update(env)

    #block / statement dispatch 
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
            self.functions[node.value] = node
        else:
            raise RuntimeError_(f'Unknown statement type: {label}')

    #Print 
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

    #Input

    def _exec_input(self, node: Node, env: Environment):
        var_name = node.children[0].value
        raw      = self.input_fn(f'Input for {var_name}: ')
        val      = LolValue(str(raw), 'YARN')
        env.set(var_name, val)
        self._notify_update(env)

    #Assignment

    def _exec_assignment(self, node: Node, env: Environment):
        var_name = node.children[0].value
        val      = self._eval_expr(node.children[1], env)
        if not env.has(var_name):
            raise RuntimeError_(f'Variable "{var_name}" is not defined. Declare it in WAZZUP.')
        env.set(var_name, val)
        env.set_it(val)
        self._notify_update(env)

    #Recast (IS NOW A)

    def _exec_recast(self, node: Node, env: Environment):
        var_name = node.children[0].value
        to_type  = node.children[1].value
        cur_val  = env.get(var_name)
        new_val  = typecast(cur_val, to_type, explicit=True)
        env.set(var_name, new_val)
        self._notify_update(env)

    #If-then

    def _exec_if(self, node: Node, env: Environment):
        condition = to_troof(env.get_it())

        ya_rly = None
        no_wai = None
        mebbes = []

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
            executed = False
            for mebbe in mebbes:
                mebbe_cond = to_troof(self._eval_expr(mebbe.children[0], env))
                if mebbe_cond:
                    self._exec_block(mebbe.children[1], env)
                    executed = True
                    break
            if not executed and no_wai:
                self._exec_block(no_wai.children[0], env)

    #Switch

    def _exec_switch(self, node: Node, env: Environment):
        it_val  = env.get_it()
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
        #equality check for switch-case (no auto typecast per spec).
        if a.type != b.type:
            return False
        return a.value == b.value

    #loop

    def _exec_loop(self, node: Node, env: Environment):
        op_node   = None
        var_node  = None
        cond_node = None
        body      = None

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
                if cond_node:
                    cond_val  = self._eval_expr(cond_node.children[0], env)
                    cond_bool = to_troof(cond_val)
                    if cond_node.value == 'TIL'  and cond_bool:
                        break
                    if cond_node.value == 'WILE' and not cond_bool:
                        break

                self._exec_block(body, env)

                if op_node and var_node:
                    cur     = env.get(var_node.value)
                    cur_num = typecast(cur, TYPE_NUMBR)
                    if op_node.value == 'UPPIN':
                        new_val = LolValue(cur_num.value + 1, TYPE_NUMBR)
                    else:  #NERFIN
                        new_val = LolValue(cur_num.value - 1, TYPE_NUMBR)
                    env.set(var_node.value, new_val)
                    self._notify_update(env)

        except GtfoSignal:
            pass

    #Expression evaluator

    def _eval_expr(self, node: Node, env: Environment) -> LolValue:
        label = node.label

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

    #Literal
    def _eval_literal(self, node: Node) -> LolValue:
        label = node.label
        raw   = node.value

        if 'NUMBR' in label and 'NUMBAR' not in label:
            return LolValue(int(raw), TYPE_NUMBR)
        if 'NUMBAR' in label:
            return LolValue(float(raw), TYPE_NUMBAR)
        if 'YARN' in label:
            return LolValue(raw[1:-1], 'YARN')   # strip surrounding quotes
        if 'TROOF' in label:
            return LolValue(raw == 'WIN', 'TROOF')
        raise RuntimeError_(f'Unknown literal type in node: {label}')

    #Binary op

    def _eval_binary(self, node: Node, env: Environment) -> LolValue:
        op    = node.value
        left  = self._eval_expr(node.children[0], env)
        right = self._eval_expr(node.children[1], env)

        if op in ('SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF',
                  'BIGGR OF', 'SMALLR OF'):
            return self._eval_arithmetic(op, left, right)

        if op == 'BOTH OF':
            return LolValue(to_troof(left) and to_troof(right), 'TROOF')
        if op == 'EITHER OF':
            return LolValue(to_troof(left) or  to_troof(right), 'TROOF')
        if op == 'WON OF':
            return LolValue(to_troof(left) !=  to_troof(right), 'TROOF')

        if op == 'BOTH SAEM':
            return LolValue(self._compare_equal(left, right), 'TROOF')
        if op == 'DIFFRINT':
            return LolValue(not self._compare_equal(left, right), 'TROOF')

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
        #Equality per spec — no automatic typecasting for comparison
        if a.type == 'NUMBR'  and b.type == 'NUMBR':
            return a.value == b.value
        if a.type == 'NUMBAR' and b.type == 'NUMBAR':
            return a.value == b.value
        if a.type == 'YARN'   and b.type == 'YARN':
            return a.value == b.value
        if a.type == 'TROOF'  and b.type == 'TROOF':
            return a.value == b.value
        # Mixed numeric — allow NUMBR vs NUMBAR
        if a.type in ('NUMBR', 'NUMBAR') and b.type in ('NUMBR', 'NUMBAR'):
            return float(a.value) == float(b.value)
        return False

    #Unary op

    def _eval_unary(self, node: Node, env: Environment) -> LolValue:
        op  = node.value
        val = self._eval_expr(node.children[0], env)
        if op == 'NOT':
            return LolValue(not to_troof(val), 'TROOF')
        raise RuntimeError_(f'Unknown unary op: {op}')

    #Variadic op
    def _eval_variadic(self, node: Node, env: Environment) -> LolValue:
        op = node.value

        if op == 'SMOOSH':
            parts = [to_yarn(self._eval_expr(c, env)) for c in node.children]
            return LolValue(''.join(parts), 'YARN')

        vals = [to_troof(self._eval_expr(c, env)) for c in node.children]

        if op == 'ALL OF':
            return LolValue(all(vals), 'TROOF')
        if op == 'ANY OF':
            return LolValue(any(vals), 'TROOF')

        raise RuntimeError_(f'Unknown variadic op: {op}')

    #Typecast (MAEK)

    def _eval_typecast(self, node: Node, env: Environment) -> LolValue:
        val     = self._eval_expr(node.children[0], env)
        to_type = node.children[1].value
        result  = typecast(val, to_type, explicit=True)
        env.set_it(result)
        return result

    #Function call
    def _eval_call(self, node: Node, env: Environment) -> LolValue:
        name = node.value
        if name not in self.functions:
            raise RuntimeError_(f'Function "{name}" is not defined')

        func_node   = self.functions[name]
        params      = func_node.children[0]   # Parameters node
        body        = func_node.children[1]   # Block node

        #evaluate arguments in caller's environment
        arg_vals    = [self._eval_expr(c, env) for c in node.children]
        param_names = [p.value for p in params.children]

        if len(arg_vals) != len(param_names):
            raise RuntimeError_(
                f'Function "{name}" expects {len(param_names)} argument(s), '
                f'got {len(arg_vals)}'
            )

        #fresh environment — no access to outer vars (pass-by-value)
        func_env = Environment()
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

    #Notify symbol table
    def _notify_update(self, env: Environment):
        #Push current variable state to the UI callback.
        self.update_fn(env.all_vars())


#CLI entry point

def main():
    from lexer import Lexer
    from parser import Parser

    if len(sys.argv) < 2:
        print('Usage: python3 -m interpreter <file.lol>')
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