# -*- coding: utf-8 -*-
import sqlite3

import logging

log = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)

class Database:
    """
    Handles db connection
    """
    def __init__(self, **kwargs):
        path = kwargs["path"]
        
        try:
            self.db = sqlite3.connect(path)
            self.db.row_factory = sqlite3.Row
        except:
            log.error("SpiffyRPG: error connecting to db")

    def get_handle(self):
        return self.db

