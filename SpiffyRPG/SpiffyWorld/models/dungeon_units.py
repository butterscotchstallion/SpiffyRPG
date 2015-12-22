#!/usr/bin/env python
# -*- coding: utf-8 -*-

class DungeonUnits:
    """
    Dungeon units model
    """
    def __init__(self, **kwargs):
        self.db = kwargs["db"]

    def _get_dungeon_units_map(self, units):
        dungeon_units_map = {}

        for dungeon_unit in units:
            dungeon_id = dungeon_unit["dungeon_id"]

            if dungeon_id not in dungeon_units_map:
                dungeon_units_map[dungeon_id] = []

            dungeon_units_map[dungeon_id].append(dungeon_unit["unit_id"])

        return dungeon_units_map

    def get_dungeon_units(self):
        """
        Fetches units for one or many dungeons
        """
        cursor = self.db.cursor()
        
        cursor.execute("""SELECT
                          du.dungeon_id,
                          du.unit_id
                          FROM spiffyrpg_dungeon_units du
                          JOIN spiffyrpg_units u ON du.unit_id = u.id""")

        tmp_units = cursor.fetchall()
        cursor.close()
        units = []

        if tmp_units:
            for u in tmp_units:
                unit = dict(u)
                units.append(unit)

        return self._get_dungeon_units_map(units)