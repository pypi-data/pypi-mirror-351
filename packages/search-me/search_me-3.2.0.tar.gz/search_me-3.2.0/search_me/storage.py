# -*- coding: utf-8 -*-
import logging
from base64 import urlsafe_b64encode
from contextlib import contextmanager
from io import BytesIO
from os import path, urandom

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pandas import read_json

logger = logging.getLogger(__name__)


class SafeStorage:
    """Safe storage for engines, etc data
    """

    ORIENT = "records"
    COMP = "gzip"

    @staticmethod
    def save_salt(file_path, size=1024):
        """Save salt to file

        Parameters
        ----------
        file_path : str
            Salt file
        size : int, optional
            Salt size, by default 1024

        Returns
        -------
        bytes
            Salt
        """
        salt = urandom(size)
        with open(file_path, "wb") as f:
            f.write(salt)
        return salt

    @staticmethod
    def load_salt(file_path):
        """Load salt from file

        Parameters
        ----------
        file_path : str
            Salt file

        Returns
        -------
        bytes
            Salt
        """
        with open(file_path, "rb") as f:
            salt = f.read()
        return salt

    @staticmethod
    def load_key(password, salt, algorithm=hashes.SHA256, length=32, iterations=1000000):
        """Get key

        Parameters
        ----------
        password : bytes
            Password
        salt : bytes
            Salt
        algorithm : hashes, optional
            Hash algorithm, by default hashes.SHA256
        length : int, optional
            Key length, by default 32
        iterations : int, optional
            Number iterations, by default 1000000

        Returns
        -------
        Fernet
            Key
        """
        return Fernet(
            urlsafe_b64encode(PBKDF2HMAC(
            algorithm=algorithm(), length=length, salt=salt, iterations=iterations
            ).derive(password)))

    @classmethod
    def __save(cls, filepath_salt, filepath_pass):
        """Encrypt and save data to file

        Parameters
        ----------
        filepath_salt : str
            Salt path
        filepath_pass : str
            Password path

        Yields
        ------
        None
            None
        """
        raw_pass = cls.load_salt(filepath_pass) if path.exists(filepath_pass) else cls.save_salt(filepath_pass)
        raw_salt = cls.load_salt(filepath_salt) if path.exists(filepath_salt) else cls.save_salt(filepath_salt)
        __key__ = cls.load_key(raw_pass, raw_salt)
        p1, p2 = None, None
        while True:
            df_path, df = yield p1, p2
            with BytesIO() as df_stream, open(df_path, "wb") as f:
                df.to_json(df_stream, orient=cls.ORIENT, compression=cls.COMP)
                df_stream.seek(0)
                f.write(__key__.encrypt(df_stream.read()))

    @classmethod
    def __load(cls, filepath_salt, filepath_pass):
        """Load and decrypt data from file

        Parameters
        ----------
        filepath_salt : str
            Salt path
        filepath_pass : str
            Password path

        Yields
        ------
        pandas.DataFrame
            DataFrame
        """
        __key__ = cls.load_key(cls.load_salt(filepath_pass), cls.load_salt(filepath_salt))
        f = None
        while True:
            df_path = yield f
            with open(df_path, "rb") as f_r:
                yield read_json(
                    BytesIO(__key__.decrypt(f_r.read())),
                    orient=cls.ORIENT, compression=cls.COMP
                    )

    @classmethod
    @contextmanager
    def save(cls, filepath_salt, filepath_pass):
        """Wrapper for generator

        Parameters
        ----------
        filepath_salt : str
            Salt path
        filepath_pass : str
            Password path

        Yields
        ------
        save
            File saver
        """
        saver = cls.__save(filepath_salt, filepath_pass)
        next(saver)
        try:
            yield saver
        except Exception as exc:
            logger.error(str(exc))
        finally:
            saver.close()

    @classmethod
    @contextmanager
    def load(cls, filepath_salt, filepath_pass):
        """Wrapper for generator

        Parameters
        ----------
        filepath_salt : str
            Salt path
        filepath_pass : str
            Password path

        Yields
        ------
        load
            File loader
        """
        loader = cls.__load(filepath_salt, filepath_pass)
        next(loader)
        try:
            yield loader
        except Exception as exc:
            logger.error(str(exc))
        finally:
            loader.close()
