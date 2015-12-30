# -*- coding: utf-8 -*-
import sqlite3 as lite
import os


class Database:

    """
    Handles db connection
    """

    def __init__(self, **kwargs):
        self.log = None

        if "log" in kwargs:
            self.log = kwargs["log"]

        if "path" in kwargs:
            path = kwargs["path"]

            if not path or path is None:
                raise ValueError("Database: path is invalid")

            self.path = path
        else:
            try:
                self.path = os.environ.get("SPIFFYDB_PATH")
            except KeyError:
                pass

        if not isinstance(self.path, str) or not self.path:
            raise RuntimeError("Database path not found: %s" % self.path)

        connection = lite.connect(self.path, check_same_thread=False)
        connection.row_factory = lite.Row

        if self.log is not None:
            self.log.info("SpiffyWorld: initialized db path %s" % self.path)

        self.connection = connection

    def get_connection(self):
        return self.connection
