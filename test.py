from __future__ import annotations
from lexicon import Lexicon
from chart import Chart
import os

TEST_ITEMS = [('eng', 'the rat that the cat chased ran'),
              ('eng', 'the rat that the cat with a long tail chased ran'),
              ('jpn', 'nekoga nezumio oikake nak at ta'),
              ('jpn', 'nekosika nezumio oikake nak at ta')]

os.chdir(os.path.dirname(__file__))
for test_item in TEST_ITEMS:
    lex = Lexicon(f'./lex/{test_item[0]}.txt')
    c = Chart(lex, test_item[1])
    c.parse_inc()
    print(c.get_results())
    c.save_log('./log/')