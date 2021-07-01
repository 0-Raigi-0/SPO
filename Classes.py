class Item:
    def __init__(s, value=None):
        s.value = value
        s.nextValue = None

class LList:
    def __init__(s):
        s.head = None

    def __repr__(s):
        cur = s.head
        sk = '[ '
        while cur is not None:
            sk += f'{cur.value},'
            cur = cur.nextValue
        sk += ']'
        return sk

    def cont(s, value):

        LIm = s.head
        while LIm:
            if value == LIm.value:
                return True
            else:
                LIm = LIm.nextValue
        return False

    def push(s, newValue):
        NIm = Item(newValue)
        if s.head is None:
            s.head = NIm
            return
        LIm = s.head
        while LIm.nextValue:
            LIm = LIm.nextValue
        LIm.nextValue = NIm

    def get(s, ImIx):
        LIm = s.head
        BIx = 0
        while BIx <= ImIx:
            if BIx == ImIx:
                return LIm.cat
            BIx = BIx + 1
            LIm = LIm.nextValue

    def rm(s, rmValue):
        HIm = s.head

        if HIm is not None:
            if HIm.value == rmValue:
                s.head = HIm.nextValue
                return
        while HIm is not None:
            if HIm.value == rmValue:
                break
            LIm = HIm
            HIm = HIm.nextValue
        if HIm is None:
            return
        LIm.nextValue = HIm.nextValue

class Node:
    def __init__(s, name='', value='', height=0):
        s.children = []
        s.name = name
        s.value = value
        s.height = height
        s.buffer = []

    def __repr__(s):
        str_end = ''
        for child in s.children:
            str_end += "\t" * child.height + f'{child}'
        return f'{s.name}\n{str_end}'

class List:
    def __init__(s, name='', value='', height=0):
        s.name = name
        s.value = value
        s.height = height

    def __repr__(s):
        return f'{s.name} {s.value}\n'    
