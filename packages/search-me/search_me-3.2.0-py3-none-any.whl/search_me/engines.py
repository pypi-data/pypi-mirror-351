import logging
import time
from functools import cached_property
from pathlib import Path

from aiohttp.client_exceptions import ClientConnectorError
from bs4 import BeautifulSoup
from numpy import where

from search_me.balancers import DWRR, RR
from search_me.exceptions import (SearchEngineAccessError,
                                  SearchEngineFormatError,
                                  SearchEngineRequestError)
from search_me.models import SearchResult as Response
from search_me.storage import SafeStorage as Storage
from search_me.tools import check_params, get_current_dir, retry

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class SearchEngine:
    """Search Engine
    """

    domain_balancer = RR
    lang_balancer = RR

    __slots__ = (
        "default_kwargs", "default_params",
        "__domains", "__languages", "__regex", "__output_format"
        )

    def __init__(self, **default_kwargs) -> None:
        """Init
        """
        self.default_kwargs = default_kwargs
        self.load()

    def __str__(self) -> str:
        """Str

        Returns
        -------
        str
            Str
        """
        return self.name

    def __repr__(self) -> str:
        """Repr

        Returns
        -------
        str
            Repr
        """
        return f"{self.name}()"

    def df_to_list_filter_by_engine(self, df):
        """Convert datafrme column to list

        Parameters
        ----------
        df : pandas.DataFrame
            DataFrame

        Returns
        -------
        List
            List of values
        """
        return df.iloc[where(df.engine.values == self.name)].name.tolist()

    def load(self):
        """Load data from files

        Raises
        ------
        SearchEngineFormatError
            Raised if not found right format
        """
        workdir = get_current_dir() / f".{Path(__file__).name.split('.')[0]}"

        with Storage.load(workdir / ".salt", workdir / ".pass") as loader:
            df_domains = loader.send(workdir / ".domains")
            next(loader)
            df_languages = loader.send(workdir / ".languages")
            next(loader)
            df_regex= loader.send(workdir / ".regex")
            next(loader)
            df_formats = loader.send(workdir / ".formats")
            next(loader)
            df_params = loader.send(workdir / ".params")
            next(loader)

        domains, languages, regex, output_format, default_params = (
            self.df_to_list_filter_by_engine(df_domains),
            self.df_to_list_filter_by_engine(df_languages),
            self.df_to_list_filter_by_engine(df_regex),
            self.df_to_list_filter_by_engine(df_formats),
            self.df_to_list_filter_by_engine(df_params)
        )

        if domains:
            self.__domains = self.domain_balancer(*domains)
        if languages:
            self.__languages = self.lang_balancer(*languages)
        if regex:
            self.__regex = regex[0].split(",")
        if output_format:
            self.__output_format = output_format[0]
            if self.__output_format not in {*df_formats.name.tolist()}:
                raise SearchEngineFormatError(self.__output_format)
        if default_params:
            self.default_params = default_params[0]
        else:
            self.default_params = {}

    @property
    def name(self):
        """Name

        Returns
        -------
        str
            Name
        """
        return self.__class__.__name__

    @name.setter
    def name(self, value):
        """Name

        Raises
        ------
        SearchEngineAccessError
            Raised when access descriptor
        """
        raise SearchEngineAccessError()

    @name.deleter
    def name(self):
        """Name

        Raises
        ------
        SearchEngineAccessError
            Raised when access descriptor
        """
        raise SearchEngineAccessError()

    @property
    def domains(self):
        """Domains

        Returns
        -------
        generator
            Domains
        """
        return self.__domains

    @domains.setter
    def domains(self, value):
        """Domains

        Raises
        ------
        SearchEngineAccessError
            Raised when access descriptor
        """
        raise SearchEngineAccessError()

    @domains.deleter
    def domains(self):
        """Domains

        Raises
        ------
        SearchEngineAccessError
            Raised when access descriptor
        """
        raise SearchEngineAccessError()

    @property
    def languages(self):
        """Languages

        Returns
        -------
        generator
            Languages
        """
        try:
            return self.__languages
        except AttributeError:
            return

    @languages.setter
    def languages(self, value):
        """Languages

        Raises
        ------
        SearchEngineAccessError
            Raised when access descriptor
        """
        raise SearchEngineAccessError()

    @languages.deleter
    def languages(self):
        """Languages

        Raises
        ------
        SearchEngineAccessError
            Raised when access descriptor
        """
        raise SearchEngineAccessError()

    @property
    def regex(self):
        """Regex

        Returns
        -------
        tuple
            Regex
        """
        return self.__regex

    @regex.setter
    def regex(self, value):
        """Regex

        Raises
        ------
        SearchEngineAccessError
            Raised when access descriptor
        """
        raise SearchEngineAccessError()

    @regex.deleter
    def regex(self):
        """Regex

        Raises
        ------
        SearchEngineAccessError
            Raised when access descriptor
        """
        raise SearchEngineAccessError()

    @property
    def output_format(self):
        """Output format

        Returns
        -------
        str
            Output format
        """
        return self.__output_format

    @output_format.setter
    def output_format(self, value):
        """Output format

        Raises
        ------
        SearchEngineAccessError
            Raised when access descriptor
        """
        raise SearchEngineAccessError()

    @output_format.deleter
    def output_format(self):
        """Output format

        Raises
        ------
        SearchEngineAccessError
            Raised when access descriptor
        """
        raise SearchEngineAccessError()

    @cached_property
    def is_html(self):
        """Check is output format - html

        Returns
        -------
        bool
            Check is output format - html
        """
        return self.output_format == "html"

    def parse_page(self, raw_data, q):
        """Parse JSON of HTML data

        Parameters
        ----------
        raw_data : any
            Raw data
        q : str
            Search term

        Returns
        -------
        generator
            Parsed data
        """
        return self.parse_page_html(
            raw_data, q
            ) if self.is_html else self.parse_page_json(raw_data, q)

    def parse_page_html(self, html_content, q):
        """Parse HTML

        Parameters
        ----------
        html_content : str
            HTML
        q : str
            Search term

        Yields
        ------
        tuple
            Parsed data
        """
        block_xpath, uri_xpath, title_xpath = self.regex
        is_a_uri_xpath = uri_xpath == "a"
        blocks = BeautifulSoup(html_content, "html.parser").select(block_xpath)
        rating = 0
        for block in blocks:
            uri = block.find(uri_xpath, href=True) if is_a_uri_xpath else block.find(uri_xpath)
            title = block.find(title_xpath) if title_xpath else uri
            if uri and title:
                url = uri["href"] if is_a_uri_xpath else uri.text
                yield q, rating + 1, url, title.text.strip(), self.name
                rating += 1

    def parse_page_json(self, json_content, q):
        """Parse JSON

        Parameters
        ----------
        json_content : Dict
            JSON
        q : str
            Search term

        Yields
        ------
        tuple
            Parsed data
        """
        json_path_1, json_path_2, *_ = self.regex
        json_results = json_content[json_path_1]
        if json_path_2:
            json_results = json_results[json_path_2]
        rating = 0
        for values in json_results:
            sources = values.get("sources", None)
            source = ",".join(sources) if sources else self.name
            yield q, rating + 1, values["url"], values["title"].strip(), source
            rating += 1

    @retry((ClientConnectorError, SearchEngineRequestError))
    async def fetch_page(self, session, **params):
        """Fetch web url

        Parameters
        ----------
        session : aiohttp.ClientSession
            Session

        Returns
        -------
        any
            HTML or JSON content

        Raises
        ------
        SearchEngineRequestError
            If bad request
        """
        domain = next(self.domains)
        if self.languages is not None:
            key = "hl" if self.name == "Google" else "language"
            params[key] = next(self.languages)
        async with session.get(domain, params=params) as resp:
            status_code = resp.status
            logger.debug(f"Called {domain}. Status code: {status_code}")
            if status_code == 200:
                if self.is_html:
                    content = await resp.text()
                else:
                    content = await resp.json()
                self.recalc_domain_weights(domain, 1)
                return content
            self.recalc_domain_weights(domain, -1)
            time.sleep(self.default_kwargs.get("delay", 0))
            raise SearchEngineRequestError(domain, status_code)

    def recalc_domain_weights(self, domain, w):
        """Recalc weights for item

        Parameters
        ----------
        domain : str
            Domain
        w : int
            Weight
        """
        balancer = self.domains
        if isinstance(balancer, DWRR):
            balancer.recalc_weights(domain, w)

    @check_params("q")
    async def search(self, session, return_raw=False, **params):
        """Search

        Parameters
        ----------
        session : aiohttp.ClientSession
            Session
        return_raw : bool, optional
            Raw data or not, by default False

        Returns
        -------
        generator
            Search results
        """
        params = {**self.default_params, **params}
        q = params["q"]
        if self.name == "Etools":
            params["query"] = params["q"]
            del params["q"]
        logger.debug(f"Processing q: {q}")
        raw_data = await self.fetch_page(session, **params)
        parsed_data = self.parse_page(raw_data, q) if raw_data else ( )
        return parsed_data if return_raw else map(lambda x: Response(*x), parsed_data)


class Google(SearchEngine):
    """Google search engine
    """
    domain_balancer = DWRR


class Bing(SearchEngine):
    """Bing search engine
    """


class Brave(SearchEngine):
    """Brave search engine
    """


class Mojeek(SearchEngine):
    """Mojeek search engine
    """


class Moose(SearchEngine):
    """Moose search engine
    """


class Yahoo(SearchEngine):
    """Yahoo search engine
    """


class Searx(SearchEngine):
    """Searx search engine
    """
    domain_balancer = DWRR


class Etools(SearchEngine):
    """Etools search engine
    """
