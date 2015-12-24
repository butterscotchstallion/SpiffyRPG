#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from SpiffyWorld import Database


class TestBuildWorld(unittest.TestCase):

    """
    Functional tests for building the world
    """
    @classmethod
    def setUpClass(cls):
        cls._db = Database()
        cls.db = cls._db.get_connection()

if __name__ == '__main__':
    unittest.main()
