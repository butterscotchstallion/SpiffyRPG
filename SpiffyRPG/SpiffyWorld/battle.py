#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from SpiffyWorld import PlayerAnnouncer


class InvalidCombatantException(ValueError):

    """
    This exception represents scenarios where the combatants
    are the same or dead or some other condition that might
    prevent the combatants from battling.
    """
    def __init__(self, ex_msg):
        self.message = ex_msg
        ValueError.__init__(self, ex_msg)

    def __str__(self):
        return self.message


class CombatStatusException(ValueError):

    """
    This exception occurs when a unit attempts to initiate
    battle with a non-hostile unit (e.g. a unit which has not accepted
    a challenge prior to attacking).
    """
    def __init__(self, ex_msg):
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

    def start_round(self, **kwargs):
        """
        1. Accept battle argument
        2. Attacker.attack
        3. If hit, add round
        4. If miss, target strikes
        5. Add round
        """
        player_announcer = None
        target_announcer = None
        battle = kwargs["battle"]
        irc = kwargs["irc"]
        ircutils = kwargs["ircutils"]
        ircmsgs = kwargs["ircmsgs"]
        dungeon = kwargs["dungeon"]

        if not isinstance(battle, Battle):
            raise ValueError("battle must be instance of Battle")

        attacker, target_unit = battle.combatants

        """
        Attacker -> attack target unit
        """
        hit_info = attacker.attack(target=target_unit)
        is_hit = hit_info["is_hit"]
        item = hit_info["attacker_weapon"]

        if target_unit.is_player:
            target_announcer = PlayerAnnouncer(irc=irc,
                                               destination=target_unit.nick,
                                               ircutils=ircutils,
                                               ircmsgs=ircmsgs)
        if attacker.is_player:
            player_announcer = PlayerAnnouncer(irc=irc,
                                               destination=attacker.nick,
                                               ircutils=ircutils,
                                               ircmsgs=ircmsgs)
        """
        a. Attack lands
        b. Attack misses (target deals damage instead)
        c. Draw
        """
        if hit_info["is_draw"]:
            player_announcer.draw(item_name=item.name,
                                  target_name=target_unit.get_name())
        else:
            """
            Not a draw. Attacker lands hit. Announce damage. Damage
            is already applied by Unit.attack
            """
            if is_hit:
                # Your X hits Y for Z damage
                if player_announcer is not None:
                    player_announcer.damage_dealt(attack_info=hit_info,
                                                  target=target_unit)
                # You take X damage from Y's Z
                if target_announcer is not None:
                    target_announcer.damage_applied(attack_info=hit_info,
                                                    target=target_unit)
            else:
                """
                Attacker missed. Target unit may now attack the attacker.
                """
                target_hit_info = target_unit.attack(target=attacker)

                """
                This should always be a hit, since the attacker hasn't
                equipped another item and the original strike was a miss.
                """
                if target_hit_info["is_hit"]:
                    if player_announcer is not None:
                        player_announcer.damage_applied(attack_info=hit_info,
                                                        target=target_unit)

                    if target_announcer is not None:
                        target_announcer.damage_dealt(attack_info=hit_info,
                                                      target=target_unit)
                else:
                    self.log.warn("ANOMALY: %s's -> %s retaliatioon hit missed!" %
                                  (target_unit.get_name(), attacker.get_name()))
        """
        Announce victory if the target is dead
        """
        if target_unit.is_dead():
            xp_gained = self.get_xp_for_battle(winner=attacker,
                                               loser=target_unit)
            dungeon.announcer.unit_victory(winner=attacker,
                                           loser=target_unit,
                                           hit_info=hit_info,
                                           xp_gained=xp_gained)
            # player announce you have slain X! here
        elif attacker.is_dead():
            xp_gained = self.get_xp_for_battle(winner=target_unit,
                                               loser=attacker)
            dungeon.announcer.unit_victory(winner=target_unit,
                                           loser=attacker,
                                           hit_info=target_hit_info,
                                           xp_gained=xp_gained)

        battle.add_round(attacker=attacker,
                         target=target_unit,
                         hit_info=hit_info)

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
                raise InvalidCombatantException("Not your turn")

            self.last_attacker = attacker

            self.rounds.append(kwargs)
        else:
            ex_msg = "Round maximum reached: %s (%s maximum)" % \
                (current_rounds_length, self.total_rounds)

            # Should this be something else?
            raise InvalidCombatantException(ex_msg)

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

    def get_xp_for_battle(self, **kwargs):
        loser = kwargs["loser"]
        winner = kwargs["winner"]
        xp = int(5 * loser.level)

        if not loser.is_player:
            if loser.is_boss:
                xp *= 4
            else:
                xp *= 3

        if winner.level > (loser.level + 3):
            level_diff = winner.level - loser.level

            xp /= level_diff
        else:
            level_diff = winner.level - loser.level

            """ Level difference must be at least one """
            if level_diff >= 1:
                xp *= level_diff

        return xp
