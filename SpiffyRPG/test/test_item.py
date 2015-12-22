#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from SpiffyWorld import Item


class TestItem(unittest.TestCase):

    """
    Tests the Item class
    """

    def test_create_item(self):
        item_name = "Orb of Testing"
        item_id = 1
        item_type = "rock"

        item_model = {
            "id": item_id,
            "name": item_name,
            "description": "foo",
            "effects": [],
            "min_level": 1,
            "max_level": 0,
            "rarity": "dank",
            "equipment_slot": None,
            "is_permanent": 0,
            "unit_type_id": 0,
            "can_use": 0,
            "charges": 0,
            "created_at": "1",
            "item_type": item_type
        }

        item = Item(item=item_model)

        self.assertEqual(item.id, item_id)
        self.assertEqual(item.name, item_name)
        self.assertEqual(item.item_type, item_type)
        # XXX add tests for the hit words
        #self.assertEqual(item.get_hit_word(), "crushes")

if __name__ == '__main__':
    unittest.main()
