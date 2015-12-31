#!/usr/bin/env python
# -*- coding: utf-8 -*-


class World:
    """
    Representation of the world

    This is a container for all the stuff
    Worldbuilder provides - the end product of
    Worldbuilder.build_world()
    """
    def __init__(self, **kwargs):
        self.irc = kwargs["irc"]
        self.log = kwargs["log"]
        self.dungeon_collection = kwargs["dungeon_collection"]
        self.item_collection = kwargs["item_collection"]
        self.unit_collection = kwargs["unit_collection"]
        self.effect_collection = kwargs["effect_collection"]
        self.dialogue_collection = kwargs["dialogue_collection"]
        self.unit_type_collection = kwargs["unit_type_collection"]
        self.unit_model = kwargs["unit_model"]
        self.battlemaster = kwargs["battlemaster"]

    def destroy(self):
        self.log.info("SpiffyRPG: destroying world!")

        for dungeon in self.dungeons:
            dungeon.destroy()

    def get_dungeon_by_channel(self, channel):
        return self.dungeon_collection.get_dungeon_by_channel(channel)
