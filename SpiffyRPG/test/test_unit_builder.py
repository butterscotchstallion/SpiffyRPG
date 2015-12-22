#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from SpiffyWorld.collections import ItemCollection, EffectCollection, UnitDialogueCollection
from SpiffyWorld.models import UnitItems, UnitEffects, UnitDialogue as UnitDialogueModel
from SpiffyWorld import Item, Unit, UnitBuilder, Effect, UnitDialogue
import logging
from uuid import uuid4
from random import randrange, choice

log = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)

class TestUnitBuilder(unittest.TestCase):
    def _make_dialogue(self):
        dialogue_id = uuid4()
        dialogue_context = "sup"
        dialogue_text = "hello world"

        dialogue_model = {
            "id": dialogue_id,
            "context": dialogue_context,
            "dialogue": dialogue_text,
            "unit_id": uuid4()
        }

        dialogue = UnitDialogue(dialogue=dialogue_model)

        return dialogue

    def _make_item(self, **kwargs):
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

        item = Item(item=item_model)

        return item

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

    def _get_unit_model(self):
        xp = randrange(1, 70000)
        unit_id = uuid4()
        name = "SpiffyNPC-%s" % unit_id

        unit_model = {
            "id": unit_id,
            "unit_name": name,
            "items": [],
            "effects": [],
            "dialogue": [],
            "experience": xp,
            "level": randrange(1, 100),
            "user_id": randrange(0, 9999),
            "is_boss": randrange(0, 1),
            "unit_type_id": randrange(1, 3),
            "unit_type_name": "Hacker",
            "combat_status": "hostile"
        }

        return unit_model

    def test_create_units(self):
        """
        The item collection is populated by models
        """
        item_collection = ItemCollection()
        effect_collection = EffectCollection()
        dialogue_collection = UnitDialogueCollection()

        """
        Prepare unit model collection
        """        
        unit_models = []
        expected_units = []
        unit_items = []
        unit_effects = []
        unit_dialogue = []
        unit_items_model = UnitItems(db="quux")
        unit_effects_model = UnitEffects(db="quux")
        unit_dialogue_model = UnitDialogueModel(db="quux")

        total_units = 25
        total_items_per_unit = 10
        total_effects_per_unit = 5
        total_dialogue_per_unit = 5

        for j in range(0, total_units):
            """
            Add items for each unit
            """
            items = []
            effects = []
            dialogue = []
            unit_model = self._get_unit_model()
            unit_id = unit_model["id"]

            for i in range(0, total_items_per_unit):
                item = self._make_item()
                items.append(item)
                item_collection.add(item)
                unit_items.append({"item_id": item.id, "unit_id": unit_id})

            unit_model["items"] = items
            
            """
            Add effects
            """
            for k in range(0, total_effects_per_unit):
                effect = self._make_effect()
                effects.append(effect)
                effect_collection.add(effect)
                unit_effects.append({"effect_id": effect.id, "unit_id": unit_id})

            unit_model["effects"] = effects

            """
            Add dialogue
            """
            for q in range(0, total_dialogue_per_unit):
                a_dialogue = self._make_dialogue()
                dialogue.append(a_dialogue)
                dialogue_collection.add(a_dialogue)
                unit_dialogue.append({"dialogue_id": a_dialogue.id, "unit_id": unit_id})

            unit_model["dialogue"] = dialogue

            """
            Add completed unit to expected
            """
            unit_models.append(unit_model)
            unit = Unit(unit=unit_model)
            expected_units.append(unit)

        unit_items_map = unit_items_model._get_unit_items_map(unit_items)
        unit_effects_map = unit_effects_model._get_unit_effects_map(unit_effects)
        unit_dialogue_map = unit_dialogue_model._get_unit_dialogue_map(unit_dialogue)

        builder = UnitBuilder()
        actual_units = builder.build_units(unit_models=unit_models,
                                           unit_items_map=unit_items_map,
                                           item_collection=item_collection,
                                           effect_collection=effect_collection,
                                           unit_effects_map=unit_effects_map,
                                           dialogue_collection=dialogue_collection,
                                           unit_dialogue_map=unit_dialogue_map)

        expected_unit_ids = [unit.id for unit in expected_units]
        actual_unit_ids = [unit.id for unit in actual_units]

        self.assertEqual(expected_unit_ids, actual_unit_ids)

        """
        Test that the actual units contain the expected items
        and effects
        """
        self.assertEqual(len(actual_units), len(expected_units))

        for e_unit in expected_units:
            self.assertEqual(len(e_unit.items), total_items_per_unit)
            self.assertEqual(len(e_unit.effects), total_effects_per_unit)
            self.assertEqual(len(e_unit.dialogue), total_dialogue_per_unit)

        for a_unit in actual_units:
            self.assertEqual(len(a_unit.items), total_items_per_unit)
            self.assertEqual(len(a_unit.effects), total_effects_per_unit)
            self.assertEqual(len(a_unit.dialogue), total_dialogue_per_unit)

















