# -*- coding: utf-8 -*-
import unittest

from SpiffyWorld import Battle, Battlemaster, Unit, Item

class TestBattlemaster(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def _make_item(self, **kwargs):
        item_type = kwargs["item_type"]
        item_name = kwargs["item_name"]

        return Item(item={
            "id": 1,
            "name": item_name,
            "description": "foo",
            "item_type": item_type,
            "unit_type_id": 0,
            "min_level": 1,
            "max_level": 1,
            "rarity": "dank",
            "equipment_slot": "main_hand",
            "is_permanent": 0,
            "created_at": "01-01-1970 00:00:00",
            "charges": 0,
            "can_use": 0,
            "effects": []
        })

    def _make_unit(self, **kwargs):
        name = kwargs["name"]
        unit_id = kwargs["id"]

        unit = {
            "id": unit_id,
            "user_id": 0,
            "name": name,
            "unit_name": name,
            "unit_type_name": "TestUnitType",
            "unit_type_id": 1,
            "experience": 6500,
            "is_boss": False,
            "combat_status": "hostile",
            "effects": [],
            "items": [],
            "dialogue": []
        }

        combatant_1 = Unit(unit=unit)

        return combatant_1

    def test_cannot_add_dead_combatants(self):
        combatant_1 = self._make_unit(id=1, name="TestUnit1")
        combatant_2 = self._make_unit(id=2, name="TestUnit2")
        battle = Battle(total_rounds=3)

        combatant_1.hp = 0

        battle.add_combatant(combatant_1)
        battle.add_combatant(combatant_2)

        self.assertEqual(len(battle.combatants), 1)

    def test_add_battle(self):
        combatant_1 = self._make_unit(id=1, name="TestUnit1")
        combatant_2 = self._make_unit(id=2, name="TestUnit2")

        battle = Battle(total_rounds=3)

        battlemaster = Battlemaster()
        battlemaster.add_battle(battle=battle)

        self.assertEqual(len(battlemaster.battles), 1)

        battle.add_combatant(combatant_1)
        battle.add_combatant(combatant_2)

        self.assertEqual(len(battle.combatants), 2)

        actual_1 = battlemaster.get_battle_by_combatant(combatant=combatant_1)
        self.assertIsNotNone(actual_1)
        self.assertEqual(battle, actual_1)

        actual_2 = battlemaster.get_battle_by_combatant(combatant=combatant_2)
        self.assertIsNotNone(actual_2)
        self.assertEqual(battle, actual_2)

        """
        Round 1
        """
        attacker_weapon = self._make_item(item_name="foo", item_type="rock")
        target_weapon = self._make_item(item_name="foo", item_type="scissors")

        hit_info = {
            "is_hit": True,
            "attacker_weapon": attacker_weapon,
            "target_weapon": target_weapon,
            "is_draw": False,
            "hit_word": "hit"
        }

        battle.add_round(attacker=combatant_1,
                         target=combatant_2,
                         hit_info=hit_info)

        self.assertEqual(len(battle.rounds), 1)

        rounds_won_for_combatant_1 = battle.get_rounds_won(combatant=combatant_1)
        rounds_won_for_combatant_2 = battle.get_rounds_won(combatant=combatant_2)

        self.assertEqual(rounds_won_for_combatant_1, 1)
        self.assertEqual(rounds_won_for_combatant_2, 0)

        """
        Round 2
        """
        round_2_attacker_weapon = self._make_item(item_name="foo", item_type="paper")
        round_2_target_weapon = self._make_item(item_name="foo", item_type="rock")

        hit_info = {
            "is_hit": True,
            "attacker_weapon": round_2_attacker_weapon,
            "target_weapon": round_2_target_weapon,
            "is_draw": False,
            "hit_word": "hit"
        }

        battle.add_round(attacker=combatant_2, 
                         target=combatant_1,
                         hit_info=hit_info)

        self.assertEqual(len(battle.rounds), 2)

        rounds_won_for_combatant_1 = battle.get_rounds_won(combatant=combatant_1)
        rounds_won_for_combatant_2 = battle.get_rounds_won(combatant=combatant_2)

        self.assertEqual(rounds_won_for_combatant_1, 1)
        self.assertEqual(rounds_won_for_combatant_2, 1)

        """
        Round 3
        """
        round_3_attacker_weapon = self._make_item(item_name="foo", item_type="lizard")
        round_3_target_weapon = self._make_item(item_name="foo", item_type="spock")

        hit_info = {
            "is_hit": True,
            "attacker_weapon": round_3_attacker_weapon,
            "target_weapon": round_3_target_weapon,
            "is_draw": False,
            "hit_word": "hit"
        }

        battle.add_round(attacker=combatant_1, 
                         target=combatant_2,
                         hit_info=hit_info)

        self.assertEqual(len(battle.rounds), 3)

        rounds_won_for_combatant_1 = battle.get_rounds_won(combatant=combatant_1)
        rounds_won_for_combatant_2 = battle.get_rounds_won(combatant=combatant_2)

        self.assertEqual(rounds_won_for_combatant_1, 2)
        self.assertEqual(rounds_won_for_combatant_2, 1)

        """
        Make sure we can't add a new round and that
        attempting to do so will raise a ValueError
        """
        with self.assertRaises(ValueError):
            battle.add_round(attacker=combatant_1,
                             target=combatant_2,
                             hit_info=hit_info)

            self.assertEqual(len(battle.rounds), 3)

if __name__ == '__main__':
    unittest.main()