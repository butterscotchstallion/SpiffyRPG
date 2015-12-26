#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from SpiffyWorld import Database
from SpiffyWorld.models import Dungeon as DungeonModel, Effect as EffectModel, \
    ItemEffects, Item as ItemModel, UnitItems, Unit as UnitModel, UnitEffects, \
    UnitDialogue as UnitDialogueModel
from SpiffyWorld.collections import UnitCollection, ItemCollection, \
    EffectCollection, UnitDialogueCollection
from SpiffyWorld import UnitBuilder, Effect, Unit, UnitDialogue, \
    ItemBuilder


class TestBuildWorld(unittest.TestCase):

    """
    Functional tests for building the world
    """
    @classmethod
    def setUpClass(cls):
        cls._db = Database()
        cls.db = cls._db.get_connection()

    def test_build_world(self):
        """
        Utilize models to build the world.

        1. Get dungeons
        2. Get effects
        3. Get item effects
        4. Get items
        5. Get unit items
        6. Get units
        """

        """ Dungeons """
        dungeon_model = DungeonModel(db=self.db)
        dungeon_models = dungeon_model.get_dungeons()

        self.assertIsInstance(dungeon_models, list)
        self.assertTrue(dungeon_models)

        """ Effects """
        effects_model = EffectModel(db=self.db)
        effects_models = effects_model.get_effects()

        self.assertIsInstance(effects_models, list)
        self.assertTrue(effects_models)

        """ Unit effects map """
        unit_effects_model = UnitEffects(db=self.db)
        unit_effects = unit_effects_model.get_unit_effects()
        unit_effects_map = unit_effects_model._get_unit_effects_map(unit_effects)

        self.assertIsInstance(unit_effects_map, dict)
        self.assertTrue(unit_effects_map)

        """ Unit dialogue map """
        unit_dialogue_model = UnitDialogueModel(db=self.db)
        unit_dialogue = unit_dialogue_model.get_unit_dialogue()
        unit_dialogue_map = unit_dialogue_model._get_unit_dialogue_map(unit_dialogue)

        self.assertIsInstance(unit_dialogue, list)
        self.assertIsInstance(unit_dialogue_map, dict)
        self.assertTrue(unit_dialogue_map)

        """ Item effects map """
        item_effects_model = ItemEffects(db=self.db)
        item_effects = item_effects_model.get_item_effects()
        item_effects_map = item_effects_model._get_item_effects_map(item_effects)

        self.assertIsInstance(item_effects, list)
        self.assertIsInstance(item_effects_map, dict)
        self.assertTrue(item_effects_map)
        self.assertTrue(item_effects)

        """ Items """
        item_model = ItemModel(db=self.db)
        item_models = item_model.get_items()

        self.assertIsInstance(item_models, list)
        self.assertTrue(item_models)

        """ Unit items map """
        unit_items_model = UnitItems(db=self.db)
        unit_item_models = unit_items_model.get_unit_items()
        unit_items_map = unit_items_model._get_unit_items_map(unit_item_models)

        self.assertIsInstance(unit_item_models, list)
        self.assertIsInstance(unit_items_map, dict)
        self.assertTrue(unit_items_map)
        self.assertTrue(unit_item_models)

        """ Units """
        unit_model = UnitModel(db=self.db)
        unit_models = unit_model.get_units()

        self.assertIsInstance(unit_models, list)
        self.assertTrue(unit_models)

        """ Assemble collections using models """
        item_collection = ItemCollection()
        effect_collection = EffectCollection()
        dialogue_collection = UnitDialogueCollection()

        for effect_model in effects_models:
            effect = Effect(effect=effect_model)
            effect_collection.add(effect)

        self.assertTrue(effect_collection.effects)

        item_builder = ItemBuilder()
        items = item_builder.build_items(item_models=item_models,
                                         item_effects_map=item_effects_map,
                                         effect_collection=effect_collection)
        self.assertIsInstance(items, list)
        self.assertTrue(items)

        for item in items:
            item_collection.add(item)

        self.assertTrue(item_collection.items)

        for ud in unit_dialogue:
            dialogue = UnitDialogue(dialogue=ud)
            dialogue_collection.add(dialogue)

        """ Build units using assembled collections """
        unit_builder = UnitBuilder()

        units = unit_builder.build_units(unit_models=unit_models,
                                         effect_collection=effect_collection,
                                         item_collection=item_collection,
                                         dialogue_collection=dialogue_collection,
                                         unit_items_map=unit_items_map,
                                         unit_effects_map=unit_effects_map,
                                         unit_dialogue_map=unit_dialogue_map)

        self.assertIsInstance(units, list)
        self.assertTrue(units)

        for unit in units:
            self.assertIsInstance(unit, Unit)

        """
        Populate collections
        """
        unit_collection = UnitCollection()

        for unit in units:
            unit_collection.add(unit)

        self.assertEqual(len(unit_collection.units), len(unit_models))

if __name__ == '__main__':
    unittest.main()
