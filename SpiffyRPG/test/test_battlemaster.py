#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import logging
from testfixtures import LogCapture
from SpiffyWorld import Battle, Battlemaster, ItemGenerator, \
    UnitGenerator, InvalidCombatantException, Dungeon, DungeonAnnouncer
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils


class TestBattlemaster(unittest.TestCase):
    """
    Tests battle interactions between units
    """
    def _make_item(self, **kwargs):
        item_type = kwargs["item_type"]

        item_generator = ItemGenerator()

        return item_generator.generate(item_type=item_type)

    def _make_unit(self, **kwargs):
        level = kwargs["level"]
        unit_generator = UnitGenerator()

        return unit_generator.generate(level=level)

    def _make_dungeon(self):
        dungeon_model = {
            "id": 1,
            "name": "TestDungeon",
            "min_level": 1,
            "max_level": 100,
            "description": "foo",
            "channel": "#SpiffyRPG",
            "units": []
        }

        dungeon_announcer = DungeonAnnouncer(ircmsgs=ircmsgs,
                                             ircutils=ircutils,
                                             testing=True,
                                             destination=dungeon_model["channel"],
                                             irc="quux")

        with LogCapture():
            logger = logging.getLogger()
            dungeon = Dungeon(announcer=dungeon_announcer,
                              dungeon=dungeon_model,
                              log=logger)

        return dungeon

    def test_battle_cannot_add_non_hostile_combatants(self):
        pass

    def test_battle_add_challenge(self):
        """
        In order to engage in combat, the unit must consent
        to a challenge. NPCs should accept automatically; an
        attack with an NPC target generates a challenge.

        If NPC:
        - issue challenge immediately adds challenge

        if PC:
        - issue challenge adds to battlemaster.challenges
        and accepting adds hostile combatant to target

        A battle ending or a unit dying should clear
        hostile combatants
        """
        with LogCapture():
            logger = logging.getLogger()
            battle = Battle(log=logger)

        battlemaster = Battlemaster()

        unit_charlie = self._make_unit(is_player=True, level=13)
        unit_omega = self._make_unit(is_player=True, level=13)

        """
        Could adding a combatant automatically issue a challenge?
        """
        battle.add_combatant(combatant=unit_charlie)
        battle.add_combatant(combatant=unit_omega)

        self.assertEqual(len(battle.combatants), 2, "Failed to add combatants")

        """
        The battlemaster issues a challenge on behalf of
        unit_charlie!
        """
        battlemaster.issue_challenge(attacker=unit_charlie,
                                     target=unit_omega)

        self.assertEqual(len(battlemaster.challenges), 1)

        """
        After the challenge has been issued, verify that
        the Battlemaster has recorded that
        """
        has_challenged = \
            battlemaster.has_accepted_challenge(attacker=unit_charlie,
                                                target=unit_omega)

        self.assertFalse(has_challenged, "Failed to issue challenge")

        # Attempt to accept challenge
        battlemaster.accept_challenge_from_target(attacker=unit_charlie,
                                                  target=unit_omega)

        accepted_challenge = \
            battlemaster.has_accepted_challenge(attacker=unit_charlie,
                                                target=unit_omega)

        self.assertTrue(accepted_challenge, "Failed to accept challenge")

    def test_add_battle(self):
        with LogCapture():
            logger = logging.getLogger()
            battle = Battle(log=logger)

        battlemaster = Battlemaster()

        unit_charlie = self._make_unit(is_player=True, level=13)
        unit_omega = self._make_unit(is_player=True, level=13)

        battle.add_combatant(combatant=unit_charlie)
        battle.add_combatant(combatant=unit_omega)

        # Make sure battle was added
        battlemaster.add_battle(battle=battle)

        attacker_weapon = self._make_item(item_type="lizard")
        target_weapon = self._make_item(item_type="spock")

        unit_charlie.equip_item(item=attacker_weapon)
        unit_omega.equip_item(item=target_weapon)

        hit_info = unit_charlie.attack(target=unit_omega)

        battle.add_round(attacker=unit_charlie,
                         target=unit_omega,
                         hit_info=hit_info)

        self.assertEqual(len(battle.rounds), 1)

    def test_cannot_start_battle_with_no_combatants(self):
        with LogCapture():
            logger = logging.getLogger()
            battle = Battle(log=logger)

        battlemaster = Battlemaster()

        """
        Attempting to add a battle with less than two
        combatants should raise ValueError
        """
        try:
            battlemaster.add_battle(battle=battle)
        except ValueError:
            self.assertEqual(len(battlemaster.battles), 0)

    def test_cannot_battle_unit_in_combat(self):
        """
        Units should not be able to start a battle
        if either of them are currently engaged in
        a battle.
        """
        unit_alpha = self._make_unit(level=13)
        unit_bravo = self._make_unit(level=13)
        unit_delta = self._make_unit(level=13)

        # Engage first two targets in battle
        with LogCapture():
            logger = logging.getLogger()
            battle = Battle(log=logger, total_rounds=2)

        battle.add_combatant(unit_alpha)
        battle.add_combatant(unit_bravo)

        self.assertEqual(len(battle.combatants), 2)

        battlemaster = Battlemaster()
        battlemaster.add_battle(battle=battle)

        """
        Make sure we can't add a combatant in battle to
        another battle simultaneously
        """
        with LogCapture():
            logger = logging.getLogger()
            another_battle = Battle(log=logger)

        another_battle.add_combatant(unit_alpha)
        another_battle.add_combatant(unit_bravo)
        another_battle.add_combatant(unit_delta)

        """
        Attempting to do this should not work
        because two of the combatants are in battle.
        """
        battlemaster.add_battle(battle=another_battle)
        self.assertEqual(len(battlemaster.battles), 1)

    def test_cannot_add_dead_combatants(self):
        combatant_1 = self._make_unit(level=13)
        combatant_2 = self._make_unit(level=13)
        with LogCapture():
            logger = logging.getLogger()
            battle = Battle(log=logger)

        combatant_1.kill()

        try:
            battle.add_combatant(combatant_1)
        except InvalidCombatantException:
            battle.add_combatant(combatant_2)
            self.assertEqual(len(battle.combatants), 1)

    def test_add_battle_with_rounds(self):
        combatant_1 = self._make_unit(level=13, is_player=False)
        combatant_2 = self._make_unit(level=13, is_player=False)

        with LogCapture():
            logger = logging.getLogger()
            battle = Battle(log=logger)

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
        attacker_weapon = self._make_item(item_type="rock")
        target_weapon = self._make_item(item_type="scissors")

        combatant_1.equip_item(item=attacker_weapon)
        combatant_2.equip_item(item=target_weapon)

        dungeon = self._make_dungeon()
        battle.start_round(battle=battle,
                           irc="quux",
                           ircutils="quux",
                           ircmsgs="quux",
                           dungeon=dungeon)

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

        combatant_2.equip_item(item=round_2_attacker_weapon)
        combatant_1.equip_item(item=round_2_target_weapon)

        battle.combatants = list(reversed(battle.combatants))

        battle.start_round(battle=battle,
                           irc="quux",
                           ircutils="quux",
                           ircmsgs="quux",
                           dungeon=dungeon)

        self.assertEqual(len(battle.rounds), 2)

        rounds_won_for_combatant_1 = battle.get_rounds_won(
            combatant=combatant_1)
        rounds_won_for_combatant_2 = battle.get_rounds_won(
            combatant=combatant_2)

        self.assertEqual(rounds_won_for_combatant_1, 1)
        self.assertEqual(rounds_won_for_combatant_2, 1)

        """
        Round 3
        """
        round_3_attacker_weapon = self._make_item(item_type="lizard")
        round_3_target_weapon = self._make_item(item_type="spock")

        combatant_1.equip_item(item=round_3_attacker_weapon)
        combatant_2.equip_item(item=round_3_target_weapon)

        battle.combatants = list(reversed(battle.combatants))

        battle.start_round(battle=battle,
                           irc="quux",
                           ircutils="quux",
                           ircmsgs="quux",
                           dungeon=dungeon)

        self.assertEqual(len(battle.rounds), 3)

        rounds_won_for_combatant_1 = battle.get_rounds_won(
            combatant=combatant_1)
        rounds_won_for_combatant_2 = battle.get_rounds_won(
            combatant=combatant_2)

        self.assertEqual(rounds_won_for_combatant_1, 2)
        self.assertEqual(rounds_won_for_combatant_2, 1)

        """
        Make sure we can't exceed max rounds
        """
        cannot_add_round_reason = battle.can_add_round(attacker=combatant_1,
                                                       target=combatant_2)
        self.assertEqual(cannot_add_round_reason, "Cannot add round: maximum rounds reached.")
        self.assertEqual(len(battle.rounds), 3)


if __name__ == '__main__':
    unittest.main()
