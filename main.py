from Core import Lex, StM, Par


if __name__ == '__main__':
    L = Lex()
    L.get_term('code.txt')
    print('Tokens:', L.l_tokens)
    try:
        P = Par(L.l_tokens)
        Tree = P.S()
        print('Tree:\n', Tree)
        StM = StM(Tree.children)
        StM.start()
    except BaseException:
        print('Syntax error')
