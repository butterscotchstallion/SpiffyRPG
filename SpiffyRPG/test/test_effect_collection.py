#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from SpiffyWorld.collections import EffectCollection
from SpiffyWorld import Effect
import logging

log = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)


class TestEffectCollection(unittest.TestCase):

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

    def test_make_effect_by_effect_name(self):
        effect_name = "Realm King"
        effect = self._make_effect(effect_name=effect_name)

        collection = EffectCollection()
        collection.add(effect)

        expected = effect

        # Typical use case
        actual = collection.get_effect_by_effect_name(effect_name=effect_name)

        self.assertEqual(len(collection.effects), 1)
        self.assertEqual(expected, actual)

        # Test that we don't get the wrong thing
        expected = None
        actual = collection.get_effect_by_effect_name(
            effect_name="hello world")
        self.assertEqual(expected, actual)

    def test_get_effect_undead(self):
        effect_name = "Undead"
        undead_effect = self._make_effect(effect_name=effect_name)

        collection = EffectCollection()

        """
        Test that it doesn't return something
        when the collection is empty
        """
        actual = collection.get_effect_undead()

        self.assertEqual(len(collection.effects), 0)
        self.assertEqual(None, actual)

        # Add undead
        collection.add(undead_effect)

        # Typical use case
        actual = collection.get_effect_undead()

        self.assertEqual(len(collection.effects), 1)
        self.assertEqual(undead_effect, actual)

        """
        Add something other than undead and make sure
        it doesn't return the wrong thing
        """
        effect_name = "Realm King"
        realm_king_effect = self._make_effect(effect_name=effect_name)

        collection.add(realm_king_effect)

        actual = collection.get_effect_undead()

        self.assertEqual(len(collection.effects), 2)
        self.assertEqual(undead_effect, actual)
