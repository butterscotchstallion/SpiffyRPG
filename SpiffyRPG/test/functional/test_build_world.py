#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from SpiffyWorld.models import Unit as UnitModel, UnitItems, UnitType, \
    Item, ItemEffects, DungeonUnits, Dungeon, Dialogue
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

        self.assertIsInstance(unit_models, list)
        self.assertTrue(len(unit_models) > 0)

        for unit in unit_models:
            self.assertIsInstance(unit, dict)
            self.assertTrue(unit["id"])
            self.assertTrue(unit["unit_name"])
            self.assertTrue("experience" in unit)
            self.assertTrue(unit["unit_type_name"])
            # Because this can be zero
            self.assertTrue("user_id" in unit)
            self.assertTrue(unit["is_boss"] in (0, 1))

    def test_get_items(self):
        items_model = Item(db=self.db)
        items = items_model.get_items()

        self.assertIsInstance(items, list)
        self.assertTrue(len(items) > 0)

        for item in items:
            self.assertIsInstance(item, dict)
            self.assertTrue(item["id"])
            self.assertTrue(item["name"])
            self.assertTrue("description" in item)
            self.assertTrue("min_level" in item)
            self.assertTrue("max_level" in item)
            self.assertTrue(item["item_type"])
            self.assertTrue("rarity" in item)
            self.assertTrue("equipment_slot" in item)
            self.assertTrue(item["is_permanent"] in ("0", "1"))
            self.assertTrue("unit_type_id" in item)
            self.assertTrue("charges" in item)
            self.assertTrue(item["can_use"] in (0, 1))

    def test_get_item_effects(self):
        item_effects_model = ItemEffects(db=self.db)
        item_effects = item_effects_model.get_item_effects()

        self.assertIsInstance(item_effects, dict)
        self.assertTrue(len(item_effects) > 0)

    def test_get_unit_items(self):
        unit_items_model = UnitItems(db=self.db)
        unit_items = unit_items_model.get_unit_items()

        self.assertIsInstance(unit_items, dict)
        self.assertTrue(len(unit_items) > 0)

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

    def test_get_dialogue(self):
        dialogue_model = Dialogue(db=self.db)
        dialogue = dialogue_model.get_dialogue()

        self.assertIsInstance(dialogue, list)
        self.assertTrue(len(dialogue) > 0)

        for d in dialogue:
            self.assertIsInstance(d, dict)
            self.assertTrue(d["id"])
            self.assertTrue(d["dialogue"])
            self.assertTrue(d["context"])
            self.assertTrue("unit_id" in d)

    def test_get_dungeon_units(self):
        dungeon_units_model = DungeonUnits(db=self.db)
        dungeon_units = dungeon_units_model.get_dungeon_units()

        self.assertIsInstance(dungeon_units, dict)
        self.assertTrue(len(dungeon_units) > 0)

    def test_get_unit_types(self):
        unit_types_model = UnitType(db=self.db)
        unit_types = unit_types_model.get_unit_types()

        self.assertIsInstance(unit_types, list)
        self.assertTrue(len(unit_types) > 0)

if __name__ == '__main__':
    unittest.main()
