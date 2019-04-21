import ast
import sys


class ASTVisitor(ast.NodeVisitor):
    def __init__(self):
        self.api_seq = []

    def visit(self, node):
        if node is None:
            return
        return super().visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            self.visit(target)
        self.visit(node.value)

    # def visit_AugAssign(self, node):
    #     set_precedence(node, node.value, node.target)
    #     self.statement(node, node.target, get_op_symbol(node.op, ' %s= '),
    #                    node.value)
    #
    # def visit_AnnAssign(self, node):
    #     set_precedence(node, node.target, node.annotation)
    #     set_precedence(Precedence.Comma, node.value)
    #     need_parens = isinstance(node.target, ast.Name) and not node.simple
    #     begin = '(' if need_parens else ''
    #     end = ')' if need_parens else ''
    #     self.statement(node, begin, node.target, end, ': ', node.annotation)
    #     self.conditional_write(' = ', node.value)

    # def visit_Expr(self, node):
    #     self.visit(node.value)
    #
    # def visit_FunctionDef(self, node, is_async=False):
    #     self.append(node.name)
    #     if isinstance(node.args, list):
    #         for arg in node.args:
    #             self.visit(arg)
    #     else:
    #         self.visit(node.args)
    #     for n in node.body:
    #         self.visit(n)
    #     self.visit(node.returns)
    #
    # # introduced in Python 3.5
    # def visit_AsyncFunctionDef(self, node):
    #     self.visit_FunctionDef(node, is_async=True)
    #
    def visit_If(self, node):
        self.append("if")
        self.visit(node.test)
        for body in node.body:
            self.visit(body)
        self.append("else")
        for orelse in node.orelse:
            self.visit(orelse)

    def visit_For(self, node, is_async=False):
        if is_async:
            self.append("async")
        self.append("for")
        self.visit(node.target)
        self.visit(node.iter)
        if node.orelse:
            self.append("else")
            for orelse in node.orelse:
                self.visit(orelse)

    def visit_While(self, node):
        self.append("while")
        self.visit(node.test)
        for body in node.body:
            self.visit(body)
        if node.orelse:
            self.append("else")
            for orelse in node.orelse:
                self.visit(orelse)

    #
    # def visit_With(self, node, is_async=False):
    #     if is_async:
    #         self.append("async")
    #     self.append("with")
    #     for item in node.items:
    #         self.visit(item)
    #     self.visit(node.body)
    #
    # # new for Python 3.5
    # def visit_AsyncWith(self, node):
    #     self.visit_With(node, is_async=True)
    #
    # # new for Python 3.3
    # def visit_withitem(self, node):
    #     self.visit(node.context_expr)
    #     self.visit(node.optional_vars)

    def visit_NameConstant(self, node):
        self.append(node.value)

    def visit_Pass(self, node):
        self.append('pass')

    # def visit_Print(self, node):
    #     # XXX: python 2.6 only
    #     self.append("print")
    #     for value in node.values:
    #         self.visit(value)
    #
    # def visit_Delete(self, node):
    #     self.append('del')
    #     for target in node.targets:
    #         self.visit(target)
    #
    # def visit_TryExcept(self, node):
    #     self.visit_Try(node)
    #     self.visit(node.orelse)
    #
    # # new for Python 3.3
    # def visit_Try(self, node):
    #     self.append("try")
    #     self.visit(node.body)
    #     for handler in node.handlers:
    #         self.visit(handler)
    #
    # def visit_ExceptHandler(self, node):
    #     self.append("except")
    #     self.visit(node.type)
    #     self.visit(node.name)
    #     self.visit(node.body)
    #
    # def visit_TryFinally(self, node):
    #     self.visit_Try(node)
    #     self.append("finally")
    #     self.visit(node.finalbody)

    # def visit_Exec(self, node):
    #     dicts = node.globals, node.locals
    #     dicts = dicts[::-1] if dicts[0] is None else dicts
    #     self.statement(node, 'exec ', node.body)
    #     self.conditional_write(' in ', dicts[0])
    #     self.conditional_write(', ', dicts[1])

    # def visit_Assert(self, node):
    #     set_precedence(node, node.test, node.msg)
    #     self.statement(node, 'assert ', node.test)
    #     self.conditional_write(', ', node.msg)

    # def visit_Global(self, node):
    #     self.statement(node, 'global ', ', '.join(node.names))
    #
    # def visit_Nonlocal(self, node):
    #     self.statement(node, 'nonlocal ', ', '.join(node.names))

    def visit_Return(self, node):
        self.append("return")
        self.visit(node.value)

    def visit_Break(self, node):
        self.append("break")

    def visit_Continue(self, node):
        self.append("continue")

    def visit_Raise(self, node):
        # XXX: Python 2.6 / 3.0 compatibility
        self.append("raise")
        self.visit(node.exc)

    # Expressions

    def visit_Attribute(self, node):
        self.visit(node.value)
        self.append(node.attr)

    # def visit_Call(self, node, len=len):
    #     self.visit(node.func)
    #     args = node.args
    #     for arg in args:
    #         self.visit(arg)
    #     keywords = node.keywords
    #     for keyword in keywords:
    #         # a keyword.arg of None indicates dictionary unpacking
    #         # (Python >= 3.5)
    #         arg = keyword.arg or ''
    #         self.append(arg)
    #         self.visit(keyword.value)

    def visit_Name(self, node):
        self.append(node.id)

    # def visit_JoinedStr(self, node):
    #     for value in node.values:
    #         self.visit(value)

    def visit_Str(self, node, is_joined=False):
        self.append(node.s)

    def visit_Bytes(self, node):
        self.append(repr(node.s))

    def visit_Num(self, node,
                  # constants
                  new=sys.version_info >= (3, 0)):
        self.append(node.n)

    # def visit_Tuple(self, node):
    #     with self.delimit(node) as delimiters:
    #         # Two things are special about tuples:
    #         #   1) We cannot discard the enclosing parentheses if empty
    #         #   2) We need the trailing comma if only one item
    #         elts = node.elts
    #         delimiters.discard = delimiters.discard and elts
    #         self.comma_list(elts, len(elts) == 1)
    #
    # def visit_List(self, node):
    #     with self.delimit('[]'):
    #         self.comma_list(node.elts)
    #
    # def visit_Set(self, node):
    #     if node.elts:
    #         with self.delimit('{}'):
    #             self.comma_list(node.elts)
    #     else:
    #         # If we tried to use "{}" to represent an empty set, it would be
    #         # interpreted as an empty dictionary. We can't use "set()" either
    #         # because the name "set" might be rebound.
    #         self.write('{1}.__class__()')
    #
    # def visit_Dict(self, node):
    #     set_precedence(Precedence.Comma, *node.values)
    #     with self.delimit('{}'):
    #         for idx, (key, value) in enumerate(zip(node.keys, node.values)):
    #             self.write(', ' if idx else '',
    #                        key if key else '',
    #                        ': ' if key else '**', value)
    #
    # def visit_BinOp(self, node):
    #     op, left, right = node.op, node.left, node.right
    #     with self.delimit(node, op) as delimiters:
    #         ispow = isinstance(op, ast.Pow)
    #         p = delimiters.p
    #         set_precedence((Precedence.Pow + 1) if ispow else p, left)
    #         set_precedence(Precedence.PowRHS if ispow else (p + 1), right)
    #         self.write(left, get_op_symbol(op, ' %s '), right)
    #
    # def visit_BoolOp(self, node):
    #     with self.delimit(node, node.op) as delimiters:
    #         op = get_op_symbol(node.op, ' %s ')
    #         set_precedence(delimiters.p + 1, *node.values)
    #         for idx, value in enumerate(node.values):
    #             self.write(idx and op or '', value)
    #
    # def visit_Compare(self, node):
    #     with self.delimit(node, node.ops[0]) as delimiters:
    #         set_precedence(delimiters.p + 1, node.left, *node.comparators)
    #         self.visit(node.left)
    #         for op, right in zip(node.ops, node.comparators):
    #             self.write(get_op_symbol(op, ' %s '), right)
    #
    # def visit_UnaryOp(self, node):
    #     with self.delimit(node, node.op) as delimiters:
    #         set_precedence(delimiters.p, node.operand)
    #         # In Python 2.x, a unary negative of a literal
    #         # number is merged into the number itself.  This
    #         # bit of ugliness means it is useful to know
    #         # what the parent operation was...
    #         node.operand._p_op = node.op
    #         sym = get_op_symbol(node.op)
    #         self.write(sym, ' ' if sym.isalpha() else '', node.operand)
    #
    # def visit_Subscript(self, node):
    #     set_precedence(node, node.slice)
    #     self.write(node.value, '[', node.slice, ']')
    #
    # def visit_Slice(self, node):
    #     set_precedence(node, node.lower, node.upper, node.step)
    #     self.conditional_write(node.lower)
    #     self.write(':')
    #     self.conditional_write(node.upper)
    #     if node.step is not None:
    #         self.write(':')
    #         if not (isinstance(node.step, ast.Name) and
    #                 node.step.id == 'None'):
    #             self.visit(node.step)
    #
    # def visit_Index(self, node):
    #     with self.delimit(node) as delimiters:
    #         set_precedence(delimiters.p, node.value)
    #         self.visit(node.value)
    #
    # def visit_ExtSlice(self, node):
    #     dims = node.dims
    #     set_precedence(node, *dims)
    #     self.comma_list(dims, len(dims) == 1)
    #
    # def visit_Yield(self, node):
    #     with self.delimit(node):
    #         set_precedence(get_op_precedence(node) + 1, node.value)
    #         self.write('yield')
    #         self.conditional_write(' ', node.value)
    #
    # # new for Python 3.3
    # def visit_YieldFrom(self, node):
    #     with self.delimit(node):
    #         self.write('yield from ', node.value)
    #
    # # new for Python 3.5
    # def visit_Await(self, node):
    #     with self.delimit(node):
    #         self.write('await ', node.value)
    #
    # def visit_Lambda(self, node):
    #     with self.delimit(node) as delimiters:
    #         set_precedence(delimiters.p, node.body)
    #         self.write('lambda ')
    #         self.visit_arguments(node.args)
    #         self.write(': ', node.body)
    #
    # def visit_Ellipsis(self, node):
    #     self.write('...')
    #
    # def visit_ListComp(self, node):
    #     with self.delimit('[]'):
    #         self.write(node.elt, *node.generators)
    #
    # def visit_GeneratorExp(self, node):
    #     with self.delimit(node) as delimiters:
    #         if delimiters.pp == Precedence.call_one_arg:
    #             delimiters.discard = True
    #         set_precedence(Precedence.Comma, node.elt)
    #         self.write(node.elt, *node.generators)
    #
    # def visit_SetComp(self, node):
    #     with self.delimit('{}'):
    #         self.write(node.elt, *node.generators)
    #
    # def visit_DictComp(self, node):
    #     with self.delimit('{}'):
    #         self.write(node.key, ': ', node.value, *node.generators)
    #
    # def visit_IfExp(self, node):
    #     with self.delimit(node) as delimiters:
    #         set_precedence(delimiters.p + 1, node.body, node.test)
    #         set_precedence(delimiters.p, node.orelse)
    #         self.write(node.body, ' if ', node.test, ' else ', node.orelse)
    #
    # def visit_Starred(self, node):
    #     self.write('*', node.value)
    #
    # def visit_Repr(self, node):
    #     # XXX: python 2.6 only
    #     with self.delimit('``'):
    #         self.visit(node.value)
    #
    # def visit_Module(self, node):
    #     self.write(*node.body)
    #
    # visit_Interactive = visit_Module
    #
    # def visit_Expression(self, node):
    #     self.visit(node.body)
    #
    # # Helper Nodes
    #
    # def visit_arg(self, node):
    #     self.write(node.arg)
    #     self.conditional_write(': ', node.annotation)
    #
    # def visit_alias(self, node):
    #     self.write(node.name)
    #     self.conditional_write(' as ', node.asname)
    #
    # def visit_comprehension(self, node):
    #     set_precedence(node, node.iter, *node.ifs)
    #     set_precedence(Precedence.comprehension_target, node.target)
    #     stmt = ' async for ' if self.get_is_async(node) else ' for '
    #     self.write(stmt, node.target, ' in ', node.iter)
    #     for if_ in node.ifs:
    #         self.write(' if ', if_)
    def append(self, value):
        if isinstance(value, str):
            value = value.strip()
            if value:
                self.api_seq.append(value)
        else:
            self.api_seq.append(value)
