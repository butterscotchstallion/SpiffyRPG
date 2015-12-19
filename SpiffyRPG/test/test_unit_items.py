# -*- coding: utf-8 -*-
import unittest
from SpiffyWorld.models import UnitItems

class TestUnitItemsModel(unittest.TestCase):
    def test_get_unit_items_map(self):
        """
        This method should return a dictionary with
        the unit_id as the key, and the a list of item_ids
        as the value
        """
        unit_items = [{"unit_id": 1, "item_id": 1}, 
                      {"unit_id": 2, "item_id": 1},
                      {"unit_id": 1, "item_id": 99},
                      {"unit_id": 2, "item_id": 101}]
        
        expected = {1: [1, 99], 2: [1, 101]}
        unit_items_model = UnitItems(db="test")
        actual = unit_items_model._get_unit_items_map(unit_items)

        self.assertEqual(expected, actual)
