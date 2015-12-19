# -*- coding: utf-8 -*-

from SpiffyWorld import DungeonCollection, ItemCollection, \
EffectsCollection, DialogueCollection, UnitTitleCollection, Database, \
PlayerUnitCollection, UnitEffectsCollection, DungeonUnitCollection, \
Item, Effect, Unit

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

        self.items = []
        self.item_collection = ItemCollection(db=self.db)
        
        self.effects = []
        self.effects_collection = EffectsCollection(db=self.db)

        self.unit_effects = []
        self.unit_effects_collection = UnitEffectsCollection(db=self.db)
        
        self.dialogue = []
        self.dialogue_collection = DialogueCollection(db=self.db)

        self.unit_titles = {}
        self.unit_title_collection = UnitTitleCollection(db=self.db)

        self.dungeon_units = {}
        self.dungeon_unit_collection = DungeonUnitCollection(db=self.db)

        self.player_units = []
        self.player_unit_collection = PlayerUnitCollection(db=self.db)

        self.dungeons = []
        self.dungeon_collection = DungeonCollection(db=self.db)

    def build(self):
        """
        Populate retrieves db info and build
        uses that to create objects
        """
        self._populate_collections()

        self._build_effects()
        self._build_items()
        self._build_unit_effects()
        self._build_dungeon_units()
        self._build_player_units()
        self._build_dungeons()

    def _populate_collections(self):
        self.item_collection.populate()
        self.effects_collection.populate()
        self.unit_effects_collection.populate()
        self.dialogue_collection.populate()
        self.dungeon_unit_collection.populate()
        self.player_unit_collection.populate()
        self.dungeon_collection.populate()

    def _build_items(self):
        for litem in self.item_collection.items:
            """
            Check if this item has any effects associated
            """
            lid = litem["id"]
            
            if lid in self.item_collection.item_effects:
                fx = self.item_collection.item_effects[lid]
                
                for f in fx:
                    objectified_effect = Effect(effect=f)
                    litem["effects"].append(objectified_effect)

            objectified_item = Item(item=litem)
            self.items.append(objectified_item)

    def _build_effects(self):
        for leffect in self.effects_collection.effects:
            objectified_effect = Effect(effect=leffect)
            self.effects.append(objectified_effect)

    def _build_unit_effects(self):
        for leffect in self.unit_effects_collection.effects:
            objectified_effect = Effect(effect=leffect)

            self.unit_effects.append(objectified_effect)

    def _build_dungeon_units(self):
        for lunit in self.dungeon_unit_collection.units:
            objectified_unit = Unit(db=self.db, unit=lunit, worldbuilder=self)

            self.dungeon_units.append(objectified_unit)

    def _build_player_units(self):
        for lunit in self.player_unit_collection.units:
            objectified_unit = Unit(db=self.db, unit=lunit, worldbuilder=self)
            self.player_units.append(objectified_unit)

    def _build_dungeons(self):
        for ldungeon in self.dungeon_collection.dungeons:
            objectified_dungeon = Dungeon(dungeon=ldungeon, worldbuilder=worldbuilder)
            self.dungeons.append(objectified_dungeon)
