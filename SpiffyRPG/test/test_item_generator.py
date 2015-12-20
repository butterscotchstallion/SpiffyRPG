# -*- coding: utf-8 -*-
import unittest
from SpiffyWorld import ItemGenerator, Item

class TestItemGenerator(unittest.TestCase):
    def test_generate(self):
        item_gen = ItemGenerator()
        item = item_gen.generate()

        self.assertIsInstance(item, Item)
        self.assertEqual(item.charges, 0)
        self.assertEqual(item.can_use, 0)
        self.assertIsNotNone(item.name)
        self.assertEqual(len(item.effects), 0)


