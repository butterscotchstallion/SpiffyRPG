# -*- coding: utf-8 -*-
import unittest
from SpiffyWorld import Dungeon, UnitGenerator, Unit

class TestDungeon(unittest.TestCase):
    def _get_dungeon_model(self):
        dungeon_model = {
            "id": 1,
            "name": "TestDungeon",
            "min_level": 1,
            "max_level": 100,
            "description": "foo",
            "channel": "#testing",
            "units": []
        }

        return dungeon_model

    def test_create_dungeon(self):
        dungeon_model = self._get_dungeon_model()
        dungeon = Dungeon(dungeon=dungeon_model, announcer={})

        self.assertEqual(len(dungeon.units), 0)

    def test_add_dungeon_units(self):
        dungeon_model = self._get_dungeon_model()
        dungeon = Dungeon(dungeon=dungeon_model, announcer={})

        unit_generator = UnitGenerator()
        unit = unit_generator.generate()

        dungeon.add_unit(unit)

        dungeon_unit = dungeon.units[0]

        self.assertIsInstance(dungeon_unit, Unit)

    def test_get_unit_by_user_id(self):
        dungeon_model = self._get_dungeon_model()
        dungeon = Dungeon(dungeon=dungeon_model, announcer={})
        user_id = 42
        unit_generator = UnitGenerator()
        unit = unit_generator.generate(user_id=user_id)

        dungeon.add_unit(unit)

        actual = dungeon.get_unit_by_user_id(user_id)

        self.assertIsInstance(actual, Unit)

    def test_get_player_by_user_id(self):
        dungeon_model = self._get_dungeon_model()
        dungeon = Dungeon(dungeon=dungeon_model, announcer={})

        user_id = 42
        unit_generator = UnitGenerator()
        unit = unit_generator.generate(user_id=user_id)

        dungeon.add_unit(unit)

        self.assertTrue(len(dungeon.units), 0)

        actual = dungeon.get_player_by_user_id(user_id)

        self.assertIsInstance(actual, Unit)

    def test_get_unit_by_name(self):
        dungeon_model = self._get_dungeon_model()
        dungeon = Dungeon(dungeon=dungeon_model, announcer={})

        unit_name = "quux"

        unit_generator = UnitGenerator()
        unit = unit_generator.generate(unit_name=unit_name)

        dungeon.add_unit(unit)

        self.assertTrue(len(dungeon.units), 0)

        # test exact match
        actual = dungeon.get_unit_by_name(unit_name)
        self.assertIsInstance(actual, Unit)

        # test invalid match
        actual = dungeon.get_unit_by_name("foo")
        self.assertIsNone(actual)

        # test case sensitivity
        actual = dungeon.get_unit_by_name(unit_name.upper())
        self.assertIsInstance(actual, Unit)

        # test startswith
        actual = dungeon.get_unit_by_name(unit_name[0:1])
        self.assertIsInstance(actual, Unit)

    def test_get_living_unit_by_name(self):
        dungeon_model = self._get_dungeon_model()
        dungeon = Dungeon(dungeon=dungeon_model, announcer={})

        unit_name = "baz"
        unit_generator = UnitGenerator()
        unit = unit_generator.generate(unit_name=unit_name)

        dungeon.add_unit(unit)

        # test typical use case
        actual = dungeon.get_living_unit_by_name(unit.get_name())
        self.assertIsInstance(actual, Unit)

        unit.kill()

        actual = dungeon.get_living_unit_by_name(unit.get_name())
        self.assertIsNone(actual)

    def test_get_dead_unit_by_name(self):
        dungeon_model = self._get_dungeon_model()
        dungeon = Dungeon(dungeon=dungeon_model, announcer={})

        unit_name = "Oliver Queen"
        unit_generator = UnitGenerator()
        unit = unit_generator.generate(unit_name=unit_name)

        dungeon.add_unit(unit)

        unit.kill()

        # test typical use case
        actual = dungeon.get_dead_unit_by_name(unit.get_name())
        self.assertIsInstance(actual, Unit)

        unit.hp = 1

        actual_alive = dungeon.get_living_unit_by_name(unit.get_name())
        self.assertIsInstance(actual_alive, Unit)

    def test_get_living_players(self):
        dungeon_model = self._get_dungeon_model()
        dungeon = Dungeon(dungeon=dungeon_model, announcer={})

        unit_generator = UnitGenerator()

        unit = unit_generator.generate(is_player=True)

        dungeon.add_unit(unit)

        dead_unit = unit_generator.generate()
        dead_unit.kill()

        dungeon.add_unit(dead_unit)

        # test typical use case
        actual = dungeon.get_living_players()
        self.assertEqual(len(actual), 1)

        dead_players = dungeon.get_dead_players()
        self.assertEqual(len(dead_players), 0)

    def test_get_unit_status_distribution(self):
        dungeon_model = self._get_dungeon_model()
        dungeon = Dungeon(dungeon=dungeon_model, announcer={})

        """ living hostile player """
        unit_generator = UnitGenerator()
        living_player = unit_generator.generate(is_player=True,
                                                combat_status="hostile")
        dungeon.add_unit(living_player)

        """ dead friendly NPC """
        dead_friendly_unit = unit_generator.generate(combat_status="friendly")
        dead_friendly_unit.kill()
        dungeon.add_unit(dead_friendly_unit)

        """ living friendly NPC """
        living_npc = unit_generator.generate(combat_status="friendly")
        dungeon.add_unit(living_npc)

        """ living hostile NPC """
        hostile_living_npc = unit_generator.generate(combat_status="hostile")
        dungeon.add_unit(hostile_living_npc)

        actual = dungeon.get_unit_status_distribution()

        expected = {
            "players": {
                "living": 1,
                "dead": 0,
                "undead": 0
            },
            "npc": {
                "hostile": {
                    "living": 1,
                    "dead": 0,
                    "undead": 0
                },
                "friendly": {
                    "living": 1,
                    "dead": 1,
                    "undead": 0
                }
            }
        }

        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()