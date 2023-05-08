from __future__ import annotations
from structure import Tree, Cat

class Lexicon:
    def __init__(self, path: str):
        self.dict: list[tuple[str, Cat]] = []
        self.load_lex(path)
    
    def load_lex(self, path: str):
        with open(path) as file:
            lines = file.readlines()
        for line in lines:
            lst = line.split()
            self.dict.append((lst[0], text_to_cat(lst[1])))

    def get_as_trees(self, word: str) -> list[Tree]:
        lst = []
        for li in self.dict:
            if li[0] == word:
                lst.append(Tree(mt=li[1], pf=word))
        if len(lst) == 0:
            print(f'Error: word "{word}" is not found in the lexicon')
        return lst
    

def text_to_cat(text: str) -> Cat:
    def to_sla(text: str) -> Cat:
        feats = []
        if len(text) == 2:
            if text[1] == '*':
                feats.extend(['-hdiv','-xdiv'])
            elif text[1] == '#':
                feats.append('-xdiv')
            elif text[1] == '%':
                feats.append('-hdiv')
        if text[0] == '/':
            feats.append('+fwd')
        elif text[0] == '\\':
            feats.append('-fwd')
        return Cat(f'[{",".join(feats)}]')
    
    level = 0
    for i in range(len(text)):
        if text[i] == '(':
            level += 1
        elif text[i] == ')':
            level -= 1
        elif level == 1 and text[i] in ['/','\\','|']:
            hd = text_to_cat(text[1:i])
            if text[i+1] in ['*','#','%']:
                arg = text_to_cat(text[i+2:-1])
                sla = to_sla(text[i:i+2])
            else:
                arg = text_to_cat(text[i+1:-1])
                sla = to_sla(text[i])
            return Cat(func=True, hd=hd, val=Cat(sla=sla, arg=arg))
    if text == '_':
        return Cat(func=False)
    if text[-1] == '^':
        return Cat(func=False, cat=text[:-1])
    return Cat(func=False, tr=False, cat=text)