# -*- coding: utf-8 -*-
from abc import abstractmethod
from collections import defaultdict
from functools import reduce
from itertools import cycle
from math import gcd as mgcd

from search_me.tools import count_calls

__all__ = ("RR", "DWRR")


class AR:
    """Abstract class describes protocol of balance strategies
    """

    def __init__(self):
        """Init
        """
        self.calls = defaultdict(int)

    def __iter__(self):
        """Iterator must-have method

        Returns
        -------
        Iterator
            Iterator
        """
        return next(self)

    @abstractmethod
    def __next__(self):
        """Iterator must-have method

        Raises
        ------
        NotImplementedError
            Should be implemented in nested class
        """
        raise NotImplementedError()


class RR(AR):
    """Round Robin

    Parameters
    ----------
    AR : class
        Abstract Robin
    """

    def __init__(self, *data):
        """Init
        """
        super().__init__()
        self.__cycle = cycle(data)

    @count_calls
    def __next__(self):
        """Get next item

        Returns
        -------
        Any
            Next item
        """
        item = next(self.__cycle)
        return item


class WRR(AR):
    """Weighted Round Robin

    Parameters
    ----------
    AR : class
        Abstract Robin
    """

    def __init__(self, *data):
        """Init
        """
        super().__init__()
        self.weights = list(data)
        self.size = len(data)
        self.max_w = max(data, key=lambda x: x[1])[1]
        self.gcd = reduce(mgcd, (w for _, w in data))
        self.cur_idx = -1
        self.cur_w = 0

    @count_calls
    def __next__(self):
        """Get next item

        Returns
        -------
        Any
            Next item
        """
        while True:
            self.cur_idx = (self.cur_idx + 1) % self.size
            if self.cur_idx == 0:
                self.cur_w = self.cur_w - self.gcd
                if self.cur_w <= 0:
                    self.cur_w = self.max_w
                    if self.cur_w == 0:
                        return
            item, w = self.weights[self.cur_idx]
            if w >= self.cur_w:
                return item


class DWRR(AR):
    """Dynamic Weighted Round Robin

    Parameters
    ----------
    AR : class
        Abstract Robin
    """

    def __init__(self, *data):
        """Init
        """
        super().__init__()
        self.weights = {d: 1000 for d in data}
        self.size = len(data)
        self.cur_idx = -1
        self.cur_w = 0

    @count_calls
    def __next__(self):
        """Get next item

        Returns
        -------
        Any
            Next item
        """
        while True:
            self.cur_idx = (self.cur_idx + 1) % self.size
            if self.cur_idx == 0:
                self.cur_w = self.cur_w - self.gcd
                if self.cur_w <= 0:
                    self.cur_w = self.max_w
                    if self.cur_w == 0:
                        return
            item, w = self.data_w[self.cur_idx]
            if w >= self.cur_w:
                return item

    def recalc_weights(self, item, w_value):
        """Recalc weights for item

        Parameters
        ----------
        item : str
            item name
        w_value : int
            Weight
        """
        self.weights[item] += w_value

    @property
    def data_w(self):
        """Data weights

        Returns
        -------
        List
            List of data tuples
        """
        return list(self.weights.items())

    @property
    def max_w(self):
        """Get max weight

        Returns
        -------
        int
            Max weight
        """
        return max(self.data_w, key=lambda x: x[1])[1]

    @property
    def gcd(self):
        """Reduced gcd

        Returns
        -------
        int
            GCD
        """
        return reduce(mgcd, (w for _, w in self.data_w))
