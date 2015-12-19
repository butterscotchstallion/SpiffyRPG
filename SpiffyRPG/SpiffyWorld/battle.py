# -*- coding: utf-8 -*-
import time

class Battle:


    """
    A battle between two units
    """
    def __init__(self, **kwargs):
        self.rounds = []
        self.combatants = []
        self.total_rounds = kwargs["total_rounds"]
        self.created_at = time.time()

    def __eq__(self, other):
        created_at_match = self.created_at == other.created_at

        if not created_at_match:
            return False

        total_rounds_match = self.total_rounds == other.total_rounds

        if not total_rounds_match:
            return False

        rounds_match = self.rounds == other.rounds

        if not rounds_match:
            return False

        combatant_match = True

        # Compare combatants
        for combatant in self.combatants:
            if combatant not in other.combatants:
                combatant_match = False
                break

        return combatant_match

    def add_round(self, **kwargs):
        current_rounds_length = len(self.rounds)

        if current_rounds_length < self.total_rounds:
            self.rounds.append(kwargs)
        else:
            raise ValueError("Round maximum reached: %s (%s maximum)" % \
                            (current_rounds_length, self.total_rounds))

    def add_combatant(self, combatant):
        if combatant not in self.combatants and combatant.is_alive():
            self.combatants.append(combatant)

    def get_rounds_won(self, **kwargs):
        combatant = kwargs["combatant"]
        rounds_won = 0

        for bround in self.rounds:
            id_match = bround["attacker"].id == combatant.id
            is_hit = bround["hit_info"]["is_hit"]

            if id_match and is_hit:
                rounds_won += 1

        return rounds_won
