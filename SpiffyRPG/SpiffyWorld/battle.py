# -*- coding: utf-8 -*-
import time

class InvalidCombatantException(ValueError):
    """
    This exception represents scenarios where the combatants
    are the same or dead or some other condition that might
    prevent the combatants from battling.
    """
    def __init__(self, ex_msg):
        ex_msg = "One or more combatants is not valid."
        ValueError.__init__(self, ex_msg)

class Battle:
    """
    A battle between two units
    """
    def __init__(self, **kwargs):
        total_rounds = 3

        if "total_rounds" in kwargs:
            total_rounds = kwargs["total_rounds"]

        self.rounds = []
        self.combatants = []
        self.total_rounds = total_rounds
        self.created_at = time.time()
        self.last_attacker = None

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
        attacker = kwargs["attacker"]
        target = kwargs["target"]

        if current_rounds_length < self.total_rounds:
            """
            Make sure we're not trying to add rounds when
            either of the combatants are dead
            """
            if not attacker.is_alive():
                ex_msg = "Cannot add round: Unit %s is dead." % \
                          attacker.get_name()
                raise InvalidCombatantException(ex_msg)

            if not target.is_alive():
                ex_msg = "Cannot add round: Unit %s is dead." % \
                          target.get_name()
                raise InvalidCombatantException(ex_msg)

            """
            Check to make sure units are not attacking twice
            in a row
            """
            same_attacker = False
            attacker_exists = self.last_attacker is not None

            if attacker_exists:
                id_match = attacker.id == self.last_attacker.id
                same_attacker = attacker_exists and id_match

            if same_attacker:
                raise ValueError("Not your turn")

            self.last_attacker = attacker

            self.rounds.append(kwargs)
        else:
            raise ValueError("Round maximum reached: %s (%s maximum)" %
                             (current_rounds_length, self.total_rounds))

    def add_combatant(self, combatant):
        if not combatant.is_alive():
            params = (combatant.name, combatant.get_hp())
            msg = "Cannot add dead unit to battle: %s (%s HP)" % params
            raise InvalidCombatantException(msg)

        if combatant not in self.combatants:
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

