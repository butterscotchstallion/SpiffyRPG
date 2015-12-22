#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from SpiffyWorld import Battle, Battlemaster, ItemGenerator, \
    UnitGenerator, InvalidCombatantException


class TestBattlemaster(unittest.TestCase):

    def _make_item(self, **kwargs):
        item_type = kwargs["item_type"]

        item_generator = ItemGenerator()

        return item_generator.generate(item_type=item_type)

    def _make_unit(self, **kwargs):
        unit_generator = UnitGenerator()

        return unit_generator.generate()

    def test_send_challenge(self):
        """
        In order to engage in combat, the unit must consent
        to a challenge. NPCs should accept automatically; an
        attack with an NPC target generates a challenge.
        """
        battle = Battle()
        battlemaster = Battlemaster()

        unit_charlie = self._make_unit(is_player=True, level=5)
        unit_omega = self._make_unit(is_player=True, level=5)

        battle.add_combatant(combatant=unit_charlie)
        battle.add_combatant(combatant=unit_omega)

        battlemaster.add_battle(battle=battle)

        attacker_weapon = self._make_item(item_type="lizard")
        target_weapon = self._make_item(item_type="spock")

        unit_charlie.equip_item(item=attacker_weapon)
        unit_omega.equip_item(item=target_weapon)

        try:
            hit_info = unit_charlie.attack(target=unit_omega)

            battle.add_round(attacker=unit_charlie,
                             target=unit_omega,
                             hit_info=hit_info)
        except InvalidCombatantException:
            """
            In the event of an InvalidCombatantException,
            one of the combatants is dead. Since unit_omega
            was the target of attack we can assume that in
            this scenario that unit is dead. Let's verify that.
            """
            self.assertTrue(unit_omega.is_dead())
            self.assertTrue(unit_charlie.is_alive())

    def test_cannot_start_battle_with_no_combatants(self):
        battle = Battle()

        battlemaster = Battlemaster()

        """
        Attempting to add a battle with less than two
        combatants should raise ValueError
        """
        with self.assertRaises(ValueError):
            battlemaster.add_battle(battle=battle)
            self.assertEqual(len(battlemaster.battles), 0)

    def test_cannot_battle_unit_in_combat(self):
        """
        Units should not be able to start a battle
        if either of them are currently engaged in
        a battle.
        """
        unit_alpha = self._make_unit()
        unit_bravo = self._make_unit()
        unit_delta = self._make_unit()

        # Engage first two targets in battle
        battle = Battle(total_rounds=2)

        battle.add_combatant(unit_alpha)
        battle.add_combatant(unit_bravo)

        self.assertEqual(len(battle.combatants), 2)

        battlemaster = Battlemaster()
        battlemaster.add_battle(battle=battle)

        """
        Make sure we can't add a combatant in battle to
        another battle simultaneously
        """
        another_battle = Battle(total_rounds=2)
        another_battle.add_combatant(unit_alpha)
        another_battle.add_combatant(unit_bravo)
        another_battle.add_combatant(unit_delta)

        """
        Attempting to do this should raise InvalidCombatantException
        because two of the combatants are in battle.
        """
        with self.assertRaises(InvalidCombatantException):
            battlemaster.add_battle(battle=another_battle)

        self.assertEqual(len(battlemaster.battles), 1)

    def test_cannot_add_dead_combatants(self):
        combatant_1 = self._make_unit()
        combatant_2 = self._make_unit()
        battle = Battle(total_rounds=3)

        combatant_1.kill()

        with self.assertRaises(InvalidCombatantException):
            battle.add_combatant(combatant_1)

        battle.add_combatant(combatant_2)
        self.assertEqual(len(battle.combatants), 1)

    def test_add_battle(self):
        combatant_1 = self._make_unit()
        combatant_2 = self._make_unit()

        battle = Battle(total_rounds=3)

        battle.add_combatant(combatant_1)
        battle.add_combatant(combatant_2)

        self.assertEqual(len(battle.combatants), 2)

        battlemaster = Battlemaster()
        battlemaster.add_battle(battle=battle)

        self.assertEqual(len(battlemaster.battles), 1)

        actual_1 = battlemaster.get_battle_by_combatant(combatant=combatant_1)
        self.assertIsNotNone(actual_1)
        self.assertEqual(battle, actual_1)

        actual_2 = battlemaster.get_battle_by_combatant(combatant=combatant_2)
        self.assertIsNotNone(actual_2)
        self.assertEqual(battle, actual_2)

        self.assertTrue(combatant_1.is_alive())
        self.assertTrue(combatant_2.is_alive())

        """
        Round 1
        """
        try:
            attacker_weapon = self._make_item(item_type="rock")
            target_weapon = self._make_item(item_type="scissors")

            combatant_1.equip_item(item=attacker_weapon)
            combatant_2.equip_item(item=target_weapon)

            hit_info = combatant_1.attack(target=combatant_2)

            battle.add_round(attacker=combatant_1,
                             target=combatant_2,
                             hit_info=hit_info)

            self.assertEqual(len(battle.rounds), 1)

            rounds_won_for_combatant_1 = battle.get_rounds_won(
                combatant=combatant_1)
            rounds_won_for_combatant_2 = battle.get_rounds_won(
                combatant=combatant_2)

            self.assertEqual(rounds_won_for_combatant_1, 1)
            self.assertEqual(rounds_won_for_combatant_2, 0)

            """
            Round 2
            """
            round_2_attacker_weapon = self._make_item(item_type="paper")
            round_2_target_weapon = self._make_item(item_type="rock")

            combatant_1.equip_item(item=round_2_attacker_weapon)
            combatant_2.equip_item(item=round_2_target_weapon)

            hit_info = combatant_1.attack(target=combatant_2)

            battle.add_round(attacker=combatant_2,
                             target=combatant_1,
                             hit_info=hit_info)

            self.assertEqual(len(battle.rounds), 2)

            rounds_won_for_combatant_1 = battle.get_rounds_won(
                combatant=combatant_1)
            rounds_won_for_combatant_2 = battle.get_rounds_won(
                combatant=combatant_2)

            self.assertEqual(rounds_won_for_combatant_1, 1)
            self.assertEqual(rounds_won_for_combatant_2, 1)

            """
            Test that units cannot attack twice in a row
            """
            with self.assertRaises(InvalidCombatantException):
                battle.add_round(attacker=combatant_2,
                                 target=combatant_1,
                                 hit_info=hit_info)

                """
                Rounds should not change because adding a new
                round with the same attacker as last round
                should not be possible
                """
                self.assertEqual(len(battle.rounds), 2)

            """
            Round 3
            """
            round_3_attacker_weapon = self._make_item(item_type="lizard")
            round_3_target_weapon = self._make_item(item_type="spock")

            combatant_1.equip_item(item=round_3_attacker_weapon)
            combatant_2.equip_item(item=round_3_target_weapon)

            hit_info = combatant_1.attack(target=combatant_2)

            battle.add_round(attacker=combatant_1,
                             target=combatant_2,
                             hit_info=hit_info)

            self.assertEqual(len(battle.rounds), 3)

            rounds_won_for_combatant_1 = battle.get_rounds_won(
                combatant=combatant_1)
            rounds_won_for_combatant_2 = battle.get_rounds_won(
                combatant=combatant_2)

            self.assertEqual(rounds_won_for_combatant_1, 2)
            self.assertEqual(rounds_won_for_combatant_2, 1)

            """
            Make sure we can't add a new round and that
            attempting to do so will raise a InvalidCombatantException
            """
            with self.assertRaises(InvalidCombatantException):
                battle.add_round(attacker=combatant_1,
                                 target=combatant_2,
                                 hit_info=hit_info)

                self.assertEqual(len(battle.rounds), 3)

        except InvalidCombatantException:
            """
            If we're here, it means that one of the combatants died
            before three rounds were over. This is quite possible, since
            units are randomly generated and could be in different ranges
            """
            self.assertTrue(combatant_1.is_dead() or combatant_2.is_dead())

if __name__ == '__main__':
    unittest.main()
