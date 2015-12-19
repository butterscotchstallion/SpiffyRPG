# -*- coding: utf-8 -*-
import unittest
from SpiffyWorld import Dungeon, Unit

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

        xp = 6501
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
            "combat_status": "hostile"
        }

        unit = Unit(unit=unit_model)

        dungeon.add_unit(unit)

        dungeon_unit = dungeon.units[0]

        self.assertEqual(dungeon_unit.id, unit_id)
        self.assertEqual(dungeon_unit.name, name)
        self.assertEqual(dungeon_unit.items, [])
        self.assertEqual(dungeon_unit.dialogue, [])
        self.assertEqual(dungeon_unit.experience, xp)
        self.assertEqual(dungeon_unit.level, level)
        self.assertEqual(dungeon_unit.is_player, True)
        self.assertEqual(dungeon_unit.is_npc, False)

    def test_get_unit_by_user_id(self):
        dungeon_model = self._get_dungeon_model()
        dungeon = Dungeon(dungeon=dungeon_model, announcer={})

        xp = 6501
        level = 11
        name = "SpiffyPlayer"
        unit_id = 1
        user_id = 1

        unit_model = {
            "id": unit_id,
            "unit_name": name,
            "items": [],
            "effects": [],
            "dialogue": [],
            "experience": xp,
            "level": level,
            "user_id": user_id,
            "is_boss": 0,
            "unit_type_id": 2,
            "unit_type_name": "Hacker",
            "combat_status": "hostile"
        }

        unit = Unit(unit=unit_model)

        dungeon.add_unit(unit)

        actual = dungeon.get_unit_by_user_id(user_id)

        self.assertIsInstance(actual, Unit)

    def test_get_player_by_user_id(self):
        dungeon_model = self._get_dungeon_model()
        dungeon = Dungeon(dungeon=dungeon_model, announcer={})

        xp = 6501
        level = 11
        name = "SpiffyPlayer"
        unit_id = 1
        user_id = 42

        unit_model = {
            "id": unit_id,
            "unit_name": name,
            "items": [],
            "effects": [],
            "dialogue": [],
            "experience": xp,
            "level": level,
            "user_id": user_id,
            "is_boss": 0,
            "unit_type_id": 2,
            "unit_type_name": "Hacker",
            "combat_status": "hostile"
        }

        unit = Unit(unit=unit_model)

        dungeon.add_unit(unit)

        actual = dungeon.get_player_by_user_id(user_id)

        self.assertIsInstance(actual, Unit)

    def test_get_unit_by_name(self):
        dungeon_model = self._get_dungeon_model()
        dungeon = Dungeon(dungeon=dungeon_model, announcer={})

        xp = 6501
        level = 11
        name = "SpiffyPlayer"
        unit_id = 1
        user_id = 42

        unit_model = {
            "id": unit_id,
            "unit_name": name,
            "items": [],
            "effects": [],
            "dialogue": [],
            "experience": xp,
            "level": level,
            "user_id": user_id,
            "is_boss": 0,
            "unit_type_id": 2,
            "unit_type_name": "Hacker",
            "combat_status": "hostile"
        }

        unit = Unit(unit=unit_model)

        dungeon.add_unit(unit)

        # test exact match
        actual = dungeon.get_unit_by_name(name)
        self.assertIsInstance(actual, Unit)

        # test invalid match
        actual = dungeon.get_unit_by_name("lol")
        self.assertIsNone(actual)

        # test case sensitivity
        actual = dungeon.get_unit_by_name(name.upper())
        self.assertIsInstance(actual, Unit)

        # test startswith
        actual = dungeon.get_unit_by_name("spiffy")
        self.assertIsInstance(actual, Unit)

    def test_get_living_unit_by_name(self):
        dungeon_model = self._get_dungeon_model()
        dungeon = Dungeon(dungeon=dungeon_model, announcer={})

        xp = 6501
        level = 11
        name = "SpiffyPlayer"
        unit_id = 1
        user_id = 42

        unit_model = {
            "id": unit_id,
            "unit_name": name,
            "items": [],
            "effects": [],
            "dialogue": [],
            "experience": xp,
            "level": level,
            "user_id": user_id,
            "is_boss": 0,
            "unit_type_id": 2,
            "unit_type_name": "Hacker",
            "combat_status": "hostile"
        }

        unit = Unit(unit=unit_model)

        dungeon.add_unit(unit)

        # test typical use case
        actual = dungeon.get_living_unit_by_name(name)
        self.assertIsInstance(actual, Unit)

        unit.hp = 0

        actual = dungeon.get_living_unit_by_name(name)
        self.assertIsNone(actual)

    def test_get_dead_unit_by_name(self):
        dungeon_model = self._get_dungeon_model()
        dungeon = Dungeon(dungeon=dungeon_model, announcer={})

        xp = 6501
        level = 11
        name = "SpiffyPlayer"
        unit_id = 1
        user_id = 42

        unit_model = {
            "id": unit_id,
            "unit_name": name,
            "items": [],
            "effects": [],
            "dialogue": [],
            "experience": xp,
            "level": level,
            "user_id": user_id,
            "is_boss": 0,
            "unit_type_id": 2,
            "unit_type_name": "Hacker",
            "combat_status": "hostile"
        }

        unit = Unit(unit=unit_model)

        dungeon.add_unit(unit)

        # test typical use case
        actual = dungeon.get_dead_unit_by_name(name)
        self.assertIsNone(actual)
    
        unit.hp = 1

        actual = dungeon.get_living_unit_by_name(name)
        self.assertIsInstance(actual, Unit)

    def test_get_living_players(self):
        dungeon_model = self._get_dungeon_model()
        dungeon = Dungeon(dungeon=dungeon_model, announcer={})

        xp = 6501
        level = 11
        name = "SpiffyPlayer"
        unit_id = 1
        user_id = 42

        unit_model = {
            "id": unit_id,
            "unit_name": name,
            "items": [],
            "effects": [],
            "dialogue": [],
            "experience": xp,
            "level": level,
            "user_id": user_id,
            "is_boss": 0,
            "unit_type_id": 2,
            "unit_type_name": "Hacker",
            "combat_status": "hostile"
        }

        living_unit = Unit(unit=unit_model)

        dungeon.add_unit(living_unit)

        """ dead unit """
        xp = 6501
        level = 11
        name = "DeadSpiffyNPC"
        unit_id = 2
        user_id = 0

        unit_model = {
            "id": unit_id,
            "unit_name": name,
            "items": [],
            "effects": [],
            "dialogue": [],
            "experience": xp,
            "level": level,
            "user_id": user_id,
            "is_boss": 0,
            "unit_type_id": 2,
            "unit_type_name": "Hacker",
            "combat_status": "hostile"
        }

        dead_unit = Unit(unit=unit_model)
        dead_unit.hp = 0

        dungeon.add_unit(dead_unit)

        # test typical use case
        actual = dungeon.get_living_players()
        self.assertEqual(len(actual), 1)

        dead_players = dungeon.get_dead_players()
        self.assertEqual(len(dead_players), 0)

    def test_get_unit_status_distribution(self):
        dungeon_model = self._get_dungeon_model()
        dungeon = Dungeon(dungeon=dungeon_model, announcer={})

        xp = 6501
        level = 11
        name = "SpiffyPlayer"
        unit_id = 1
        user_id = 42

        unit_model = {
            "id": unit_id,
            "unit_name": name,
            "items": [],
            "effects": [],
            "dialogue": [],
            "experience": xp,
            "level": level,
            "user_id": user_id,
            "is_boss": 0,
            "unit_type_id": 2,
            "unit_type_name": "Hacker",
            "combat_status": "hostile"
        }

        living_unit = Unit(unit=unit_model)

        dungeon.add_unit(living_unit)

        """ dead unit """
        xp = 6501
        level = 11
        name = "DeadSpiffyNPC"
        unit_id = 2
        user_id = 0

        unit_model = {
            "id": unit_id,
            "unit_name": name,
            "items": [],
            "effects": [],
            "dialogue": [],
            "experience": xp,
            "level": level,
            "user_id": user_id,
            "is_boss": 0,
            "unit_type_id": 2,
            "unit_type_name": "Hacker",
            "combat_status": "friendly"
        }

        dead_unit = Unit(unit=unit_model)
        dead_unit.hp = 0

        dungeon.add_unit(dead_unit)

        actual = dungeon.get_unit_status_distribution()

        expected = {
            "players": {
                "living": 1,
                "dead": 0,
                "undead": 0
            },
            "npc": {
                "hostile": {
                    "living": 0,
                    "dead": 0,
                    "undead": 0
                },
                "friendly": {
                    "living": 0,
                    "dead": 1,
                    "undead": 0
                }
            }
        }

        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()