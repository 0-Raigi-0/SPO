import re
from Classes import LList, Node, List



class Lex(object):
    token = {"ЕСЛИ": "^if$", "ИНАЧЕ": "^else$", "ПОКА": "^while$", "ОПЕРАЦИЯ": "^[-+*/]$", "Л_ОПЕРАЦИЯ": r"^==|>|>=|<|<=|!=$",
              "Л_СКОБКА ": "[(]", "П_СКОБКА": "[)]", 'ТОЧКА': r'\.', "Л_ФИГУРНАЯ": "^[{]$",
             'С_СПИСОК': r'LList', "П_ФИГУРНАЯ": "^[}]$", "ОПЕРАЦИЯ_П": "^=$",
              "КОНЕЦ": "^;$", "ЧИСЛО": r"^0|([1-9][0-9]*)$", "СТРОКА": r"'[^']*'", "ПЕРЕМЕННАЯ": "^[a-zA-Z0-9_]+$", "НЕ_ОПРЕДЕЛЕНО": r".*[^.]*"}

    def __init__(s):
        s.l_tokens = []

    def __set_token(s, item):
        for key in s.token.keys():
            if re.fullmatch(s.token[key], item):
                return key

    def get_term(s, file):
        with open(file) as f_hand:
            buf = ''
            l_token = ''
            for line in f_hand:
                for char in line:
                    if not len(buf) and char == "'":
                        buf += char
                        continue
                    elif len(buf) and not buf.count("'") == 2:
                        if buf[0] == "'":
                            buf += char
                            continue

                    if l_token == 'ТОЧКА':
                        if not char == '(':
                            buf += char
                            continue
                        else:
                            s.l_tokens.append({'МЕТОД': buf})
                            buf = ''

                    l_token = s.__set_token(buf)
                    buf += char
                    token = s.__set_token(buf)

                    if token == "НЕ_ОПРЕДЕЛЕНО":
                        if len(buf) and not l_token == "НЕ_ОПРЕДЕЛЕНО":
                            s.l_tokens.append({l_token: buf[:-1]})
                        if not (buf[-1] == ' ' or buf[-1] == '\n'):
                            buf = buf[-1]
                        else:
                            buf = ''

            token = s.__set_token(buf)
            if not token == "НЕ_ОПРЕДЕЛЕНО":
                s.l_tokens.append({token: buf[0]})


class StM:
    pr = {'(': 0, ')': 1, '=': 1, '==': 3, '!=': 3, '>': 4, '>=': 4, '<': 4, '<=': 4, '+': 5, '-': 5, '*': 6, '/': 6,
          'cont': 7, 'rm': 7, 'push': 7, 'get': 7}
    log_op = ['==', '!=', '>', '>=', '<', '<=']
    op = ['+', '-', '*', '/']
    list_com = ['cont', 'rm', 'push', 'get']

    def __init__(s, inp):
        s.stack = []
        s.input = inp
        s.output = []
        s.buf = []
        s.bufel = []
        s.nl = 0
        s.index = -1
        s.variables = {}

    @staticmethod
    def b_log_op(a, b, op):
        if op == '>':
            return a > b
        elif op == '<':
            return a < b
        elif op == '>=':
            return a >= b
        elif op == '<=':
            return a <= b
        elif op == '==':
            return a == b
        elif op == '!=':
            return a != b

    @staticmethod
    def b_op(a, b, op):
        if op == '+':
            return a + b
        elif op == '-':
            return a - b
        elif op == '*':
            return a * b
        elif op == '/':
            return a / b

    @staticmethod
    def methodList(a, b, op):
        if op == 'push':
            a.push(b)
        elif op == 'rm':
            a.rm(b)
        elif op == 'get':
            a.get(b)
        elif op == 'cont':
            a.cont(b)

    def assign(s, a, b):
        if re.fullmatch(r"0|([1-9][0-9]*)", str(b)):
            s.variables[a] = int(b)
        elif b == 'LList':
            s.variables[a] = LList()
        else:
            s.variables[a] = b

    def abs(s, item):
        if item.name == 'while_expr':
            s.buf.append({s.nl: len(s.output)})

        if item.name not in Lex.token and not item.name == 'МЕТОД':
            for i in item.children:
                s.abs(i)

            s.stack.reverse()
            for y in s.stack:
                if not y == '(':
                    s.output.append(y)

            s.stack = []

        else:
            if item.name == 'ИНАЧЕ':
                s.bufel.append(s.nl)
                s.output.append('\t')

            if item.name == 'П_ФИГУРНАЯ':
                s.nl -= 1
                if '\n' in s.output:
                    s.output.reverse()
                    s.output[s.output.index('\n')] = len(s.output)
                    s.output.reverse()

                if len(s.buf):
                    if s.nl in list(s.buf[-1].keys()):
                        s.output.append('!' + str(s.buf[-1][s.nl]))
                        s.buf.pop(-1)

            if item.name == 'Л_ФИГУРНАЯ':
                s.nl += 1
                if s.nl > 0:
                    s.output.append('\n')

            if len(s.bufel) and not item.name == 'ИНАЧЕ':
                if s.nl == s.bufel[-1]:
                    s.output.reverse()
                    s.output[s.output.index('\t')] =\
                        '!' + str(len(s.output))
                    s.output.reverse()
                    s.bufel.pop(-1)

            if item.name in ['ПЕРЕМЕННАЯ', 'ЧИСЛО', 'ЧИСЛО', 'С_СПИСОК']:
                s.output.append(str(item.value))

            else:
                if not item.value == '':
                    k = 0
                    for i in range(len(s.stack) - 1, -1, -1):
                        k += 1
                        if item.value == ')':
                            if not s.stack[i] == '(':
                                s.output.append(s.stack[i])
                            else:
                                break
                        elif s.pr[item.value] <= s.pr[s.stack[i]] \
                                and not item.value == '(':
                            s.output.append(s.stack[i])
                        else:
                            break

                    for j in range(1, k):
                        s.stack.pop(-j)

                    if not item.value == ')':
                        s.stack.append(item.value)

    def start(s):
        try:
            for item in s.input:
                s.abs(item)
                s.stack = []
            print(s.output)
            s.compil()
            print(s.variables)
        except BaseException:
            raise BaseException

    def compil(s):
        k = 0

        while k < len(s.output):
            if not s.output[k] in list(s.pr.keys()):
                if not (str(type(s.output[k])) == "<class 'int'>" or
                        list(s.output[k])[0] == '!'):
                    s.stack.append(s.output[k])
                    k += 1

                elif len(s.stack):
                    if not s.stack[-1] and\
                            not list(str(s.output[k]))[0] == '!':
                        if not s.stack[-1]:
                            if (s.output[k]) < len(s.output):
                                if isinstance(s.output[s.output[k]],
                                              int):
                                    k = s.output[k] + 1
                                    s.stack.pop(-1)
                                    continue
                                elif list(str(s.output[s.output[k]]))[0]\
                                        == '!':
                                    k = s.output[k] + 1
                                    s.stack.pop(-1)
                                    continue
                                else:
                                    k = s.output[k]
                                    s.stack.pop(-1)
                                    continue
                            else:
                                k = s.output[k] + 1
                                s.stack.pop(-1)
                                continue

                    elif list(str(s.output[k]))[0] == '!':
                        k = s.output[k]
                        continue

                    else:
                        s.stack.pop(-1)

                elif list(str(s.output[k]))[0] == '!':
                    k = int(str(s.output[k])[1:])
                    continue

                else:
                    k += 1

            else:
                b = s.stack.pop(-1)
                a = s.stack.pop(-1)
                op = s.output[k]
                k += 1
                if op == '=':
                    s.assign(a, b)

                elif op in s.log_op:
                    s.stack.append(s.b_log_op(s.variables[a],
                                                      s.variables[b], op))

                elif op in s.op:
                    if not re.fullmatch(r"0|([1-9][0-9]*)", a):
                        a = s.variables[a]
                    else:
                        a = int(a)
                    if not re.fullmatch(r"0|([1-9][0-9]*)", b):
                        b = int(s.variables[b])
                    else:
                        b = int(b)
                    s.stack.append(s.b_op(a, b, op))

                elif op in s.list_com:
                    s.stack.append(s.methodList(s.variables[a], b, op))

                    
class Par:
    def __init__(s, Lex):
        s.height = 0
        s.i = 0
        s.start = Lex
        s.LB = 0

    def S(s):
        S = Node('S')
        while s.i < len(s.start) - 1:
            s.height = 1
            expr = s.expr()
            if expr is not None:
                S.children.append(expr)
            s.i += 1

        return S

    def expr(s):
        try:
            expr = Node('expr', height=s.height)
            s.height += 1

            token = list(s.start[s.i].keys())[0]

            if token == "ПЕРЕМЕННАЯ":
                try:
                    assign_expr = s.assign_expr()
                    expr.children.append(assign_expr)
                    s.height -= 1
                    return expr

                except BaseException:
                    expr.children.append(List(list(s.start[s.i].keys())[0], list(s.start[s.i].values())[0],
                                              s.height))
                    s.check_next('ТОЧКА')
                    s.i += 1
                    method = s.method()
                    expr.children.append(method)
                    return expr

            elif token == 'ПОКА':
                while_expr = s.while_expr()
                expr.children.append(while_expr)
                s.height -= 1
                return expr

            elif token == 'ЕСЛИ':
                if_expr = s.if_expr()
                expr.children.append(if_expr)
                s.height -= 1
                return expr

            else:
                return None
        except BaseException:
            raise BaseException

    def method(s):
        method = Node('method', height=s.height)
        s.height += 1
        s.check_next('МЕТОД')
        s.i += 1
        method.children.append(List(name=list(s.start[s.i].keys())[0], value=list(s.start[s.i].values())[0],
                               height=s.height))
        s.height += 1
        s.check_next('Л_СКОБКА ')
        s.i += 1
        method.children.append(List(name=list(s.start[s.i].keys())[0], value=list(s.start[s.i].values())[0],
                                    height=s.height))
        math_expr = s.math_expr()
        method.children.append(math_expr)

        if not list(s.start[s.i].keys())[0] == 'КОНЕЦ':
            raise BaseException

        return method

    def if_expr(s):
        height = s.height
        if_expr = Node('if_expr', height=s.height)
        s.height += 1
        start_height = s.height
        s.check_next('Л_СКОБКА ')
        if_expr.children.append(List('Л_СКОБКА ', '(', height=s.height))
        s.i += 2
        s.height += 1
        token = list(s.start[s.i].keys())[0]

        if token == 'ПЕРЕМЕННАЯ' or token == 'ЧИСЛО' or token == 'Л_СКОБКА ':
            math_logic = s.math_logic(ht=[start_height])
            if_expr.children.append(math_logic)

            s.height = start_height
            s.check_next('Л_ФИГУРНАЯ')
            if_expr.children.append(Node('Л_ФИГУРНАЯ', height=start_height))
            s.i += 1
            num_L = 1
            while num_L:
                if list(s.start[s.i].keys())[0] == 'П_ФИГУРНАЯ':
                    num_L -= 1
                if list(s.start[s.i].keys())[0] == 'Л_ФИГУРНАЯ':
                    num_L += 1
                if num_L:
                    s.i += 1
                    s.height = start_height
                    s.height += 1
                    if list(s.start[s.i].keys())[0] == 'Л_ФИГУРНАЯ':
                        num_L += 1
                    if list(s.start[s.i].keys())[0] == 'П_ФИГУРНАЯ':
                        num_L -= 1
                        break
                    expr = s.expr()
                    if expr is not None:
                        if_expr.children.append(expr)

            if_expr.children.append(Node('П_ФИГУРНАЯ', height=start_height))

            if s.i < len(s.start) - 1:
                s.check_next('ИНАЧЕ')
                s.i += 1
                s.check_next('Л_ФИГУРНАЯ')
                s.height = height
                if_expr.children.append(Node('ИНАЧЕ', height=s.height))
                s.height += 1
                start_height = s.height
                if_expr.children.append(Node('Л_ФИГУРНАЯ', height=s.height))
                num_L = 1

                while num_L:

                    if list(s.start[s.i].keys())[0] == 'П_ФИГУРНАЯ':
                        num_L -= 1
                    if list(s.start[s.i].keys())[0] == 'Л_ФИГУРНАЯ':
                        num_L += 1
                    if num_L:
                        s.i += 1
                        s.height = start_height
                        s.height += 1
                        if list(s.start[s.i].keys())[0] == 'Л_ФИГУРНАЯ':
                            num_L += 1
                        if list(s.start[s.i].keys())[0] == 'П_ФИГУРНАЯ':
                            num_L -= 1
                            break
                        expr = s.expr()
                        if expr is not None:
                            if_expr.children.append(expr)

                if_expr.children.append(Node('П_ФИГУРНАЯ', height=start_height))
            return if_expr

    def while_expr(s):
        while_expr = Node('while_expr', height=s.height)
        s.height += 1
        start_height = s.height
        s.check_next('Л_СКОБКА ')
        while_expr.children.append(List('Л_СКОБКА ', '(', height=s.height))
        s.i += 2
        s.height += 1
        token = list(s.start[s.i].keys())[0]
        if token == 'ПЕРЕМЕННАЯ' or token == 'ЧИСЛО' or token == 'Л_СКОБКА ':
            math_logic = s.math_logic(ht=[start_height])
            while_expr.children.append(math_logic)

            s.height = start_height
            s.check_next('Л_ФИГУРНАЯ')
            s.i += 1
            while_expr.children.append(Node('Л_ФИГУРНАЯ', height=s.height))
            num_L = 1

            while num_L:
                if list(s.start[s.i].keys())[0] == 'П_ФИГУРНАЯ':
                    num_L -= 1
                if list(s.start[s.i].keys())[0] == 'Л_ФИГУРНАЯ':
                    num_L += 1

                if num_L:
                    s.i += 1
                    s.height = start_height
                    s.height += 1
                    if list(s.start[s.i].keys())[0] == 'Л_ФИГУРНАЯ':
                        num_L += 1
                    if list(s.start[s.i].keys())[0] == 'П_ФИГУРНАЯ':
                        num_L -= 1
                        break
                    expr = s.expr()
                    if expr is not None:
                        while_expr.children.append(expr)

            while_expr.children.append(Node('П_ФИГУРНАЯ', height=start_height))
            return while_expr
        else:
            raise BaseException

    def math_logic(s, ht=[]):
        token = list(s.start[s.i].keys())[0]

        if not token == 'П_СКОБКА' or not token == 'Л_ОПЕРАЦИЯ' \
                or not token == 'ОПЕРАЦИЯ':
            math_logic = Node('math_logic', height=s.height)
        else:
            math_logic = ''
        s.height += 1

        if token == 'Л_СКОБКА ':
            ht.append(s.height)
            LBreaket = s.LBreaket()
            math_logic.children.append(LBreaket)

        elif token == 'П_СКОБКА':
            s.height = ht.pop(-1)
            math_logic = Node('П_СКОБКА',  height=s.height)

        elif token == 'ЧИСЛО':
            math_logic.children.append(List(list(s.start[s.i].keys())[0],
                                            list(s.start[s.i].
                                                 values())[0],
                                            s.height))

            if s.i + 1 < len(s.start):
                if list(s.start[s.i + 1].keys())[0] == 'Л_ОПЕРАЦИЯ':
                    s.i += 1
                    math_logic.children.append(List(list(s.start[s.i].
                                                         keys())[0],
                                                    list(s.start[s.i].
                                                         values())[0],
                                                    s.height))

                elif list(s.start[s.i + 1].keys())[0] == 'ОПЕРАЦИЯ':
                    s.i += 1
                    math_logic.children.append(List(list(s.start[s.i].
                                                         keys())[0],
                                                    list(s.start[s.i].
                                                         values())[0],
                                                    s.height))

        elif token == 'ПЕРЕМЕННАЯ':
            math_logic.children.append(List(list(s.start[s.i].keys())[0],
                                            list(s.start[s.i].
                                                 values())[0],
                                            s.height))

            if s.i + 1 < len(s.start):
                if list(s.start[s.i + 1].keys())[0] == 'Л_ОПЕРАЦИЯ':
                    s.i += 1
                    math_logic.children.append(List(list(s.start[s.i].
                                                         keys())[0],
                                                    list(s.start[s.i].
                                                         values())[0],
                                                    s.height))

                elif list(s.start[s.i + 1].keys())[0] == 'ОПЕРАЦИЯ':
                    s.i += 1
                    math_logic.children.append(List(list(s.start[s.i].
                                                         keys())[0],
                                                    list(s.start[s.i].
                                                         values())[0],
                                                    s.height))

        elif token == 'Л_ОПЕРАЦИЯ':
            s.height -= 1
            math_logic = Node('Л_ОПЕРАЦИЯ' +
                              list(s.start[s.i].values())[0],
                              height=s.height)

        elif token == 'ОПЕРАЦИЯ':
            s.height -= 1
            math_logic = Node('ОПЕРАЦИЯ' + list(s.start[s.i].values())[0],
                              height=s.height)

        elif not token == 'КОНЕЦ':
            raise BaseException

        if len(ht):
            s.i += 1
            me = s.math_logic(ht)
            math_logic.children.append(me)

        return math_logic

    def check_next(s, values):
        token = list(s.start[s.i + 1].keys())[0]
        if not token == values:
            raise BaseException

    def assign_expr(s):
        assign_expr = Node('Н_ВЫРАЖ', '=', s.height)
        s.check_next("ОПЕРАЦИЯ_П")
        s.height += 1
        assign_expr.children.append(List(list(s.start[s.i].keys())[0],
                                         list(s.start[s.i].
                                              values())[0], s.height))
        s.i += 1
        assign_expr.children.append(List(list(s.start[s.i].keys())[0],
                                         list(s.start[s.i].
                                              values())[0], s.height))
        s.height -= 1
        s.i += 1
        token = list(s.start[s.i].keys())[0]
        if token == 'СТРОКА':
            s.height += 1
            assign_expr.children.append(List('СТРОКА', list(s.start[s.i].
                                                         values())[0],
                                             s.height))
            s.check_next('КОНЕЦ')
            s.i += 1

        elif token == 'ЧИСЛО' or token == 'Л_СКОБКА ' or token == 'ПЕРЕМЕННАЯ':
            s.height += 1
            math_expr = s.math_expr()
            assign_expr.children.append(math_expr)

        elif token == 'С_СПИСОК':
            s.height += 1
            assign_expr.children.append(List('С_СПИСОК', list(s.start[s.i].values())[0], s.height))

        return assign_expr

    def math_expr(s, ht=[]):
        token = list(s.start[s.i].keys())[0]
        if not token == 'П_СКОБКА' or not token == 'ОПЕРАЦИЯ' or not token == 'ТОЧКА':
            math_expr = Node('math_expr', height=s.height)
        else:
            math_expr = ''
        s.height += 1

        if token == 'Л_СКОБКА ':
            ht.append(s.height)
            LBreaket = s.LBreaket()
            math_expr.children.append(LBreaket)

        elif token == 'П_СКОБКА':
            s.LB -= 1
            s.height = ht.pop(-1)
            if s.LB < 0:
                raise BaseException
            math_expr = Node('П_СКОБКА', value=')', height=s.height)

        elif token == 'ЧИСЛО':
            math_expr.children.append(List(list(s.start[s.i].keys())[0],
                                           list(s.start[s.i].
                                                values())[0],
                                           s.height))

            if s.i + 1 < len(s.start):
                if list(s.start[s.i + 1].keys())[0] == 'ОПЕРАЦИЯ':
                    s.i += 1
                    math_expr.children.append(List(list(s.start[s.i].
                                                        keys())[0],
                                                   list(s.start[s.i].
                                                        values())[0],
                                                   s.height))

        elif token == 'ОПЕРАЦИЯ':
            s.height -= 1
            math_expr = Node('ОПЕРАЦИЯ' + list(s.start[s.i].values())[0],
                             height=s.height)

        elif token == 'ПЕРЕМЕННАЯ':
            math_expr.children.append(List(list(s.start[s.i].keys())[0],
                                           list(s.start[s.i].
                                                values())[0],
                                           s.height))

            if s.i + 1 < len(s.start):
                if list(s.start[s.i + 1].keys())[0] == 'ОПЕРАЦИЯ':
                    s.i += 1
                    math_expr.children.append(List(list(s.start[s.i].
                                                        keys())[0],
                                                   list(s.start[s.i].
                                                        values())[0],
                                                   s.height))

        elif token == 'ТОЧКА':
            math_expr = s.method()
            s.i -= 1
        elif not token == 'КОНЕЦ':
            raise BaseException

        s.i += 1
        if not list(s.start[s.i].keys())[0] == 'КОНЕЦ':
            me = s.math_expr(ht)
            math_expr.children.append(me)

        return math_expr

    def LBreaket(s):
        s.LB += 1
        LBreaket = List('Л_СКОБКА ', '(', height=s.height)

        return LBreaket

