#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from SpiffyWorld.models import Unit as UnitModel, UnitItems, UnitType, \
    Item, ItemEffects
from SpiffyWorld import Database


class TestBuildWorld(unittest.TestCase):

    """
    Functional tests for building the world
    """
    @classmethod
    def setUpClass(cls):
        cls._db = Database()
        cls.db = cls._db.get_connection()

    def test_get_units(self):
        unit_model = UnitModel(db=self.db)
        unit_models = unit_model.get_units()

        self.assertIsNotNone(unit_models)
        self.assertTrue(len(unit_models) > 0)

    def test_get_items(self):
        items_model = Item(db=self.db)
        items = items_model.get_items()

        self.assertIsNotNone(items)
        self.assertTrue(len(items) > 0)

    def test_get_item_effects(self):
        item_effects_model = ItemEffects(db=self.db)
        item_effects = item_effects_model.get_item_effects()

        self.assertIsNotNone(item_effects)
        self.assertTrue(len(item_effects) > 0)

    def test_get_unit_items(self):
        unit_items_model = UnitItems(db=self.db)
        unit_items = unit_items_model.get_unit_items()

        self.assertIsNotNone(unit_items)
        self.assertTrue(len(unit_items) > 0)

    def test_get_unit_types(self):
        unit_types_model = UnitType(db=self.db)
        unit_types = unit_types_model.get_unit_types()

        self.assertIsNotNone(unit_types)
        self.assertTrue(len(unit_types) > 0)

if __name__ == '__main__':
    unittest.main()
