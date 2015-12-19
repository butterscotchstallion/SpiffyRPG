# -*- coding: utf-8 -*-
import unittest
from uuid import uuid4
from random import randrange, choice
from SpiffyWorld import Unit, UnitLevel, Item, UnitBuilder
from SpiffyWorld.collections import ItemCollection
from SpiffyWorld.models import UnitItems

class TestUnit(unittest.TestCase):
    def _get_item(self, **kwargs):
        item_id = uuid4()
        item_name = "Item%s" % item_id
        item_type = kwargs["item_type"]
        is_permanent = 0

        if "is_permanent" in kwargs:
            is_permanent = kwargs["is_permanent"]

        item_model = {
            "id": item_id,
            "name": item_name,
            "description": "foo",
            "effects": [],
            "min_level": 1,
            "max_level": 0,
            "rarity": "dank",
            "equipment_slot": None,
            "is_permanent": is_permanent,
            "unit_type_id": 0,
            "can_use": 0,
            "charges": 0,
            "created_at": "1",
            "item_type": item_type
        }

        item = Item(item=item_model)

        return item

    def _get_unit_model(self, **kwargs):
        unit_level = UnitLevel()
        is_player = False
        level = randrange(1, 100)
        xp = unit_level.get_xp_for_level(level)
        unit_id = uuid4()
        unit_name = "Unit%s" % unit_id
        unit_types = (1, 2, 3)
        unit_type_id = choice(unit_types)
        
        if "is_player" in kwargs:
            is_player = kwargs["is_player"]

        user_id = 0

        if is_player:
            user_id = randrange(1, 999)

        unit_model = {
            "id": unit_id,
            "unit_name": unit_name,
            "items": [],
            "effects": [],
            "dialogue": [],
            "experience": xp,
            "level": level,
            "user_id": user_id,
            "is_boss": 0,
            "unit_type_id": unit_type_id,
            "unit_type_name": "quux",
            "combat_status": "hostile"
        }

        return unit_model

    def test_create_player(self):
        unit_model = self._get_unit_model(is_player=True)

        unit = Unit(unit=unit_model)

        self.assertEqual(unit.is_player, True)
        self.assertEqual(unit.is_npc, False)

    def test_create_npc(self):
        unit_model = self._get_unit_model(is_player=False)

        unit = Unit(unit=unit_model)

        self.assertEqual(unit.is_player, False)
        self.assertEqual(unit.is_npc, True)

    def test_unit_attacks(self):
        """
        Create units, with an item of each type
        """
        item_collection = ItemCollection()
        unit_models = []
        unit_items_list = []
        expected_units = []

        item_types = ("rock", "paper", "scissors", "lizard", "spock")
        for item_type in item_types:
            item = self._get_item(item_type=item_type)
            item_collection.add(item)

        for j in range(0, 2):
            unit_model = self._get_unit_model()
            unit_id = unit_model["id"]

            for c_item in item_collection.items:
                unit_items_list.append({"item_id": c_item.id,
                                       "unit_id": unit_id})
                unit_model["items"].append(c_item)

            unit = Unit(unit=unit_model)
            expected_units.append(unit)
            unit_models.append(unit_model)

        """
        Although we added more items, the collection should
        never add duplicates
        """
        total_items = len(item_types)
        self.assertEqual(len(item_collection.items), total_items)

        """
        There two units with five items each, so unit_items_map
        should have ten items total
        """
        unit_items_list_length = len(unit_items_list)
        self.assertEqual(unit_items_list_length, 10)

        builder = UnitBuilder()
        unit_items_model = UnitItems(db="quux")
        unit_items_map = unit_items_model._get_unit_items_map(unit_items_list)

        actual_units = builder.build_units(unit_models=unit_models,
                                           unit_items_map=unit_items_map,
                                           item_collection=item_collection,
                                           effect_collection="quux",
                                           dialogue_collection="quux",
                                           unit_effects_map={},
                                           unit_dialogue_map={})

        self.assertEqual(len(expected_units), len(actual_units))

        unit_items = [item for item in item_collection.items]

        for unit in actual_units:
            self.assertEqual(unit.items, unit_items)

        


if __name__ == '__main__':
    unittest.main()