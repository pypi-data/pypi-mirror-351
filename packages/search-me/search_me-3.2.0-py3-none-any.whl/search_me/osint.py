# -*- coding: utf-8 -*-
import asyncio
import logging
import time
from functools import cached_property

import jmespath
from numpy import where

from search_me.storage import SafeStorage as Storage
from search_me.tools import get_current_dir, validate_api_key

__all__ = ( )

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class DocMixin:
    """Doc mixin
    """

    def doc(self):
        """Get doc

        Returns
        -------
        str
            Doc
        """
        return self.df_doc.to_markdown(tablefmt="grid", index=False)


class OSINT:
    """OSINT
    """

    __slots__ = ("df_main", "df_swap", "df_doc")

    def __init__(self, api_key):
        """Init

        Parameters
        ----------
        api_key : tuple
            API KEY
        """
        self.load(api_key)

    def __repr__(self):
        """Repr

        Returns
        -------
        str
            Repr
        """
        df = self.df_main
        return (
            df
            .iloc[where(df.name.values == self.name)]
            .to_markdown(tablefmt="grid", index=False)
        )

    @cached_property
    def name(self):
        """Name

        Returns
        -------
        str
            Name
        """
        return self.__class__.__name__.lower()

    @cached_property
    def data_main(self):
        """Data main

        Returns
        -------
        list
            Data main
        """
        df = self.df_main
        return df.iloc[where(df.name.values == self.name)].to_dict("records")

    @cached_property
    def data_swap(self):
        """Data swap

        Returns
        -------
        list
            Data swap
        """
        df = self.df_swap
        return df.iloc[where(df.name.values == self.name)].swap.tolist()

    @validate_api_key
    def load(self, api_key):
        """Load data

        Parameters
        ----------
        api_key : tuple
            API KEY
        """
        workdir = get_current_dir() / ".osint"
        fp_s, fp_p = api_key
        with Storage.load(fp_s, fp_p) as loader:
            self.df_main = loader.send(workdir / ".main")
            next(loader)
            self.df_swap = loader.send(workdir / ".swap")
            next(loader)
            if DocMixin in self.__class__.__bases__:
                self.df_doc = loader.send(workdir / f".{self.name}")
                next(loader)

    def __swap_values(self, **kwargs):
        """Swap values

        Returns
        -------
        dict
            Swapped values
        """
        swp = self.data_swap
        if swp:
            swp = swp[0]
            for k1, k_arr in swp.items():
                for k2 in k_arr:
                    kwargs[k2] = kwargs[k1]
        return kwargs

    async def search(self, session, **kwargs):
        """Osint search

        Parameters
        ----------
        session : aiohttp.ClientSession
            Session

        Returns
        -------
        generator
            Results
        """
        xl_names = {"gov", "brand", "code", "rutube"}
        call_f = self.__call_xl if self.name in xl_names else self.__call
        return (
            await self.__call_batch(
                session,
                call_f,
                **self.__swap_values(**kwargs)
                )
            )

    async def __call(self, session, d, **kwargs):
        """Http request

        Parameters
        ----------
        session : aiohttp.ClientSession
            Session
        d : dict
            Data

        Returns
        -------
        Any
            Response content
        """
        uri = d["uri"].format(**kwargs)
        kw = {}
        params = d.get("params", None)
        default_headers = d.get("default_headers", None)
        if params:
            params = {k: kwargs[k] for k in kwargs if k in params.split(",")}
            default_params = d.get("default_params", None)
            if default_params:
                params = {**default_params, **params}
            kw[d["in_format"]] = params
        if default_headers:
            kw["headers"] = default_headers
        logger.debug(f"{uri, d, kw}")
        async with session.request(d["method"], uri, **kw) as resp:
            logger.info(f"{uri, resp.status}")
            if d["out_format"] == "json":
                content_type = d.get("out_content_type", None)
                if content_type:
                    content = await resp.json(content_type=content_type)
                else:
                    content = await resp.json()
                out_xpath = d.get("out_xpath", None)
                if out_xpath:
                    return jmespath.compile(out_xpath).search(content)
                else:
                    return content
            return uri, resp.status

    async def __call_xl(self, session, d, **kwargs):
        """Recursive http request

        Parameters
        ----------
        session : aiohttp.ClientSession
            Session
        d : dict
            Data

        Returns
        -------
        Any
            Response content
        """
        nested_results = []
        uri = d["uri"].format(**kwargs)
        kw = {}
        params = d.get("params", None)
        default_headers = d.get("default_headers", None)
        if params:
            params = {k: kwargs[k] for k in kwargs if k in params.split(",")}
            default_params = d.get("default_params", None)
            if default_params:
                params = {**default_params, **params}
            kw[d["in_format"]] = params
        if default_headers:
            kw["headers"] = default_headers
        logger.debug(f"{uri, d, kw}")
        async with session.request(d["method"], uri, **kw) as resp:
            logger.info(f"{uri, resp.status}")
            out_format = d.get("out_format", None)
            if out_format == "json":
                content_type = d.get("out_content_type", None)
                if content_type:
                    content = await resp.json(content_type=content_type)
                else:
                    content = await resp.json()
                out_xpath = d.get("out_xpath", None)
                if out_xpath:
                    content = jmespath.search(out_xpath, content)
            elif out_format == "file":
                fp = resp.headers["Content-Disposition"].split(";")[-1].split("=")[-1]
                with open(fp, "wb") as f:
                    async for chunk in resp.content.iter_chunked(2 ** 10):
                        f.write(chunk)
                content = fp
            else:
                content = None
            delay = d.get("delay", 0)
            time.sleep(delay)
            nested_context = d.get("nested", None)
            if nested_context:
                trace_key = d.get("trace_key", "")
                batch = d.get("batch", False)
                if batch:
                    for c in content:
                        r = await self.__call_xl(
                            session, nested_context, **{**nested_context, **{trace_key: c}}
                            )
                        nested_results.append(r)
                    return nested_results
                else:
                    trace_data = kwargs.get(trace_key, None)
                    if trace_data:
                        nested_context[trace_key] = trace_data
                    return await self.__call_xl(
                        session, nested_context, **{**content, **nested_context}
                        )
            else:
                return content

    async def __call_batch(self, session, call_f, **kwargs):
        """Batch http requests

        Parameters
        ----------
        session : aiohttp.ClientSession
            Session
        call_f : function
            Http request function

        Returns
        -------
        generator
            Results
        """
        return (
            r for r in (
                await asyncio.gather(
                    *(call_f(session, d, **kwargs) for d in self.data_main),
                    return_exceptions=True
                    )
                )
            )


class Domain(OSINT):
    """OSINT. Domain
    """


class Ip(OSINT):
    """OSINT. Ip
    """


class Url(OSINT):
    """OSINT. Url
    """


class Email(OSINT):
    """OSINT. Email
    """


class Zipcode(OSINT):
    """OSINT. Zipcode
    """


class Geo(OSINT):
    """OSINT. Geo
    """


class GeoRoute(OSINT):
    """OSINT. GeoRoute
    """


class WebCam(OSINT):
    """OSINT. WebCam
    """


class WebCamGeo(OSINT):
    """OSINT. WebCamGeo
    """


class Gov(OSINT, DocMixin):
    """OSINT. Gov
    """


class Academic(OSINT):
    """OSINT. Academic
    """


class Text(OSINT):
    """OSINT. Text
    """


class Dataset(OSINT):
    """OSINT. Dataset
    """


class News(OSINT):
    """OSINT. News
    """


class Btc(OSINT):
    """OSINT. Btc
    """


class Username(OSINT):
    """OSINT. Username
    """


class Telegram(OSINT):
    """OSINT. Telegram
    """


class Github(OSINT):
    """OSINT. Github
    """


class Vk(OSINT):
    """OSINT. Vk
    """


class Associations(OSINT):
    """OSINT. Associations
    """


class Suggestions(OSINT):
    """OSINT. Suggestions
    """


class Code(OSINT, DocMixin):
    """OSINT. Code
    """


class Brand(OSINT):
    """OSINT. Brand
    """


class Youtube(OSINT):
    """OSINT. Youtube
    """


class Rutube(OSINT):
    """OSINT. Rutube
    """


class Work(OSINT):
    """OSINT. Work
    """
