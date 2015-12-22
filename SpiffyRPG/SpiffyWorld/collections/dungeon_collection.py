#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging as log

class DungeonCollection:
    """
    Stores a lookup of dungeons
    """
    def __init__(self, **kwargs):
        self.db = kwargs["db"]
        self.dungeons = []

    def populate(self):
        self.dungeons = self._get_dungeon_lookup()
        log.info("SpiffyRPG: fetching dungoens")

    def get_dungeon_by_channel(self, channel):
        lower_channel = channel.lower()

        if lower_channel in self.dungeons:
            return self.dungeons[lower_channel]

    def _get_dungeon_lookup(self):
        cursor = self.db.cursor()
   
        cursor.execute("""SELECT 
                          id, 
                          name, 
                          channel, 
                          description, 
                          min_level,
                          max_level
                          FROM spiffyrpg_dungeons""")

        dungeons = cursor.fetchall()
        
        cursor.close()

        dungeons_all = []

        if len(dungeons) > 0:
            for d in dungeons:
                d_dungeon = dict(d)
                dungeons_all.append(d_dungeon)

        return dungeons_all