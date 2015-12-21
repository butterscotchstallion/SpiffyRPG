# -*- coding: utf-8 -*-
import unittest
from SpiffyWorld import EffectGenerator, Effect

class TestEffectGenerator(unittest.TestCase):
    def test_generate(self):
        effect_gen = EffectGenerator()
        effect = effect_gen.generate()

        self.assertIsInstance(effect, Effect)
        self.assertTrue(len(effect.name) > 0)
        self.assertTrue(len(effect.description) > 0)
        self.assertTrue(len(effect.operator) > 0)
        self.assertTrue(len(effect.description) > 0)
        self.assertTrue(hasattr(effect, "hp_adjustment"))
        self.assertTrue(hasattr(effect, "incoming_damage_adjustment"))
        self.assertTrue(hasattr(effect, "outgoing_damage_adjustment"))
        self.assertTrue(hasattr(effect, "stacks"))
        self.assertTrue(hasattr(effect, "interval_seconds"))
        self.assertTrue(hasattr(effect, "created_at"))
