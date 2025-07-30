<p align="center">
    <a href="https://pypi.org/project/search-me"><img src="https://gitlab.com/aioboy/search-me/-/raw/master/assets/logo.gif" alt="SEARCH-ME"></a>
</p>
<p align="center">
    <a href="https://pypi.org/project/search-me"><img src="https://img.shields.io/pypi/v/search-me.svg?style=flat-square&logo=appveyor" alt="Version"></a>
    <a href="https://pypi.org/project/search-me"><img src="https://img.shields.io/pypi/l/search-me.svg?style=flat-square&logo=appveyor&color=blueviolet" alt="License"></a>
    <a href="https://pypi.org/project/search-me"><img src="https://img.shields.io/pypi/pyversions/search-me.svg?style=flat-square&logo=appveyor" alt="Python"></a>
    <a href="https://pypi.org/project/search-me"><img src="https://img.shields.io/pypi/status/search-me.svg?style=flat-square&logo=appveyor" alt="Status"></a>
    <a href="https://pypi.org/project/search-me"><img src="https://img.shields.io/pypi/format/search-me.svg?style=flat-square&logo=appveyor&color=yellow" alt="Format"></a>
    <a href="https://pypi.org/project/search-me"><img src="https://img.shields.io/pypi/wheel/search-me.svg?style=flat-square&logo=appveyor&color=red" alt="Wheel"></a>
    <a href="https://pypi.org/project/search-me"><img src="https://img.shields.io/gitlab/pipeline-status/aioboy%2Fsearch-me?branch=master&style=flat-square&logo=appveyor" alt="Build"></a>
    <a href="https://pypi.org/project/search-me"><img src="https://gitlab.com/aioboy/search-me/-/raw/master/assets/coverage.svg" alt="Coverage"></a>
    <a href="https://pepy.tech/project/search-me"><img src="https://static.pepy.tech/personalized-badge/search-me?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Downloads" alt="Downloads"></a>
    <br><br><br>
</p>

# SEARCH-ME

Search in Google, Bing, Brave, Mojeek, Moose, Yahoo, Searx.

## INSTALL

```bash
pip install search-me
```

## USAGE

```python
import asyncio
import itertools
import logging
import aiohttp
from search_me import Bing, Brave

logging.basicConfig(level=logging.DEBUG)

bing, brave = Bing(retry=10), Brave()


async def main():
    async with aiohttp.ClientSession() as session:
            results = await asyncio.gather(
                bing.search(session=session, q="python 3.13"),
                brave.search(session=session, q="python 3.13")
                )
            for result in itertools.chain(*results):
                print(result.to_dict())


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```
