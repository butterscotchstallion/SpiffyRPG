#!/usr/bin/env python
# -*- coding: utf-8 -*-
from SpiffyWorld import Dungeon


class DungeonBuilder:

    """
    Builds a Dungeon given a list of dungeon/unit models
    and UnitCollection to look up units and such
    """

    def build_dungeons(self, **kwargs):
        dungeon_units_map = kwargs["dungeon_units_map"]
        dungeon_models = kwargs["dungeon_models"]
        dungeons = []

        for dungeon_model in dungeon_models:
            units = []

            dungeon_id = dungeon_model["id"]

            if dungeon_id in dungeon_units_map:
                units = dungeon_units_map[dungeon_id]

            dungeon_model["units"] = units

            dungeon = Dungeon(dungeon=dungeon_model, announcer="quux")

            dungeons.append(dungeon)

        return dungeons
