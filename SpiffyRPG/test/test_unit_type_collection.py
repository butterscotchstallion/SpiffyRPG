# -*- coding: utf-8 -*-
"""
Tests various aspects of introducing a new player
"""
import unittest
from SpiffyWorld import Unit, UnitType
from SpiffyWorld.collections import UnitTypeCollection

class TestUnitTypeCollection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._collection = UnitTypeCollection()

        unit_types = ({"id": 1, "name": "Troll"}, {"id": 2, "name": "Hacker"},
                      {"id": 2, "name": "Zen Master"})

        for unit_type in unit_types:
            objectified_unit_type = UnitType(unit_type=unit_type)
            cls._collection.add(objectified_unit_type)

    def test_setup(self):
        self.assertEqual(len(self._collection.unit_types), 3)

    def test_get_unit_type_by_invalid_name(self):
        unit_type_collection = self._collection
    
        invalid_player_class = "quux"
        expected = None
        actual = unit_type_collection.get_unit_type_by_name(invalid_player_class)

        self.assertEqual(expected, actual)

    def test_get_unit_type_by_valid_name(self):
        unit_type_collection = self._collection

        valid_unit_type = unit_type_collection.unit_types[0]
        valid_player_class = valid_unit_type.name
        expected_valid_unit_type = valid_unit_type
        actual_valid_unit_type = unit_type_collection.get_unit_type_by_name(valid_player_class)

        self.assertEqual(expected_valid_unit_type, actual_valid_unit_type)

    def test_get_unit_type_by_valid_name_casing(self):
        unit_type_collection = self._collection

        """
        upper
        """
        valid_unit_type = unit_type_collection.unit_types[0]
        valid_player_class = valid_unit_type.name.upper()
        expected_valid_unit_type = valid_unit_type
        actual_valid_unit_type = unit_type_collection.get_unit_type_by_name(valid_player_class)

        self.assertEqual(expected_valid_unit_type, actual_valid_unit_type)

        """
        lower
        """
        valid_unit_type = unit_type_collection.unit_types[0]
        valid_player_class = valid_unit_type.name.lower()
        expected_valid_unit_type = valid_unit_type
        actual_valid_unit_type = unit_type_collection.get_unit_type_by_name(valid_player_class)

        self.assertEqual(expected_valid_unit_type, actual_valid_unit_type)

        """
        mixed
        """
        valid_unit_type = unit_type_collection.unit_types[0]
        valid_player_class = valid_unit_type.name[0].upper()
        expected_valid_unit_type = valid_unit_type
        actual_valid_unit_type = unit_type_collection.get_unit_type_by_name(valid_player_class)

        self.assertEqual(expected_valid_unit_type, actual_valid_unit_type)

    def test_get_unit_type_name_list(self):
        expected = "Hacker, Troll, Zen Master"
        actual = self._collection.get_unit_type_name_list()

        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()