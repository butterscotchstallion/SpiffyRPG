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

        try:
            path = os.environ.get("SPIFFYDB_PATH")
        except KeyError:
            pass

        if path is None:
            raise RuntimeError("Enviroment variable SPIFFYDB_PATH not found!")

        is_file = os.path.isfile(path)
        is_readable = os.access(path, os.R_OK)

        if not is_file or not is_readable:
            raise RuntimeError("Unable to read DB file: %s" % path)

        self.connection = lite.connect(path)
        self.connection.row_factory = lite.Row

    def get_connection(self):
        return self.connection
