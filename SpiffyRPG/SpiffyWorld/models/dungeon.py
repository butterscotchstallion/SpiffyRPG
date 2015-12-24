#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Dungeon:

    """
    Dungeon model
    """

    def __init__(self, **kwargs):
        self.db = kwargs["db"]

    def get_dungeons(self, **kwargs):
        cursor = self.db.cursor()

        cursor.execute("""SELECT
                          id,
                          name,
                          channel,
                          description,
                          min_level,
                          max_level
                          FROM spiffyrpg_dungeons""")

        dungeons_tmp = cursor.fetchall()

        cursor.close()
        dungeons = []

        if dungeons_tmp:
            for d in dungeons_tmp:
                dungeon = dict(d)

                dungeons.append(dungeon)

        return dungeons
