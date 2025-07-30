# -*- coding: utf-8 -*-

__all__ = (
    "SearchEngineRequestError", "SearchEngineAccessError",
    "SearchEngineFormatError", "SearchEngineParamsError"
    )


class SearchEngineException(Exception):
    """Search Engine Exception
    """


class SearchEngineRequestError(SearchEngineException):
    """Search Engine Request Error
    """
    def __init__(self, *args):
        """Unpack args and call parent method
        """
        super().__init__(*args)
        self.domain = args[0]
        self.status_code = args[1]

    def __str__(self):
        """Str method

        Returns
        -------
        str
            String representation
        """
        return f"Bad request: {self.domain}. Status code: {self.status_code}"


class SearchEngineAccessError(Exception):
    """Search Engine Access Error
    """

    def __str__(self):
        """Str method

        Returns
        -------
        str
            String representation
        """
        return "No access to attr"


class SearchEngineFormatError(Exception):
    """Search Engine Format Error
    """
    def __init__(self, *args):
        """Unpack args and call parent method
        """
        super().__init__(*args)
        self.format = args[0]

    def __str__(self):
        """Str method

        Returns
        -------
        str
            String representation
        """
        return f"Can't handle format {self.format}"


class SearchEngineParamsError(Exception):
    """Search Engine Params Error
    """
    def __init__(self, *args):
        """Unpack args and call parent method
        """
        super().__init__(*args)
        self.params = args[0]

    def __str__(self):
        """Str method

        Returns
        -------
        str
            String representation
        """
        return f"Set up params {self.params}"


class ApiError(Exception):
    """Api Error
    """

    def __str__(self):
        """Str method

        Returns
        -------
        str
            String representation
        """
        return "Provide valid API key"
