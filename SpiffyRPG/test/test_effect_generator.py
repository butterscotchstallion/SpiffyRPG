#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from SpiffyWorld import EffectGenerator, Effect


class TestEffectGenerator(unittest.TestCase):

    def test_generate(self):
        eg = EffectGenerator()
        hp_adjustment = 42
        incoming_damage = 0
        outgoing_damage = 0
        stacks = 1
        interval_seconds = 0

        effect = eg.generate(hp_adjustment=hp_adjustment,
                             incoming_damage_adjustment=incoming_damage,
                             outgoing_damage_adjustment=outgoing_damage,
                             stacks=stacks,
                             interval_seconds=interval_seconds)

        self.assertIsInstance(effect, Effect)
        self.assertTrue(len(effect.name) > 0)
        self.assertTrue(len(effect.description) > 0)
        self.assertTrue(len(effect.operator) > 0)
        self.assertTrue(len(effect.description) > 0)
        self.assertEqual(effect.hp_adjustment, hp_adjustment)
        self.assertEqual(
            effect.incoming_damage_adjustment, incoming_damage)
        self.assertEqual(
            effect.outgoing_damage_adjustment, outgoing_damage)
        self.assertEqual(effect.stacks, stacks)
        self.assertEqual(effect.interval_seconds, interval_seconds)
        self.assertTrue(hasattr(effect, "created_at"))
