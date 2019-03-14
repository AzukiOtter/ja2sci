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
    re.compile(r"学名 ?= ?('*){{Snamei\|([^}]+)}}\1"),
    re.compile(r"学名 ?= ?('*){{sname[^}]*\|([^}|]+)}}\1"),
]


def translate(name: str, debug: bool =False) -> str:
    return from_dict(name) or from_wikipedia(name, debug) or None


async def async_translate(name: str, debug: bool =False) -> str:
    return from_dict(name) or await from_wikipedia_async(name, debug) or None


def from_dict(name: str) -> str:
    """Translate Japanese name into scientific name via offline dictionary"""
    return dictionary.get(name)


def __interpret_wikipedia(content: dict, name: str, debug: bool =False) -> Union[str, None]:
    if '-1' in content['query']['pages']:
        if debug:
            print('No Wikipedia page named {}.'.format(name))
        return None

    # Gets the first page from pages
    page = next(i for i in content['query']['pages'].values())
    page_content = page['revisions'][0]['*']

    if debug:
        if "redirects" in content['query']:
            for redirect in content['query']['redirects']:
                print(f"REDIRECTED: {redirect['from']} -> {redirect['to']}")
        print(f'============== PAGE CONTENT OF {page["title"]} ==============')
        print(page_content)
        print(f'====================================================')

    for regex in wikipedia_regex:
        match = regex.search(page_content)
        if match:
            return match.group(2)

    if debug:
        print('{} exists in Wikipedia, but no scientific name found in the page.'.format(name))
    return None


def from_wikipedia(name: str, debug: bool =False) -> Union[str, None]:
    """Get Wikipedia page and find scientific name"""
    titles = urllib.parse.quote(name)
    url = 'https://ja.wikipedia.org/w/api.php?format=json&action=query&prop=revisions&rvprop=content&redirects&titles={}'.format(titles)
    response = urllib.request.urlopen(url)
    content = json.loads(response.read().decode('utf8'))
    return __interpret_wikipedia(content, name, debug)


async def from_wikipedia_async(name: str, debug: bool =False) -> Union[str, None]:
    """Get Wikipedia page and find scientific name asynchronously"""
    titles = urllib.parse.quote(name)
    url = 'https://ja.wikipedia.org/w/api.php?format=json&action=query&prop=revisions&rvprop=content&redirects&titles={}'.format(titles)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            content = json.loads(await resp.text())
            return __interpret_wikipedia(content, name, debug)


def commandline():
    import sys
    print(translate(sys.argv[1]))


class BaseTranslationError(Exception):
    pass
