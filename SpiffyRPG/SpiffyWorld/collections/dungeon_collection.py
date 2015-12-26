#!/usr/bin/env python
# -*- coding: utf-8 -*-
from SpiffyWorld import Dungeon


class DungeonCollection:

    """
    A collection of Dungeons
    """

    def __init__(self, **kwargs):
        self.dungeons = []

    def add(self, dungeon):
        if not isinstance(dungeon, Dungeon):
            raise ValueError("dungeon must be an instance of Dungeon")

        if dungeon not in self.dungeons:
            self.dungeons.append(dungeon)

    def get_dungeon_by_channel(self, channel):
        lower_channel = channel.lower()

        for dungeon in self.dungeons:
            if dungeon.channel.lower() == lower_channel:
                return dungeon
