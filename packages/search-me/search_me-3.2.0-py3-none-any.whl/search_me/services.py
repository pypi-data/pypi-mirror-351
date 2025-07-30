# -*- coding: utf-8 -*-
from random import shuffle

from search_me.balancers import RR
from search_me.storage import SafeStorage as Storage
from search_me.tools import get_current_dir, validate_api_key

__all__ = ( )


class UserAgents:
    """User agents
    """

    __slots__ = ("__data", )

    def __init__(self):
        """Init
        """
        self.load()

    def load(self):
        """Load data
        """
        workdir = get_current_dir() / ".engines"
        with Storage.load(workdir / ".salt", workdir / ".pass") as loader:
            data = loader.send(workdir / f".{self.__class__.__name__.lower()}").name.tolist()
            shuffle(data)
            self.__data = RR(*data)
            next(loader)

    def get(self):
        """Get user agent

        Returns
        -------
        str
            User agent
        """
        return next(self.__data)


class Dorks:
    """Dorks
    """

    __slots__ = ("__data", )

    def __init__(self, api_key):
        """Init

        Parameters
        ----------
        api_key : tuple
            API KEY
        """
        self.load(api_key)

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
            self.__data = loader.send(workdir / f".{self.__class__.__name__.lower()}")
            next(loader)

    def get(self, query, raw=False):
        """Get dorks

        Parameters
        ----------
        query : str
            Query
        raw : bool, optional
            Raw or not, by default False

        Returns
        -------
        pandas.DataFrame of List
            Dorks
        """
        df = self.__data.query(query)
        return df if raw else df.name.tolist()
