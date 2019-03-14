from typing import Dict, Union
from pathlib import Path
import pickle
import urllib.request
import urllib.parse
import json
import re
import aiohttp

dictionary_path = './dictionary/ja2sci.pkl'

here = Path(__file__).parent
with (here / dictionary_path).open('rb') as f:
    dictionary: Dict = pickle.load(f)

wikipedia_regex = [
    re.compile(r"学名 ?= ?('+)([^']+)\1"),
    re.compile(r"学名 ?= ?('*)\{\{Snamei\|([^}]+)\}\}\1"),
    re.compile(r"学名 ?= ?('*)\{\{sname[^}]*\|([^}|]+)\}\}\1"),
]


def translate(name: str, debug: bool =False) -> str:
    return from_dict(name) or from_wikipedia(name, debug) or None


async def async_translate(name: str, debug: bool =False) -> str:
    return from_dict(name) or await from_wikipedia_async(name, debug) or None


def from_dict(name: str) -> str:
    """Translate Japanese name into scientific name via offline dictionary"""
    return dictionary.get(name)


def __interpret_wikipedia(content: dict, name: str, debug: bool =False) -> Union[str, None]:
    if '-1' in content['query']['pages'].keys():
        if debug:
            print('No Wikipedia page named {}.'.format(name))
        return None
    pages = content['query']['pages']
    page_content = [pages[page]['revisions'][0]['*'] for page in pages][0]

    if debug:
        print(f'============== PAGE CONTENT OF {name} ==============')
        print(page_content)
        print(f'====================================================')

    # raise RedirectException when #REDIRECT is found
    if page_content.startswith('#REDIRECT'):
        redirect_name = re.search(r'#REDIRECT *\[\[([^\]]+)\]\]', page_content).group(1)
        if debug:
            print(f'REDIRECTING: {name} -> {redirect_name}')
        raise RedirectException(redirect_name)

    for regex in wikipedia_regex:
        match = regex.search(page_content)
        if match:
            return match.group(2)

    if debug:
        print('{} exists in Wikipedia, but no scientific name found in the page.'.format(name))
    return None


def from_wikipedia(name: str, debug: bool =False) -> Union[str, None]:
    """Get Wikipedia page and find scientific name"""
    while True:
        titles = urllib.parse.quote(name)
        url = 'https://ja.wikipedia.org/w/api.php?format=json&action=query&prop=revisions&rvprop=content&titles={}'.format(titles)
        response = urllib.request.urlopen(url)
        content = json.loads(response.read().decode('utf8'))
        try:
            return __interpret_wikipedia(content, name, debug)
        except RedirectException as redirect:
            name = redirect.name


async def from_wikipedia_async(name: str, debug: bool =False) -> Union[str, None]:
    """Get Wikipedia page and find scientific name asynchronously"""
    while True:
        titles = urllib.parse.quote(name)
        url = 'https://ja.wikipedia.org/w/api.php?format=json&action=query&prop=revisions&rvprop=content&titles={}'.format(titles)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                content = json.loads(await resp.text())
        try:
            return __interpret_wikipedia(content, name, debug)
        except RedirectException as redirect:
            name = redirect.name


def commandline():
    import sys
    print(translate(sys.argv[1]))


class BaseTranslationError(Exception):
    pass

class RedirectException(BaseTranslationError):
    def __init__(self, name):
        self.name = name
