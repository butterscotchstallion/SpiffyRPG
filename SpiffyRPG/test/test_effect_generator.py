# -*- coding: utf-8 -*-
import unittest
from SpiffyWorld import EffectGenerator, Effect

class TestEffectGenerator(unittest.TestCase):
    def test_generate(self):
        effect_gen = EffectGenerator()
        hp_adjustment = 42
        incoming_damage_adjustment = 0
        outgoing_damage_adjustment = 0
        stacks = 1
        interval_seconds = 0

        effect = effect_gen.generate(hp_adjustment=hp_adjustment,
                                     incoming_damage_adjustment=incoming_damage_adjustment,
                                     outgoing_damage_adjustment=outgoing_damage_adjustment,
                                     stacks=stacks,
                                     interval_seconds=interval_seconds)

        self.assertIsInstance(effect, Effect)
        self.assertTrue(len(effect.name) > 0)
        self.assertTrue(len(effect.description) > 0)
        self.assertTrue(len(effect.operator) > 0)
        self.assertTrue(len(effect.description) > 0)
        self.assertEqual(effect.hp_adjustment, hp_adjustment)
        self.assertEqual(effect.incoming_damage_adjustment, incoming_damage_adjustment)
        self.assertEqual(effect.outgoing_damage_adjustment, outgoing_damage_adjustment)
        self.assertEqual(effect.stacks, stacks)
        self.assertEqual(effect.interval_seconds, interval_seconds)
        self.assertTrue(hasattr(effect, "created_at"))
