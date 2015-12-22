#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from SpiffyWorld import Effect

class TestEffect(unittest.TestCase):
    def _make_effect(self, **kwargs):
        effect_name = kwargs["effect_name"]
        effect_id = 1
        description = "lorem ipsum"
        hp_adjustment = 0
        incoming_damage_adjustment = 0
        outgoing_damage_adjustment = 0
        stacks = 1
        operator = "+"

        if "operator" in kwargs:
            operator = kwargs["operator"]

        if "hp_adjustment" in kwargs:
            hp_adjustment = kwargs["hp_adjustment"]

        if "stacks" in kwargs:
            stacks = kwargs["stacks"]

        if "incoming_damage_adjustment" in kwargs:
            incoming_damage_adjustment = kwargs["incoming_damage_adjustment"]

        if "outgoing_damage_adjustment" in kwargs:
            outgoing_damage_adjustment = kwargs["outgoing_damage_adjustment"]

        effect_model = {
            "id": effect_id,
            "name": effect_name,
            "description": description,
            "operator": operator,
            "hp_adjustment": hp_adjustment,
            "incoming_damage_adjustment": incoming_damage_adjustment,
            "outgoing_damage_adjustment": outgoing_damage_adjustment,
            "interval_seconds": 0,
            "stacks": stacks
        }

        effect = Effect(effect=effect_model)

        return effect

    def test_create_effect(self):
        effect_name = "QA Engineer's Tenacity"
        effect = self._make_effect(effect_name=effect_name)

        self.assertEqual(effect.name, effect_name)

    def test_get_hp_adjustment(self):
        effect_name = "QA Engineer's Tenacity"
        hp_adjustment = 20
        effect = self._make_effect(effect_name=effect_name,
                                   hp_adjustment=hp_adjustment)

        self.assertEqual(effect.name, effect_name)

        actual_adjustment = effect.get_hp_adjustment()

        self.assertEqual(hp_adjustment, actual_adjustment)

        """
        Increase stacks and re-test
        """
        effect.stacks = 2

        stacks_adjustment = effect.get_hp_adjustment()
        expected_stacks_adjustment = 40

        self.assertEqual(expected_stacks_adjustment, stacks_adjustment)

    def test_get_incoming_damage_adjustment(self):
        effect_name = "Shield of The Great Firewall"
        incoming_damage_adjustment = 90
        effect = self._make_effect(effect_name=effect_name,
                                   operator="*",
                                   incoming_damage_adjustment=incoming_damage_adjustment)

        self.assertEqual(effect.name, effect_name)

        actual_adjustment = effect.get_incoming_damage_adjustment()

        self.assertEqual(incoming_damage_adjustment, actual_adjustment)

        """
        Increase stacks and re-test
        """
        effect.stacks = 2

        stacks_adjustment = effect.get_incoming_damage_adjustment()
        expected_stacks_adjustment = 180

        self.assertEqual(expected_stacks_adjustment, stacks_adjustment)

    def test_get_outgoing_damage_adjustment(self):
        effect_name = "QA Engineer's Tenacity"
        outgoing_damage_adjustment = 20
        effect = self._make_effect(effect_name=effect_name,
                                   outgoing_damage_adjustment=outgoing_damage_adjustment)

        self.assertEqual(effect.name, effect_name)

        actual_adjustment = effect.get_outgoing_damage_adjustment()

        self.assertEqual(outgoing_damage_adjustment, actual_adjustment)

        """
        Increase stacks and re-test
        """
        effect.stacks = 5

        stacks_adjustment = effect.get_outgoing_damage_adjustment()
        expected_stacks_adjustment = 100

        self.assertEqual(expected_stacks_adjustment, stacks_adjustment)

if __name__ == '__main__':
    unittest.main()