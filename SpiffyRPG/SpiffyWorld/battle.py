# -*- coding: utf-8 -*-
class Battle:
    """
    A battle between two units
    """
    def __init__(self, **kwargs):
        self.rounds = []
        self.combatant_1 = kwargs["combatant_1"]
        self.combatant_2 = kwargs["combatant_2"]
        self.total_rounds = kwargs["total_rounds"]

    def add_round(self, **kwargs):
        if len(self.rounds) < self.total_rounds and kwargs not in self.rounds:
            self.rounds.append(kwargs)

    def get_rounds_won(self, **kwargs):
        combatant = kwargs["combatant"]
        rounds_won = 0

        for bround in self.rounds:
            id_match = bround["attacker"].id == combatant.id
            is_hit = bround["hit_info"]["is_hit"]

            if id_match and is_hit:
                rounds_won += 1

        return rounds_won
