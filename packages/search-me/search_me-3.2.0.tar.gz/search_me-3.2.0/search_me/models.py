# -*- coding: utf-8 -*-
from dataclasses import asdict, dataclass


@dataclass
class SearchResult:
    """Search result model
    """
    q: str
    rating: int
    uri: str
    title: str
    source: str

    def to_dict(self):
        """Dict form of dataclass

        Returns
        -------
        Dict
            Dict
        """
        return asdict(self)
