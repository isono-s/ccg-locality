from __future__ import annotations
from structure import Tree

class Rules:
    @classmethod
    def try_unary_rules(cls, dtr: Tree) -> list[Tree]:
        lst: list[Tree] = []
        for rule in [fwd_tr, bwd_tr, h_div, fwd_x_div, bwd_x_div]:
            if f := rule.unify(Tree(d=dtr)):
                lst.append(f)
        return lst
    
    @classmethod
    def try_binary_rules(cls, ld: Tree, rd: Tree) -> Tree | None:
        for rule in [fwd_app, bwd_app]:
            if f := rule.unify(Tree(ld = ld, rd = rd)):
                return f
        return None

fwd_app = Tree("""[
    mt = (1)[],
    ld = [mt = [+func,
                hd -> (1),
                val = [sla = [+fwd],
                       arg = (2)[]]]],
    rd = [mt -> (2)],
    rule = '>'
]""")

bwd_app = Tree("""[
    mt = (1)[],
    rd = [mt = [+func,
                hd -> (1),
                val = [sla = [-fwd],
                       arg = (2)[]]]],
    ld = [mt -> (2)],
    rule = '<'
]""")

tr = Tree("""[
    mt = [+func,
          hd = (1)[],
          val = [sla = [mod = (2)[]],
                 arg = [+func,
                        hd -> (1),
                        val = [sla = [mod -> (2)],
                               arg = (3)[-func, +tr]]]]],
    d = [mt -> (3)]
]""")

fwd_tr = tr.unify(Tree("""[
    mt = [val = [sla = [+fwd],
                 arg = [val = [sla = [-fwd]]]]],
    rule = '>T'
]"""))

bwd_tr = tr.unify(Tree("""[
    mt = [val = [sla = [-fwd],
                 arg = [val = [sla = [+fwd]]]]],
    rule = '<T'
]"""))

div = Tree("""[
    mt = [+func,
          hd = [+func,
                hd = (1)[],
                val = (4)[]],
          val = [sla = (2)[],
                 arg = [+func,
                        hd = (3)[],
                        val -> (4)]]],
    d = [mt = [+func,
               hd -> (1),
               val = [sla -> (2),
                      arg -> (3)]]]
]""")

h_div = div.unify(Tree("""[
    mt = [hd = [val = [sla = [fwd = ?x,
                              mod = [+hdiv]]]],
          val = [sla = [fwd = ?x,
                        mod = [+hdiv]]]],
    rule = 'B'
]"""))

fwd_x_div = div.unify(Tree("""[
    mt = [hd = [val = [sla = [+fwd, +xdiv]]],
          val = [sla = [-fwd, +xdiv]]],
    rule = 'Bx/'
]"""))

bwd_x_div = div.unify(Tree("""[
    mt = [hd = [val = [sla = [-fwd, +xdiv]]],
          val = [sla = [+fwd, +xdiv]]],
    rule = 'Bx\\\\'
]"""))