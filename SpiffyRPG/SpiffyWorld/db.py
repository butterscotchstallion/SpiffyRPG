# -*- coding: utf-8 -*-
import sqlite3 as lite
import os


class Database:

    """
    Handles db connection
    """

    def __init__(self, **kwargs):
        self.connection = None

        if "path" in kwargs:
            self.path = kwargs["path"]
        else:
            path = None

            try:
                path = os.environ.get("SPIFFYDB_PATH")
            except KeyError:
                pass

            if path is None:
                raise RuntimeError("Enviroment variable \
                    SPIFFYDB_PATH not found!")

            self.path = path

        assert self.path is not None
        assert isinstance(self.path, str) and self.path

    def _open_connection(self):
        assert self.path is not None

        exists = os.path.exists(self.path)
        is_readable = os.access(self.path, os.R_OK)

        if not exists:
            raise RuntimeError("Unable to open DB file: %s" % self.path)

        if not is_readable:
            raise RuntimeError("Unable to read DB file: %s" % self.path)

        connection = lite.connect(self.path, check_same_thread=False)
        connection.row_factory = lite.Row

        return connection

    def get_connection(self):
        if self.connection is None:
            self.connection = self._open_connection()

        return self.connection
