# -*- coding: utf-8 -*-
import unittest
from SpiffyWorld import Unit

class TestUnit(unittest.TestCase):
    def test_create_player(self):
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

        self.assertEqual(unit.id, unit_id)
        self.assertEqual(unit.name, name)
        self.assertEqual(unit.items, [])
        self.assertEqual(unit.dialogue, [])
        self.assertEqual(unit.experience, xp)
        self.assertEqual(unit.level, level)
        self.assertEqual(unit.is_player, True)
        self.assertEqual(unit.is_npc, False)

    def test_create_npc(self):
        xp = 54001
        level = 30
        name = "SpiffyTester"
        unit_id = 1

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
            "combat_status": "hostile"
        }

        unit = Unit(unit=unit_model)

        self.assertEqual(unit.id, unit_id)
        self.assertEqual(unit.name, name)
        self.assertEqual(unit.items, [])
        self.assertEqual(unit.dialogue, [])
        self.assertEqual(unit.experience, xp)
        self.assertEqual(unit.level, level)
        self.assertEqual(unit.is_player, False)
        self.assertEqual(unit.is_npc, True)

if __name__ == '__main__':
    unittest.main()