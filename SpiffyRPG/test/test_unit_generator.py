# -*- coding: utf-8 -*-
import unittest
from SpiffyWorld import UnitGenerator, Unit

class TestUnitGenerator(unittest.TestCase):
    def test_generate(self):
        unit_gen = UnitGenerator()
        unit = unit_gen.generate()

        self.assertIsInstance(unit, Unit)
        self.assertTrue(len(unit.name) > 0)
        self.assertEqual(len(unit.effects), 0)
