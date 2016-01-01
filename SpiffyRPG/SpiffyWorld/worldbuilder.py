#!/usr/bin/env python
# -*- coding: utf-8 -*-

from SpiffyWorld.models import Dungeon as DungeonModel, \
    Effect as EffectModel, ItemEffects, Item as ItemModel, \
    UnitEffects, DungeonUnits, UnitDialogue as UnitDialogueModel, \
    UnitItems as UnitItemsModel, Unit as UnitModel, UnitType as UnitTypeModel
from SpiffyWorld.collections import EffectCollection, ItemCollection, \
    UnitDialogueCollection, UnitCollection, DungeonCollection, \
    UnitTypeCollection
from SpiffyWorld import Effect, ItemBuilder, World, Dungeon, UnitDialogue, \
    UnitBuilder, UnitType, DungeonAnnouncer, Battlemaster


class Worldbuilder:
    """
    Builds dependencies for the world based on DB models

    1. Get everything we need to build a unit:
        a. Items
        b. Effects
        c. Unit Effects
        d. dialogue
        e. unit titles
    2. Get everything we need to build a dungeon
        a. Units
    3. Get everything we need to build a world
        a. Dungeons with units
    """
    def __init__(self, **kwargs):
        self.db = kwargs["db"]
        self.irc = kwargs["irc"]
        self.ircmsgs = kwargs["ircmsgs"]
        self.ircutils = kwargs["ircutils"]
        self.log = kwargs["log"]

    def build_world(self):
        """
        Populate retrieves db info and build
        uses that to create objects
        """
        effect_collection = self._build_effects()
        item_collection = \
            self._build_items(effect_collection=effect_collection)

        dialogue_info = self._build_dialogue()
        dialogue_collection = dialogue_info["dialogue_collection"]
        unit_dialogue_map = dialogue_info["unit_dialogue_map"]

        unit_effects_map = self._build_unit_effects()
        dungeon_unit_info = self._build_dungeon_units()
        dungeon_unit_models = dungeon_unit_info["dungeon_unit_models"]
        dungeon_unit_map = dungeon_unit_info["dungeon_unit_map"]
        unit_items_map = self._build_unit_items(item_collection)
        unit_type_collection = self._build_unit_types()

        unit_info = \
            self._build_units(item_collection=item_collection,
                              effect_collection=effect_collection,
                              dialogue_collection=dialogue_collection,
                              unit_effects_map=unit_effects_map,
                              unit_items_map=unit_items_map,
                              unit_dialogue_map=unit_dialogue_map)
        unit_collection = unit_info["unit_collection"]
        unit_model = unit_info["unit_model"]

        dungeon_collection = \
            self._build_dungeons(dungeon_unit_map=dungeon_unit_map,
                                 dungeon_unit_models=dungeon_unit_models,
                                 unit_collection=unit_collection)

        battlemaster = Battlemaster()

        world = World(effect_collection=effect_collection,
                      item_collection=item_collection,
                      unit_collection=unit_collection,
                      dialogue_collection=dialogue_collection,
                      dungeon_collection=dungeon_collection,
                      unit_type_collection=unit_type_collection,
                      unit_model=unit_model,
                      battlemaster=battlemaster,
                      irc=self.irc,
                      log=self.log)

        return world

    def _build_unit_types(self):
        self.log.info("Building unit types")

        unit_type_model = UnitTypeModel(db=self.db)
        unit_types = unit_type_model.get_unit_types()
        unit_type_collection = UnitTypeCollection()

        if unit_types:
            for ut in unit_types:
                unit_type = UnitType(unit_type=ut)
                unit_type_collection.add(unit_type)

        return unit_type_collection

    def _build_units(self, **kwargs):
        self.log.info("Building units")

        unit_model = UnitModel(db=self.db)
        unit_models = unit_model.get_units()

        item_collection = kwargs["item_collection"]
        effect_collection = kwargs["effect_collection"]
        dialogue_collection = kwargs["dialogue_collection"]
        unit_effects_map = kwargs["unit_effects_map"]
        unit_dialogue_map = kwargs["unit_dialogue_map"]
        unit_items_map = kwargs["unit_items_map"]

        unit_builder = UnitBuilder()
        unit_collection = UnitCollection()
        units = \
            unit_builder.build_units(unit_models=unit_models,
                                     item_collection=item_collection,
                                     effect_collection=effect_collection,
                                     dialogue_collection=dialogue_collection,
                                     unit_effects_map=unit_effects_map,
                                     unit_items_map=unit_items_map,
                                     unit_dialogue_map=unit_dialogue_map,
                                     log=self.log)

        for unit in units:
            unit_collection.add(unit)

        return {
            "unit_collection": unit_collection,
            "unit_model": unit_model
        }

    def _build_unit_items(self, item_collection):
        self.log.info("Building unit items")

        unit_items_model = UnitItemsModel(db=self.db)
        unit_item_models = unit_items_model.get_unit_items()
        unit_items_map = unit_items_model._get_unit_items_map(unit_item_models)

        return unit_items_map

    def _build_dialogue(self, **kwargs):
        self.log.info("Building dialogue")

        dialogue_collection = UnitDialogueCollection()
        dialogue_model = UnitDialogueModel(db=self.db)
        dialogue_models = dialogue_model.get_unit_dialogue()
        unit_dialogue_map = \
            dialogue_model._get_unit_dialogue_map(dialogue_models)

        for dialogue_model in dialogue_models:
            dialogue = UnitDialogue(dialogue=dialogue_model)
            dialogue_collection.add(dialogue)

        return {
            "dialogue_collection": dialogue_collection,
            "unit_dialogue_map": unit_dialogue_map
        }

    def _build_items(self, **kwargs):
        """
        This requires a populated EffectCollection in order
        to build the items due to the fact that items can have
        associated effects.
        """
        self.log.info("Building items")

        effect_collection = kwargs["effect_collection"]

        item_builder = ItemBuilder()
        item_model = ItemModel(db=self.db)
        item_models = item_model.get_items()
        item_effects_model = ItemEffects(db=self.db)
        item_effects_map = item_effects_model.get_item_effects()
        item_collection = ItemCollection()
        items = item_builder.build_items(item_models=item_models,
                                         item_effects_map=item_effects_map,
                                         effect_collection=effect_collection)

        for item in items:
            item_collection.add(item)

        return item_collection

    def _build_effects(self):
        """
        Returns a populated EffectCollection
        """
        self.log.info("Building effects")

        effects_collection = EffectCollection()
        effects_model = EffectModel(db=self.db)
        effects_models = effects_model.get_effects()

        for effect_model in effects_models:
            effect = Effect(effect=effect_model)

            effects_collection.add(effect)

        return effects_collection

    def _build_unit_effects(self):
        self.log.info("Building unit effects")

        unit_effects_model = UnitEffects(db=self.db)
        unit_effects = unit_effects_model.get_unit_effects()
        unit_effects_map = \
            unit_effects_model._get_unit_effects_map(unit_effects)

        return unit_effects_map

    def _build_dungeon_units(self):
        self.log.info("Building dungeon units")

        dungeon_units_model = DungeonUnits(db=self.db)
        dungeon_units = dungeon_units_model.get_dungeon_units()
        dungeon_units_map = \
            dungeon_units_model._get_dungeon_units_map(dungeon_units)

        return {
            "dungeon_unit_map": dungeon_units_map,
            "dungeon_unit_models": dungeon_units
        }

    def _build_dungeons(self, **kwargs):
        """
        Add units from map/collection
        """
        self.log.info("Building dungeons")

        total_units = 0
        player_units = 0
        npc_units = 0
        dungeon_collection = DungeonCollection()
        unit_collection = kwargs["unit_collection"]
        dungeon_unit_map = kwargs["dungeon_unit_map"]
        dungeon_unit_models = kwargs["dungeon_unit_models"]

        dungeon_model = DungeonModel(db=self.db)
        dungeon_models = dungeon_model.get_dungeons()

        for dungeon_model in dungeon_models:
            dungeon_id = dungeon_model["id"]
            units = []

            for dungeon_unit_model in dungeon_unit_models:
                if dungeon_id in dungeon_unit_map:
                    unit_id_list = dungeon_unit_map[dungeon_id]
                    units = \
                        unit_collection.get_units_by_unit_id_list(unit_id_list)

            """
            Any units that are not in the dungeon (players)
            """
            other_units = unit_collection.units

            for ounit in other_units:
                if ounit not in units:
                    units.append(ounit)

            announcer = DungeonAnnouncer(irc=self.irc,
                                         ircutils=self.ircutils,
                                         ircmsgs=self.ircmsgs,
                                         destination="#spiffyrpg")

            dungeon = Dungeon(dungeon=dungeon_model,
                              announcer=announcer,
                              log=self.log)

            for unit in units:
                added_unit = dungeon.add_unit(unit)

                if added_unit is not None:
                    total_units += 1

                    if unit.is_player:
                        player_units += 1

                    if unit.is_npc:
                        npc_units += 1

            dungeon_collection.add(dungeon)

        total_dungeons = len(dungeon_collection.dungeons)

        debug_msg = "SpiffyWorld: %s dungeons with " % total_dungeons
        debug_msg += "%s NPCs, %s players loaded" % \
            (npc_units, player_units)

        self.log.info(debug_msg)

        return dungeon_collection
