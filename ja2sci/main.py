from typing import Dict
from pathlib import Path
import pickle

dictionary_path = './dictionary/ja2sci.pkl'

here = Path(__file__).parent
with (here / dictionary_path).open('rb') as f:
    dictionary: Dict = pickle.load(f)


def translate(name):
    """Translate Japanese name into scientific name"""
    return dictionary[name]


if __name__ == '__main__':
    from sys import argv
    print(translate(argv[1]))
