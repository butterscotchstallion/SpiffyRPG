#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from SpiffyWorld import Database
from SpiffyWorld.models import Dungeon, Effect, ItemEffects, Item, \
    UnitItems, Unit


class TestBuildWorld(unittest.TestCase):

    """
    Functional tests for building the world
    """
    @classmethod
    def setUpClass(cls):
        cls._db = Database()
        cls.db = cls._db.get_connection()

    def test_build_world(self):
        """
        Utilize models to build the world.

        1. Get dungeons
        2. Get effects
        3. Get item effects
        4. Get items
        5. Get unit items
        6. Get units
        """

        """ Dungeons """
        dungeon_model = Dungeon(db=self.db)
        dungeons = dungeon_model.get_dungeons()

        self.assertIsInstance(dungeons, list)
        self.assertTrue(dungeons)

        """ Effects """
        effects_model = Effect(db=self.db)
        effects = effects_model.get_effects()

        self.assertIsInstance(effects, list)
        self.assertTrue(effects)

        """ Item effects map """
        item_effects_model = ItemEffects(db=self.db)
        item_effects_map = item_effects_model.get_item_effects()

        self.assertIsInstance(item_effects_map, dict)
        self.assertTrue(item_effects_map)

        """ Items """
        item_model = Item(db=self.db)
        items = item_model.get_items()

        self.assertIsInstance(items, list)
        self.assertTrue(items)

        """ Unit items map """
        unit_items_model = UnitItems(db=self.db)
        unit_items_map = unit_items_model.get_unit_items()

        self.assertIsInstance(unit_items_map, dict)
        self.assertTrue(unit_items_map)

        """ Units """
        unit_model = Unit(db=self.db)
        units = unit_model.get_units()

        self.assertIsInstance(units, list)
        self.assertTrue(units)


if __name__ == '__main__':
    unittest.main()
