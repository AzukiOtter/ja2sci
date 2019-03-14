from typing import Dict
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


def translate(name: str) -> str:
    try:
        return from_dict(name)
    except TranslationError:
        return from_wikipedia(name)


async def async_translate(name: str) -> str:
    try:
        return from_dict(name)
    except TranslationError:
        return await from_wikipedia_async(name)


def from_dict(name: str) -> str:
    """Translate Japanese name into scientific name via offline dictionary"""
    try:
        return dictionary[name]
    except KeyError:
        raise TranslationError('{} does not exist in the dictionary.')


def __interpret_wikipedia(content: dict, name: str) -> str:
    if '-1' in content['query']['pages'].keys():
        raise TranslationError('No Wikipedia page named {}.'.format(name))
    pages = content['query']['pages']
    page_content = [pages[page]['revisions'][0]['*'] for page in pages][0]

    # raise RedirectException when #REDIRECT is found
    if page_content.startswith('#REDIRECT'):
        redirect_name = re.search(r'#REDIRECT *\[\[([^\]]+)\]\]', page_content).group(1)
        raise RedirectException(redirect_name)

    for regex in wikipedia_regex:
        match = regex.search(page_content)
        if match:
            return match.group(2)

    raise TranslationError('{} exists in Wikipedia, but no scientific name found in the page.'.format(name))


def from_wikipedia(name: str) -> str:
    """Get Wikipedia page and find scientific name"""
    while True:
        titles = urllib.parse.quote(name)
        url = 'https://ja.wikipedia.org/w/api.php?format=json&action=query&prop=revisions&rvprop=content&titles={}'.format(titles)
        response = urllib.request.urlopen(url)
        content = json.loads(response.read().decode('utf8'))
        try:
            return __interpret_wikipedia(content, name)
        except RedirectException as redirect:
            name = redirect.name


async def from_wikipedia_async(name: str) -> str:
    """Get Wikipedia page and find scientific name asynchronously"""
    while True:
        titles = urllib.parse.quote(name)
        url = 'https://ja.wikipedia.org/w/api.php?format=json&action=query&prop=revisions&rvprop=content&titles={}'.format(titles)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                content = json.loads(await resp.text())
        try:
            return __interpret_wikipedia(content, name)
        except RedirectException as redirect:
            name = redirect.name


def commandline():
    import sys
    print(translate(sys.argv[1]))


class BaseTranslationError(Exception):
    pass

class TranslationError(BaseTranslationError):
    pass

class RedirectException(BaseTranslationError):
    def __init__(self, name):
        self.name = name
