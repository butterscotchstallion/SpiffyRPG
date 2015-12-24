#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from SpiffyWorld.models import Item
from SpiffyWorld import Database


class TestItem(unittest.TestCase):

    """
    Functional tests for unit model
    """
    @classmethod
    def setUpClass(cls):
        cls._db = Database()
        cls.db = cls._db.get_connection()

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

if __name__ == '__main__':
    unittest.main()
