#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from SpiffyWorld.models import UnitType
from SpiffyWorld import Database


class TestItem(unittest.TestCase):

    """
    Functional tests for unit type model
    """
    @classmethod
    def setUpClass(cls):
        cls._db = Database()
        cls.db = cls._db.get_connection()

    def test_get_unit_types(self):
        unit_types_model = UnitType(db=self.db)
        unit_types = unit_types_model.get_unit_types()

        self.assertIsInstance(unit_types, list)
        self.assertTrue(len(unit_types) > 0)

        for unit_type in unit_types:
            self.assertIsInstance(unit_type, dict)
            self.assertTrue("id" in unit_type)
            self.assertTrue("name" in unit_type)

if __name__ == '__main__':
    unittest.main()
