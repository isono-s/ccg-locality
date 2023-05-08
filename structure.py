from __future__ import annotations
from nltk.featstruct import FeatStruct as FS
from abc import ABCMeta, abstractmethod

class Struct(metaclass=ABCMeta):
    def __init__(self, features = None, **morefeatures) -> None:
        lst = {}
        for k, v in morefeatures.items():
            lst[k] = v.fs if isinstance(v, Struct) else v
        self.fs = FS(features, **lst)
    
    @abstractmethod
    def unify(self, other: Struct) -> Struct | None:
        pass
    
    def has_key(self, key: str) -> bool:
        return self.fs.has_key(key)

    def get(self, path: str | tuple[str]) -> Struct:
        res = self.fs.get(path)
        if isinstance(res, FS):
            new_struct = Tree() if res.has_key('mt') else Cat()
            new_struct.fs = res
            return new_struct
        return res

    @abstractmethod
    def to_text(self) -> str:
        pass

class Tree(Struct):
    def unify(self, other: Tree, trace: bool = False) -> Tree | None:
        new_tree = Tree()
        new_fs = self.fs.unify(other.fs, trace = trace)
        if new_fs is None:
            return None
        new_tree.fs = new_fs
        return new_tree

    def to_text(self, depth: int = 0) -> str:
        cat = self.cat_to_text()
        spaces = f'{"| "*depth}*'
        if self.has_key('ld'):
            ld = self.get('ld').to_text(depth + 1)
            rd = self.get('rd').to_text(depth + 1)
            return f'{spaces}{cat} {self.fs["rule"]}\n{ld}{rd}'
        if self.has_key('d'):
            d = self.get('d').to_text(depth + 1)
            return f'{spaces}{cat} {self.fs["rule"]}\n{d}'
        return f'{spaces}{cat} "{self.fs["pf"]}"\n'
    
    def cat_to_text(self) -> str:
        return self.get('mt').to_text()
    
    def get_complexity(self) -> int:
        return self.cat_to_text().count('(')
    
    def get_enf(self) -> str:
        def to_enf(skelton: list) -> list:
            if (skelton[0] == '>' and
                skelton[1][0] == '>' and
                skelton[1][1][0] == 'B'):
                x_y = skelton[1][1][1]
                y_z = skelton[1][2]
                z = skelton[2]
                return to_enf(['>', x_y, ['>', y_z, z]])
            if (skelton[0] == '<' and
                skelton[2][0] == '<' and
                skelton[2][2][0] == 'B'):
                x = skelton[1]
                y_x = skelton[2][1]
                z_y = skelton[2][2][1]
                return to_enf(['<', ['<', x, y_x], z_y])
            if (skelton[0] == '>' and
                skelton[1][0] == 'B' and 
                skelton[1][1][0] == '>' and
                skelton[1][1][1][0] == 'B'):
                x_y = skelton[1][1][1][1]
                y_z = skelton[1][1][2]
                z_w = skelton[2]
                return to_enf(['>', ['B', x_y], ['>', ['B', y_z], z_w]])
            if (skelton[0] == '>' and
                skelton[1][0] == 'Bx\\' and 
                skelton[1][1][0] == '>' and
                skelton[1][1][1][0] == 'B'):
                x_y = skelton[1][1][1][1]
                y_z = skelton[1][1][2]
                z_w = skelton[2]
                return to_enf(['>', ['Bx\\', x_y], ['>', ['Bx\\', y_z], z_w]])
            if (skelton[0] == '<' and
                skelton[2][0] == 'B' and
                skelton[2][1][0] == '<' and
                skelton[2][1][2][0] == 'B'):
                x_y = skelton[1]
                z_x = skelton[2][1][1]
                w_z = skelton[2][1][2][1]
                return to_enf(['<', ['<', x_y, ['B', z_x]], ['B', w_z]])
            if (skelton[0] == '<' and
                skelton[2][0] == 'Bx/' and
                skelton[2][1][0] == '<' and
                skelton[2][1][2][0] == 'B'):
                x_y = skelton[1]
                z_x = skelton[2][1][1]
                w_z = skelton[2][1][2][1]
                return to_enf(['<', ['<', x_y, ['Bx/', z_x]], ['Bx/', w_z]])
            if (skelton[0] == '>' and
                skelton[1][0] == '>T'):
                x = skelton[1][1]
                y_x = skelton[2]
                return to_enf(['<', x, y_x])
            if (skelton[0] == '<' and
                skelton[2][0] == '<T'):
                x_y = skelton[1]
                y = skelton[2][1]
                return to_enf(['>', x_y, y])
            if len(skelton) == 3:
                return [skelton[0], to_enf(skelton[1]), to_enf(skelton[2])]
            if len(skelton) == 2:
                return [skelton[0], to_enf(skelton[1])]
            return skelton

        if enf := self.get('enf'):
            return enf
        enf = str(to_enf(self.get_skelton()))
        self.fs['enf'] = enf
        return enf
    
    def get_skelton(self) -> list:
        if self.get('ld'):
            return [self.get('rule'), self.get('ld').get_skelton(), self.get('rd').get_skelton()]
        if self.get('d'):
            return [self.get('rule'), self.get('d').get_skelton()]
        return '.'
        

class Cat(Struct):
    def unify(self, other: Cat) -> Cat | None:
        new_cat = Cat()
        new_fs = self.fs.unify(other.fs)
        if new_fs is None:
            return None
        new_cat.fs = new_fs
        return new_cat
    
    def to_text(self) -> str:
        def sla_to_text(sla: str | None) -> str:
            if sla is None:
                return '|'
            if sla.get('fwd') is None:
                bar = '|'
            elif sla.get('fwd'):
                bar = '/' 
            else:
                bar = '\\'
            if sla.get('hdiv') is False:
                if sla.get('xdiv') is False:
                    mode = '*'
                else:
                    mode = '%'
            else:
                if sla.get('xdiv') is False:
                    mode = '#'
                else:
                    mode = ''
            return bar + mode
        
        if cat := self.get('cat'):
            return cat + ('' if self.get('tr') is False else '^')
        if not self.get('func'):
            return '?'
        hd = self.get('hd')
        hd_text = hd.to_text() if hd else '?'
        arg = self.get(('val','arg'))
        arg_text = arg.to_text() if arg else '?'
        sla = sla_to_text(self.get(('val', 'sla')))
        return f'({hd_text}{sla}{arg_text})'