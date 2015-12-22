# -*- coding: utf-8 -*-
from SpiffyWorld import Battle, InvalidCombatantException

class Battlemaster:
    """
    Handles battles between units
    """
    def __init__(self):
        self.battles = []

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
