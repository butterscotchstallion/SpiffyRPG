#!/usr/bin/env python
# -*- coding: utf-8 -*-
from SpiffyWorld import Battle, InvalidCombatantException


class Battlemaster:

    """
    Handles battles between units
    """

    def __init__(self):
        self.battles = []
        self.challenges = {}

    def add_battle(self, **kwargs):
        battle = kwargs["battle"]

        if not isinstance(battle, Battle):
            raise ValueError("battle must be an instance of Battle")

        if len(battle.combatants) < 2:
            raise ValueError("Battle must have at least two combatants")

        for unit in battle.combatants:
            if self.is_combatant_in_battle(combatant=unit):
                ex_msg = "Unit %s is currently engaged in battle!" % \
                    unit.get_name()
                raise InvalidCombatantException(ex_msg)

        self.battles.append(battle)

    def has_accepted_challenge(self, **kwargs):
        attacker = kwargs["attacker"]

        return attacker.id not in self.challenges

    def accept_challenge_from_target(self, **kwargs):
        target = kwargs["target"]

        for challenge in self.challenges:
            if self.challenges[challenge] == target.id:
                del self.challenges[challenge]

    def issue_challenge(self, **kwargs):
        attacker = kwargs["attacker"]
        target = kwargs["target"]

        attacker_in_battle = self.is_combatant_in_battle(combatant=attacker)

        if attacker_in_battle:
            raise InvalidCombatantException("%s is currently in battle!"
                                            % attacker.get_name())

        target_in_battle = self.is_combatant_in_battle(combatant=target)

        if target_in_battle:
            raise InvalidCombatantException("%s is currently in battle!"
                                            % target.get_name())

        self.challenges[attacker.id] = target

    def is_combatant_in_battle(self, **kwargs):
        combatant = kwargs["combatant"]
        is_in_battle = self.get_battle_by_combatant(combatant=combatant)

        return is_in_battle is not None

    def get_battle_by_combatant(self, **kwargs):
        combatant = kwargs["combatant"]

        for battle in self.battles:
            for combatant in battle.combatants:
                if combatant.id == combatant.id:
                    return battle
