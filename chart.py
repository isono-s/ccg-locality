from __future__ import annotations
import itertools

from rules import Rules
from lexicon import Lexicon
from structure import Tree

class Chart:
    def __init__(self, lexicon: Lexicon, string: str) -> None:
        self.log = ''
        self.words = string.split()
        self.dist_costs = [0] * len(self.words)
        self.cells: list[list[list[self.Deriv]]] = []
        for i in range(len(self.words)):
            self.cells.append([[] for _ in range(i+1)])
        for i, word in enumerate(string.split()):
            for tree in lexicon.get_as_trees(word):
                self.add_to_cell(tree, (i, i, i), force_add=True)
    
    def add_log(self, *texts) -> None:
        for text in texts:
            self.log += text+'\n'
    
    def save_log(self, dir) -> None:
        with open(f'{dir}{"_".join(self.words)}.txt', 'w') as f:
            f.write(self.log)

    class Deriv:
        def __init__(self, tree: Tree, pos: tuple[int, int, int], back = None):
            self.tree = tree
            self.pos = pos
            self.back = back
            self.last_activation = pos[2]

    def add_to_cell(self, tree: Tree, pos: tuple[int, int, int], back = None, force_add = False) -> None:
        def complexity(tree: Tree) -> int:
            return tree.cat_to_text().count('(')
        
        i, j, k = pos[0], pos[1], pos[2]
        new_tree_cat = tree.cat_to_text()
        if len(self.cells[k][k-i]) == 0:
            self.cells[k][k-i] = [self.Deriv(tree, pos, back)]
            self.add_log(f'  added {new_tree_cat}')
        else:
            old_tree_complexity = complexity(self.cells[k][k-i][0].tree)
            new_tree_complexity = complexity(tree)
            if (force_add or
                old_tree_complexity == new_tree_complexity and
                len([old_deriv for old_deriv in self.cells[k][k-i] if tree.get_enf() == old_deriv.tree.get_enf()]) == 0):
                self.cells[k][k-i].append(self.Deriv(tree, pos, back))
                self.add_log(f'  added {new_tree_cat}')
            elif old_tree_complexity > new_tree_complexity:
                self.cells[k][k-i] = [self.Deriv(tree, pos, back)]
                self.add_log(f'  added {new_tree_cat}')

    def parse_inc(self) -> None:
        for k in range(1, len(self.cells)):
            for i in range(k-1, -1, -1):
                for j in range(k-1, i-1, -1): 
                    for left in self.cells[j][j-i]:
                        for right in self.cells[k][k-j-1]:
                            left_cat = left.tree.cat_to_text()
                            right_cat = right.tree.cat_to_text()
                            left_words = ' '.join(self.words[i:j+1])
                            right_words = ' '.join(self.words[j+1:k+1])
                            self.add_log(f'at {(i,j,k)} - {left_cat} "{left_words}" + {right_cat} "{right_words}"')
                            for r in self.try_to_combine(left.tree, right.tree):
                                self.add_to_cell(r, (i, j, k), (left, right))
            self.calc_dist_cost(k)
        self.add_log('', self.get_results())
        
    def try_to_combine(self, left: Tree, right: Tree) -> Tree | None:
        def result_of_unary(base: Tree) -> list[Tree]:
            res = [[base]]
            for _ in range(2):
                res.append([])
                for dtr in res[-2]:
                    res[-1].extend(Rules.try_unary_rules(dtr))
            return list(itertools.chain.from_iterable(res))
        
        lefts = result_of_unary(left)
        rights = result_of_unary(right)
        res = []
        for l in lefts:
            for r in rights:
                if f := Rules.try_binary_rules(l, r):
                    res.append(f)
        return res
    
    def calc_dist_cost(self, k: int) -> None:
        for i in range(k):
            if len(self.cells[k][k-i]) > 0:
                break
        if len(self.cells[k][k-i]) == 0 or i == k:
            return
        left_back = self.cells[k][k-i][0].back[0]
        dist = k - left_back.last_activation
        left_back.last_activation = k
        self.dist_costs[k] = dist

    def get_results(self) -> str:
        text = 'PARSE(S):\n'
        for deriv in self.cells[-1][-1]:
            text += deriv.tree.to_text() + '\n'
        text += '\nDISTANCE COSTS:\n'
        for i, word in enumerate(self.words):
            text += f'"{word}" {self.dist_costs[i]}\n'
        return text