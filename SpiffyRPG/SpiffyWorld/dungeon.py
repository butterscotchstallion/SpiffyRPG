#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import random

GAME_CHANNEL = "#spiffyrpg"


class Dungeon:

    """
    Representation of a dungeon within the world
    """

    def __init__(self, **kwargs):
        dungeon = kwargs["dungeon"]
        self.units = []
        self.created_at = time.time()
        self.id = dungeon["id"]
        self.name = dungeon["name"]
        self.description = dungeon["description"]
        self.min_level = dungeon["min_level"]
        self.max_level = dungeon["max_level"]
        self.channel = dungeon["channel"].lower()
        self.max_units = 100
        self.log = kwargs["log"]

        params = (self.id, self.channel)

        self.log.info("SpiffyRPG: initializing dungeon #%s - %s" % params)

        self.announcer = kwargs["announcer"]

        if "max_level" in kwargs:
            self.max_level = kwargs["max_level"]

            self.log.info("SpiffyRPG: creating dungeon with max level %s" %
                          self.max_level)

    def get_boss_units(self):
        return [unit for unit in self.units if unit.is_boss]

    def get_living_necromancer_units(self):
        return [unit for unit in self.units if unit.is_necromancer() and
                unit.is_alive()]

    def check_dungeon_cleared(self, player):
        units = self.get_living_units()
        num_units = len(units)
        dungeon_cleared = num_units == 0

        self.log.info("SpiffyRPG: checking if %s has been cleared" % self.name)

        if dungeon_cleared:
            xp_needed_this_level = self.unit_level.get_xp_for_level(
                player.level)
            xp = int(xp_needed_this_level / 4)

            player.add_experience(xp)

            self.log.info("SpiffyRPG: adding %s xp to %s" % (xp, player.name))

            self.announcer.dungeon_cleared(dungeon=self,
                                           player=player,
                                           xp=xp)
        else:
            self.log.info("SpiffyRPG: %s has %s units" % (self.name, num_units))

    def start_player_regen_timer(self):
        self.log.info("SpiffyRPG: starting player regen interval")

        regen_interval = 300

        self.schedule.addPeriodicEvent(self.regenerate_players,
                                       regen_interval,
                                       name="player_regen_timer")

    def start_chaos_timer(self):
        self.log.info("SpiffyRPG: starting chaos interval")

        spawn_interval = 300

        self.schedule.addPeriodicEvent(self.herald_chaos,
                                       spawn_interval,
                                       name="chaos_timer")

    def regenerate_players(self):
        """
        When a player dies in a dungeon they stay dead until
        they are regenerated over time
        """
        self.log.info("SpiffyRPG: regenerating players in %s" % self.name)

        wounded_players = self.get_wounded_players()

        if len(wounded_players) > 0:
            for player in wounded_players:
                total_hp = player.calculate_hp()
                regen_hp = int(total_hp * .25)

                player.regenerate_hp(regen_hp)
        else:
            self.log.info("SpiffyRPG: no wounded/dead players in %s" % self.name)

    def herald_chaos(self):
        """
        Finds units in the dungeon with the Undead effect.
        In the future this could be expanded to consider
        other effects.

        chance_for_chaos = random.randrange(1, 100) < 20
        if not chance_for_chaos:
            return
        """

        units = self.get_living_units_with_effect(
            effect_id=self.effect_id_undead)

        if len(units) > 0:
            """ Now find a living unit in the dungeon for an opponent """
            alive = self.get_living_units()
            attacker = random.choice(units)
            """ Find a living unit that is not the undead attacker """
            alive_without_attacker = []

            for a in alive:
                if a.id != attacker.id:
                    alive_without_attacker.append(a)

            attacker_title = attacker.get_title()

            if len(alive_without_attacker) > 0:
                target = random.choice(alive_without_attacker)

                self.log.info("SpiffyRPG: starting chaos battle: %s vs %s" %
                              (attacker_title, target.get_title()))

                dialogue = attacker.get_zombie_dialogue()
                self.announcer.dungeon_undead_attacker(attacker=attacker,
                                                       target=target,
                                                       dungeon=self,
                                                       dialogue=dialogue)

                self.battle.add_party_member(attacker)
                self.battle.add_party_member(target)
                self.battle.start()
            else:
                self.log.info("SpiffyRPG: %s has nobody to party with" %
                              attacker_title)
        else:
            self.log.info("SpiffyRPG: no undead units!")

    def random_unit_dialogue(self):
        """ Add random chance here """
        units = self.get_living_units()

        if len(units) > 0:
            dialogue_chance = random.randrange(1, 50) < 100

            if dialogue_chance:
                unit = random.choice(units)

                dialogue = unit.dialogue_intro()

                self.log.info("SpiffyRPG: %s says '%s' to %s" %
                              (unit.get_title(), dialogue, self.channel))

                self.announcer.unit_dialogue(unit, dialogue)
            else:
                self.log.info("SpiffyRPG: dialoguing by not random enough")
        else:
            self.log.info("SpiffyRPG: no units in %s, not dialoguing" % self.name)

    def _is_nick_in_channel(self, irc, nick):
        return nick in irc.state.channels[GAME_CHANNEL].users

    def spawn_player_unit(self, **kwargs):
        """
        Spawns a player unit using its user_id
        """
        unit = kwargs["unit"]

        if unit is not None:
            self.add_unit(unit)

    def add_unit(self, unit):
        if unit not in self.units:
            params = (unit.level, unit.get_name(), unit.get_title(),
                      unit.get_hp(), self.name)

            msg_prefix = "SpiffyRPG: spawning a level "
            msg = msg_prefix

            if unit.is_player:
                msg += "%s player %s (%s) with %s HP in %s" % params
            else:
                msg += "%s NPC: %s (%s) with %s HP in %s" % params

            self.log.info(msg)

            self.units.append(unit)
        else:
            self.log.info("SpiffyRPG: not adding duplicate unit %s" %
                          (unit.get_name()))

    def remove_unit(self, unit):
        units = []

        for u in self.units:
            if unit.id != u.id:
                units.append(u)

        self.units = units

    def get_unit_by_user_id(self, user_id):
        for unit in self.units:
            if unit.user_id == user_id:
                return unit

    def get_player_by_user_id(self, user_id):
        for unit in self.units:
            if unit.is_player and unit.user_id == user_id:
                return unit

    def unit_name_matches(self, unit_name_1, unit_name_2):
        lower_unit_1_name = unit_name_1.lower()
        lower_unit_2_name = unit_name_2.lower()
        unit_name_match = lower_unit_1_name.startswith(lower_unit_2_name)

        return unit_name_match

    def unit_nick_matches(self, unit_nick_1, unit_nick_2):
        lower_unit_1_nick = unit_nick_1.lower()
        lower_unit_2_nick = unit_nick_2.lower()
        nick_match = lower_unit_1_nick.startswith(lower_unit_2_nick)

        return nick_match

    def get_unit_by_name(self, name):
        for unit in self.units:
            unit_name_matches = self.unit_name_matches(unit.get_name(), name)
            nick_matches = self.unit_nick_matches(unit.nick, name)

            if unit_name_matches or nick_matches:
                return unit

    def get_living_unit_by_name(self, target_unit_name):
        living_units = [unit for unit in self.units if unit.is_alive()]

        for unit in living_units:
            unit_name_matches = self.unit_name_matches(
                unit.get_name(), target_unit_name)
            nick_matches = self.unit_nick_matches(unit.nick, target_unit_name)

            if unit_name_matches or nick_matches:
                return unit

    def get_dead_unit_by_name(self, target_unit_name):
        dead_units = [unit for unit in self.units if unit.is_dead()]

        for unit in dead_units:
            unit_name_matches = self.unit_name_matches(
                unit.get_name(), target_unit_name)
            nick_matches = self.unit_nick_matches(unit.nick, target_unit_name)

            if unit_name_matches or nick_matches:
                return unit

    def get_living_players(self):
        return [unit for unit in self.units
                if unit.is_player and unit.is_alive()]

    def get_dead_players(self):
        return [unit for unit in self.units
                if unit.is_player and not unit.is_alive()]

    def get_living_hostiles_at_stage(self, **kwargs):
        stage = kwargs["stage"]
        hostiles = []

        for unit in self.units:
            is_hostile = not unit.is_player and unit.is_hostile()
            alive = unit.is_alive()
            same_stage = unit.get_stage_by_level(level=unit.level) == stage

            if is_hostile and alive and same_stage:
                hostiles.append(unit)

        return hostiles

    def get_wounded_players(self):
        players = []

        for unit in self.units:
            wounded_or_dead = (unit.is_below_max_hp() or not unit.is_alive())

            if unit.is_player and wounded_or_dead:
                players.append(unit)

        return players

    def get_living_units_with_effect(self, **kwargs):
        alive = self.get_living_units()
        units = []

        for unit in alive:
            for effect in unit.effects:
                if effect["id"] == kwargs["effect_id"]:
                    units.append(unit)

        return units

    def get_dead_units(self):
        dead = [unit for unit in self.units if not unit.is_alive()]

        if len(dead) > 0:
            dead = sorted(dead, key=lambda x: x.level, reverse=True)

        return dead

    def get_living_units(self):
        alive = [unit for unit in self.unit if unit.is_alive()]

        if len(alive) > 0:
            alive = sorted(alive, key=lambda x: x.level, reverse=True)

        return alive

    def get_unit_status_distribution(self):
        dist = {
            "players": {
                "living": 0,
                "dead": 0,
                "undead": 0
            },
            "npc": {
                "hostile": {
                    "living": 0,
                    "dead": 0,
                    "undead": 0
                },
                "friendly": {
                    "living": 0,
                    "dead": 0,
                    "undead": 0
                }
            }
        }

        for unit in self.units:
            if unit.is_player:
                if unit.is_alive():
                    if unit.is_undead():
                        dist["players"]["undead"] += 1

                    dist["players"]["living"] += 1
                else:
                    dist["players"]["dead"] += 1
            else:
                if unit.is_hostile():
                    if unit.is_alive():
                        if unit.is_undead():
                            dist["npc"]["hostile"]["undead"] += 1

                        dist["npc"]["hostile"]["living"] += 1
                    else:
                        dist["npc"]["hostile"]["dead"] += 1
                else:
                    if unit.is_alive():
                        if unit.is_undead():
                            dist["npc"]["friendly"]["undead"] += 1

                        dist["npc"]["friendly"]["living"] += 1
                    else:
                        dist["npc"]["friendly"]["dead"] += 1

        return dist

    def get_units(self):
        units = self.units

        if len(units) > 0:
            units = sorted(units, key=lambda x: x.level, reverse=True)

        return units
