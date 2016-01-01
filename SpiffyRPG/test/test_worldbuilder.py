#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import logging
from testfixtures import LogCapture
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
        with LogCapture():
            logger = logging.getLogger()
            worldbuilder = Worldbuilder(db=self.db,
                                        irc="quux",
                                        ircutils="quux",
                                        ircmsgs="quux",
                                        log=logger)
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
