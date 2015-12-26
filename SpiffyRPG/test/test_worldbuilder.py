#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from SpiffyWorld import Worldbuilder, Database, World


class TestWorldbuilder(unittest.TestCase):

    """
    Functional tests for Worldbuilder
    """
    @classmethod
    def setUpClass(cls):
        cls._db = Database()
        cls.db = cls._db.get_connection()

    def test_build_world(self):
        worldbuilder = Worldbuilder(db=self.db, irc="quux")
        world = worldbuilder.build_world()

        self.assertIsInstance(world, World)
        self.assertTrue(world.dungeon_collection)
        self.assertTrue(world.dungeon_collection.dungeons)

        for dungeon in world.dungeon_collection.dungeons:
            self.assertTrue(dungeon.name)
            self.assertTrue(dungeon.units)

        self.assertTrue(world.unit_collection)
        self.assertTrue(world.effect_collection)
        self.assertTrue(world.dialogue_collection)
        self.assertTrue(world.item_collection)


if __name__ == '__main__':
    unittest.main()
