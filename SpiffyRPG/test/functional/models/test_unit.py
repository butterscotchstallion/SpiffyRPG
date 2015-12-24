#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from SpiffyWorld.models import Unit as UnitModel
from SpiffyWorld import Database


class TestUnit(unittest.TestCase):

    """
    Functional tests for unit model
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

if __name__ == '__main__':
    unittest.main()
