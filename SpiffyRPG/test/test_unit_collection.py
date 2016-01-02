# -*- coding: utf-8 -*-
import unittest
from SpiffyWorld.collections import UnitCollection
from SpiffyWorld import Unit
import logging
from testfixtures import LogCapture


class TestUnitCollection(unittest.TestCase):
    def _get_player_unit(self):
        xp = 6500
        level = 11
        name = "SpiffyPlayer"
        unit_id = 1

        unit_model = {
            "id": unit_id,
            "unit_name": name,
            "items": [],
            "effects": [],
            "dialogue": [],
            "experience": xp,
            "level": level,
            "user_id": 1,
            "is_boss": 0,
            "unit_type_id": 2,
            "unit_type_name": "Hacker",
            "combat_status": "hostile",
            "base_items": []
        }

        with LogCapture():
            logger = logging.getLogger()
            unit = Unit(unit=unit_model, log=logger)

        return unit

    def _get_npc_unit(self):
        xp = 6666
        level = 42
        name = "SpiffyNPC"
        unit_id = 2

        unit_model = {
            "id": unit_id,
            "unit_name": name,
            "items": [],
            "effects": [],
            "dialogue": [],
            "experience": xp,
            "level": level,
            "user_id": 0,
            "is_boss": 0,
            "unit_type_id": 2,
            "unit_type_name": "Hacker",
            "combat_status": "hostile",
            "base_items": []
        }

        with LogCapture():
            logger = logging.getLogger()
            unit = Unit(unit=unit_model, log=logger)

        return unit

    def test_add_unit(self):
        player = self._get_player_unit()
        npc = self._get_npc_unit()

        collection = UnitCollection()
        collection.add(player)
        collection.add(npc)

        self.assertEqual(len(collection.units), 2)

    def test_get_players(self):
        player = self._get_player_unit()
        npc = self._get_npc_unit()

        collection = UnitCollection()
        collection.add(player)
        collection.add(npc)

        players = collection.get_players()

        self.assertEqual(len(players), 1)

        for player in players:
            self.assertEqual(player.is_player, True)

    def test_get_player_by_user_id(self):
        player = self._get_player_unit()
        npc = self._get_npc_unit()

        collection = UnitCollection()
        collection.add(player)
        collection.add(npc)

        user_id = 1
        player = collection.get_player_by_user_id(user_id)

        self.assertIsNotNone(player)
        self.assertEqual(player.user_id, 1)
        self.assertTrue(player.is_player, True)

    def test_get_top_players(self):
        player = self._get_player_unit()
        npc = self._get_npc_unit()

        collection = UnitCollection()
        collection.add(player)

        for j in range(0, 5):
            collection.add(self._get_player_unit())

        collection.add(npc)

        top_players = collection.get_top_players_by_xp()

        self.assertEqual(len(top_players), 3)
        self.assertIsNotNone(top_players)
        self.assertIsNotNone(player)
        self.assertEqual(player.user_id, 1)
        self.assertTrue(player.is_player, True)
