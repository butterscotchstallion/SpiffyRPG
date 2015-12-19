# -*- coding: utf-8 -*-
import unittest
from SpiffyWorld import UnitType

class TestUnitType(unittest.TestCase):
    def test_create_unit_type(self):
        unit_type_id = 1
        name = "Zen Master"

        unit_type_model = {
            "id": unit_type_id,
            "name": name
        }

        unit_type = UnitType(unit_type=unit_type_model)

        self.assertEqual(unit_type.id, unit_type_id)
        self.assertEqual(unit_type.name, name)

if __name__ == '__main__':
    unittest.main()