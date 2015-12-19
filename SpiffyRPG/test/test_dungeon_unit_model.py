# -*- coding: utf-8 -*-
import unittest
from SpiffyWorld.models import DungeonUnits

class TestDungeonUnitModel(unittest.TestCase):
    def test_get_dungeon_units_map(self):
        """
        This method should return a dictionary with
        the dungeon as the key, and the a list of dungeon_ids
        as the value
        """
        dungeon_units = [{"dungeon_id": 1, "unit_id": 1},
                        {"dungeon_id": 2, "unit_id": 1},
                        {"dungeon_id": 1, "unit_id": 99},
                        {"dungeon_id": 2, "unit_id": 101}]
        
        expected = {1: [1, 99], 2: [1, 101]}
        dungeon_unit_model = DungeonUnits(db="test")
        actual = dungeon_unit_model._get_dungeon_units_map(dungeon_units)

        self.assertEqual(expected, actual)