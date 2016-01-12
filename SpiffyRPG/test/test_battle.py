#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import logging
from testfixtures import LogCapture
from SpiffyWorld import Battle, Battlemaster, ItemGenerator, \
    UnitGenerator, InvalidCombatantException, Dungeon, DungeonAnnouncer
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils


class TestBattle(unittest.TestCase):
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

    def test_start_round(self):
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

        # Lizard poisons Spock
        attacker_weapon = self._make_item(item_type="lizard")
        target_weapon = self._make_item(item_type="spock")

        unit_charlie.equip_item(item=attacker_weapon)
        unit_omega.equip_item(item=target_weapon)
        dungeon = self._make_dungeon()

        try:
            battle.start_round(battle=battle,
                               irc="quux",
                               ircmsgs=ircmsgs,
                               dungeon=dungeon,
                               ircutils=ircutils)

            self.assertFalse(unit_omega.has_full_hp())
            self.assertTrue(unit_charlie.has_full_hp())
            self.assertTrue(len(battle.rounds), 2)
        except InvalidCombatantException:
            """
            In the event of an InvalidCombatantException,
            one of the combatants is dead. Since unit_omega
            was the target of attack we can assume that in
            this scenario that unit is dead. Let's verify that.
            """
            self.assertTrue(unit_omega.is_dead())
            self.assertTrue(unit_charlie.is_alive())

    def test_target_retaliation(self):
        """
        Tests the the following use case:
        1. Attacker strikes
        2. Target is equipped with a counter item type
        3. Attacker should miss and then take damage from
           the target unit's attack
        """
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

        # Target's Scissors cut Attacker's Paper
        attacker_weapon = self._make_item(item_type="paper")
        target_weapon = self._make_item(item_type="scissors")

        unit_charlie.equip_item(item=attacker_weapon)
        unit_omega.equip_item(item=target_weapon)

        dungeon = self._make_dungeon()

        try:
            battle.start_round(battle=battle,
                               irc="quux",
                               ircmsgs="foo",
                               dungeon=dungeon,
                               ircutils="quux")

            """
            Since Unit Omega had scissors equipped they should
            have dealt damage to Unit Charlie
            """
            self.assertFalse(unit_charlie.has_full_hp())
            self.assertTrue(unit_omega.has_full_hp())
            self.assertTrue(len(battle.rounds), 2)
        except InvalidCombatantException, e:
            """
            In the event of an InvalidCombatantException,
            one of the combatants is dead. Since unit_omega
            was the target of attack we can assume that in
            this scenario that unit is dead. Let's verify that.
            """
            ex_msg = str(e)
            self.assertTrue("dead" in ex_msg)
            self.assertTrue(unit_charlie.is_dead())
            self.assertTrue(unit_omega.is_alive())

    def test_not_your_turn(self):
        """
        Unit should not be able to attack twice in a row
        """
        with LogCapture():
            logger = logging.getLogger()
            battle = Battle(log=logger)

        battlemaster = Battlemaster()

        unit_charlie = self._make_unit(is_player=True, level=99)
        unit_omega = self._make_unit(is_player=True, level=13)

        battle.add_combatant(combatant=unit_charlie)
        battle.add_combatant(combatant=unit_omega)

        # Make sure battle was added
        battlemaster.add_battle(battle=battle)

        # Target's Scissors cut Attacker's Paper
        attacker_weapon = self._make_item(item_type="lizard")
        target_weapon = self._make_item(item_type="spock")

        unit_charlie.equip_item(item=attacker_weapon)
        unit_omega.equip_item(item=target_weapon)

        dungeon = self._make_dungeon()

        try:
            battle.start_round(battle=battle,
                               irc="quux",
                               ircmsgs="foo",
                               dungeon=dungeon,
                               ircutils="quux")

            """
            unit_charle's Lizard poisons unit_omega's Spock
            """
            self.assertFalse(unit_omega.has_full_hp())
            self.assertTrue(unit_charlie.has_full_hp())
            self.assertTrue(len(battle.rounds), 2)

            """
            Try to attack again (should fail)
            """
            battle.start_round(battle=battle,
                               irc="quux",
                               ircmsgs="foo",
                               dungeon=dungeon,
                               ircutils="quux")

            # No round should have been added
            self.assertTrue(len(battle.rounds), 2)

        except InvalidCombatantException, e:
            """
            In the event of an InvalidCombatantException,
            one of the combatants is dead. Since unit_omega
            was the target of attack we can assume that in
            this scenario that unit is dead. Let's verify that.
            """
            ex_msg = str(e)
            self.assertEqual(ex_msg, "Not your turn")


if __name__ == '__main__':
    unittest.main()
