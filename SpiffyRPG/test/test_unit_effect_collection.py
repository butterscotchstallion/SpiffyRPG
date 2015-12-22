#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from SpiffyWorld.collections import UnitEffectCollection, EffectCollection
from SpiffyWorld import Effect
import logging

log = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)

class TestUnitEffectCollection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

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

    def test_add_effect(self):
        effect_name = "Test Effect"
        effect_type = "rock"
        effect = self._make_effect(effect_name=effect_name)
        
        collection = EffectCollection()
        collection.add(effect)

        expected = effect
        actual = collection.get_effect_by_effect_name(effect_name=effect_name)

        self.assertEqual(len(collection.effects), 1)
        self.assertEqual(expected, actual)

        # Test that we can't add duplicate effects
        collection.add(effect)
        self.assertEqual(len(collection.effects), 1)

