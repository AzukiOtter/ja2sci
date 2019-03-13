# ja2sci
ja2sci converts Japanese name into scientific name.
If the given name is not on the internal dictionary, it automatically searches the wikipedia.

生物の和名を学名に変換するライブラリです。
内部辞書に学名が登録されていない場合、自動的に Wikipedia から学名を取得します。


## How to use
### As a CLI tool
```sh
$ pip install ja2sci
$ ja2sci ニホンカワウソ
Lutra lutra nippon
```

### Inside python script
```python
>>> import ja2sci
>>> ja2sci.translate('ユーラシアカワウソ')
'Lutra lutra'
```

### Advanced usage: asynchronous translation
```python
>>> import ja2sci
>>> import asyncio
>>> loop = asyncio.get_event_loop()
>>> results = loop.run_until_complete(asyncio.gather(
...     ja2sci.async_translate('ホンドテン'), # Not on internal dictionary
...     ja2sci.async_translate('ミンク')      # Not on internal dictionary
... ))
>>> print(results)
['Martes melampus melampus', 'Neovison vison']
```
