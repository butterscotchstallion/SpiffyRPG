#!/usr/bin/env python
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
        self.assertTrue(len(item.name) > 0)
        self.assertEqual(len(item.effects), 0)

        """
        Test generating with a specific item type
        """
        rock = item_gen.generate(item_type="rock")
        self.assertTrue(rock.is_rock())
        self.assertFalse(rock.is_scissors())
        self.assertFalse(rock.is_paper())
        self.assertFalse(rock.is_lizard())
        self.assertFalse(rock.is_spock())

        paper = item_gen.generate(item_type="paper")
        self.assertTrue(paper.is_paper())
        self.assertFalse(paper.is_scissors())
        self.assertFalse(paper.is_rock())
        self.assertFalse(paper.is_lizard())
        self.assertFalse(paper.is_spock())

        scissors = item_gen.generate(item_type="scissors")
        self.assertTrue(scissors.is_scissors())
        self.assertFalse(scissors.is_paper())
        self.assertFalse(scissors.is_rock())
        self.assertFalse(scissors.is_lizard())
        self.assertFalse(scissors.is_spock())

        lizard = item_gen.generate(item_type="lizard")
        self.assertTrue(lizard.is_lizard())
        self.assertFalse(lizard.is_paper())
        self.assertFalse(lizard.is_rock())
        self.assertFalse(lizard.is_scissors())
        self.assertFalse(lizard.is_spock())

        spock = item_gen.generate(item_type="spock")
        self.assertTrue(spock.is_spock())
        self.assertFalse(spock.is_paper())
        self.assertFalse(spock.is_rock())
        self.assertFalse(spock.is_scissors())
        self.assertFalse(spock.is_lizard())
