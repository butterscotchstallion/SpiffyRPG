#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from SpiffyWorld.collections import UnitCollection
from SpiffyWorld.models import DungeonUnits
from SpiffyWorld import Dungeon, Unit, DungeonBuilder
from uuid import uuid4
from random import randrange


class TestDungeonBuilder(unittest.TestCase):

    def _get_dungeon_model(self, **kwargs):
        dungeon_id = uuid4()
        dungeon_name = "TestDungeon-%s" % dungeon_id

        dungeon_model = {
            "id": dungeon_id,
            "name": dungeon_name,
            "description": "foo",
            "min_level": 0,
            "max_level": 0,
            "intro": None,
            "channel": "#test",
            "available_start_date": None,
            "available_end_date": None
        }

        return dungeon_model

    def _make_unit(self):
        xp = randrange(1, 70000)
        unit_id = uuid4()
        name = "SpiffyNPC-%s" % unit_id

        unit_model = {
            "id": unit_id,
            "unit_name": name,
            "items": [],
            "effects": [],
            "dialogue": [],
            "experience": xp,
            "level": randrange(1, 100),
            "user_id": randrange(0, 9999),
            "is_boss": randrange(0, 1),
            "unit_type_id": randrange(1, 3),
            "unit_type_name": "Hacker",
            "combat_status": "hostile"
        }

        unit = Unit(unit=unit_model)

        return unit

    def test_create_dungeon(self):
        """
        1. Create dungeons
        2. Create units for each dungeon
        3. Instantiate Dungeon using augmented model
        4. Compare to actual result from DungeonBuilder
        """
        dungeon_models = []
        dungeon_units_list = []
        total_dungeons = 3
        total_units_per_dungeon = 25
        expected_dungeons = []

        unit_collection = UnitCollection()

        for i in range(0, total_dungeons):
            units = []
            dungeon_model = self._get_dungeon_model()
            dungeon_id = dungeon_model["id"]

            for j in range(0, total_units_per_dungeon):
                unit = self._make_unit()
                unit_id = unit.id
                units.append(unit)
                dungeon_units_list.append(
                    {"dungeon_id": dungeon_id, "unit_id": unit_id})

            dungeon_model["units"] = units

            dungeon_models.append(dungeon_model)

            dungeon = Dungeon(dungeon=dungeon_model, announcer="quux")
            expected_dungeons.append(dungeon)

        dungeon_units_model = DungeonUnits(db="quux", announcer="quux")
        dungeon_units_map = dungeon_units_model._get_dungeon_units_map(
            dungeon_units_list)

        builder = DungeonBuilder()
        actual_dungeons = builder.build_dungeons(unit_collection=unit_collection,
                                                 dungeon_models=dungeon_models,
                                                 dungeon_units_map=dungeon_units_map)

        self.assertEqual(len(actual_dungeons), total_dungeons)
        self.assertEqual(len(expected_dungeons), total_dungeons)

        for e_dungeon in expected_dungeons:
            self.assertEqual(len(e_dungeon.units), total_units_per_dungeon)

        for a_dungeon in actual_dungeons:
            self.assertEqual(len(a_dungeon.units), total_units_per_dungeon)
