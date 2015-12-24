#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from SpiffyWorld.models import Effect
from SpiffyWorld import Database


class TestEffect(unittest.TestCase):

    """
    Functional tests for effect model
    """
    @classmethod
    def setUpClass(cls):
        cls._db = Database()
        cls.db = cls._db.get_connection()

    def test_get_effects(self):
        effects_model = Effect(db=self.db)
        effects = effects_model.get_effects()

        self.assertIsInstance(effects, list)
        self.assertTrue(len(effects) > 0)

        for effect in effects:
            self.assertIsInstance(effect, dict)
            self.assertTrue(effect["id"])
            self.assertTrue(effect["name"])
            self.assertTrue("description" in effect)
            self.assertTrue("operator" in effect)
            self.assertTrue("hp_adjustment" in effect)
            self.assertTrue("incoming_damage_adjustment" in effect)
            self.assertTrue("outgoing_damage_adjustment" in effect)
            self.assertTrue("interval_seconds" in effect)
            self.assertTrue("stacks" in effect)

if __name__ == '__main__':
    unittest.main()
