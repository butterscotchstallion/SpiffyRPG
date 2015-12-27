# -*- coding: utf-8 -*-
import sqlite3 as lite
import os


class Database:

    """
    Handles db connection
    """

    def __init__(self, **kwargs):
        self.connection = None
        path = None

        if "path" in kwargs:
            path = kwargs["path"]
        else:
            try:
                path = os.environ.get("SPIFFYDB_PATH")
            except KeyError:
                pass

        self.path = path

    def _open_connection(self):
        path = self.path

        exists = os.path.exists(path)
        is_readable = os.access(path, os.R_OK)

        if not exists:
            raise RuntimeError("Unable to open DB file: %s" % path)

        if not is_readable:
            raise RuntimeError("Unable to read DB file: %s" % path)

        if self.connection is None:
            self.connection = lite.connect(path)
            self.connection.row_factory = lite.Row

    def get_connection(self):
        self._open_connection()

        return self.connection
