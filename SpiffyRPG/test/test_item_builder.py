# -*- coding: utf-8 -*-
import unittest
from SpiffyWorld.collections import ItemCollection, EffectCollection
from SpiffyWorld.models import ItemEffects
from SpiffyWorld import Item, ItemBuilder, Effect
import logging
from uuid import uuid4
from random import randrange, choice

"""
log = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)
"""

class TestItemBuilder(unittest.TestCase):
    def _get_item_model(self, **kwargs):
        item_id = uuid4()
        item_name = "TestItem-%s" % item_id
        item_types = ("rock", "scissors", "paper", "lizard", "spock")
        item_type = choice(item_types)
        is_permanent = choice([0, 1])

        if "is_permanent" in kwargs:
            is_permanent = kwargs["is_permanent"]

        item_model = {
            "id": item_id,
            "name": item_name,
            "description": "foo",
            "effects": [],
            "min_level": 1,
            "max_level": 100,
            "rarity": "dank",
            "equipment_slot": "main hand",
            "is_permanent": is_permanent,
            "unit_type_id": 0,
            "can_use": 0,
            "charges": 0,
            "created_at": "1",
            "item_type": item_type
        }

        #item = Item(item=item_model)

        return item_model

    def _make_effect(self, **kwargs):
        effect_id = uuid4()
        effect_name = "TestItem-%s" % effect_id
        description = "lorem ipsum"
        hp_adjustment = randrange(1, 100)
        incoming_damage_adjustment = randrange(1, 100)
        outgoing_damage_adjustment = randrange(1, 100)
        stacks = choice([1, 2, 3, 4, 5])
        operator = choice(["+", "*", "-", "/"])

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

    def test_create_item(self):
        """
        1. Create Item
        2. Create effects for each item
        3. Instantiate Item using augmented model
        4. Compare to actual result from ItemBuilder
        """
        item_models = []
        item_effects_list = []
        total_items = 10
        total_effects_per_item = 2
        expected_items = []

        item_collection = ItemCollection()
        effect_collection = EffectCollection()

        for i in range(0, total_items):
            effects = []
            item_model = self._get_item_model()
            item_id = item_model["id"]

            for j in range(0, total_effects_per_item):
                effect = self._make_effect()
                effect_id = effect.id
                effects.append(effect)
                item_effects_list.append({"item_id": item_id, "effect_id": effect_id})

            item_model["effects"] = effects

            item_models.append(item_model)

            item = Item(item=item_model)
            expected_items.append(item)

        item_effects_model = ItemEffects(db="quux")
        item_effects_map = item_effects_model._get_item_effects_map(item_effects_list)

        builder = ItemBuilder()
        actual_items = builder.build_items(item_collection=item_collection,
                                           effect_collection=effect_collection,
                                           item_models=item_models,
                                           item_effects_map=item_effects_map)

        self.assertEqual(len(actual_items), total_items)

        for a_item in actual_items:
            self.assertEqual(len(a_item.effects), total_effects_per_item)


