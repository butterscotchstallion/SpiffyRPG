#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from SpiffyWorld.models import Dungeon
from SpiffyWorld import Database


class TestDungeon(unittest.TestCase):

    """
    Functional tests for unit model
    """
    @classmethod
    def setUpClass(cls):
        cls._db = Database()
        cls.db = cls._db.get_connection()

    def test_get_dungeons(self):
        dungeon_model = Dungeon(db=self.db)
        dungeons = dungeon_model.get_dungeons()

        self.assertIsInstance(dungeons, list)
        self.assertTrue(len(dungeons) > 0)

        for dungeon in dungeons:
            self.assertIsInstance(dungeon, dict)
            self.assertTrue(dungeon["id"])
            self.assertTrue(dungeon["name"])
            self.assertTrue(dungeon["channel"])
            self.assertTrue("description" in dungeon)
            self.assertTrue("min_level" in dungeon)
            self.assertTrue("max_level" in dungeon)

if __name__ == '__main__':
    unittest.main()
