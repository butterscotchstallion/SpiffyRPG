"""
SpiffyRPG - Battlemaster
"""
class Battlemaster:
    """
    Handles battles between units
    """
    def __init__(self):
        self.battles = []

    def add_battle(self, **kwargs):
        battle = kwargs["battle"]

        self.battles.append(battle)

    def get_battle_by_combatant(self, **kwargs):
        combatant = kwargs["combatant"]

        for battle in self.battles:
            if battle.combatant_1.id == combatant.id or \
            battle.combatant_2.id == combatant.id:
                return battle

