# -*- coding: utf-8 -*-
import logging as log

class World:
    """
    Representation of the world

    1. Get dungeon collection
    3. Get lookups for items collection (needed for units)
    4. Get lookups for unit effects collection (needed for units)
    5. Get lookup for NPC units collection
    6. Get lookup for player units collection
    """
    def __init__(self, **kwargs):
        self._irc = kwargs["irc"]
        self.worldbuilder = kwargs["worldbuilder"]

    def populate(self):
        dungeons = self.worldbuilder.dungeons

        for dungeon in dungeons:
            self.add_dungeon(dungeon)

    def add_dungeon(self, dungeon):
        if dungeon not in self.dungeons:
            self.dungeons.append(dungeon)

    def destroy(self):
        log.info("SpiffyRPG: destroying world!")

        for dungeon in self.dungeons:
            dungeon.destroy()

    def get_dungeon_by_channel(self, channel):
        """
        Retrieves dungeons in the current world
        """
        lower_channel = channel.lower()

        for dungeon in self.dungeons:
            """ dungeon.channel is lowered on instantiation """
            if dungeon.channel == lower_channel:
                return dungeon

        log.error("SpiffyRPG: error finding dungeon with channel '%s'" % channel)
