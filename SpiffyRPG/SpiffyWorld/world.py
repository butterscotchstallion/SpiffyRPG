#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging as log


class World:
    """
    Representation of the world

    This is a container for all the stuff
    Worldbuilder provides - the end product of
    Worldbuilder.build_world()
    """
    def __init__(self, **kwargs):
        self._irc = kwargs["irc"]
        self.dungeon_collection = kwargs["dungeon_collection"]
        self.item_collection = kwargs["item_collection"]
        self.unit_collection = kwargs["unit_collection"]
        self.effect_collection = kwargs["effect_collection"]
        self.dialogue_collection = kwargs["dialogue_collection"]

    def destroy(self):
        log.info("SpiffyRPG: destroying world!")

        for dungeon in self.dungeons:
            dungeon.destroy()

    def get_dungeon_by_channel(self, channel):
        return self.dungeon_collection.get_dungeon_by_channel(channel)
