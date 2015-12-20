# -*- coding: utf-8 -*-
import time
import logging as log

class Dungeon:
    """
    Representation of a dungeon within the world
    """
    def __init__(self, **kwargs):
        #self.schedule = worldbuilder.schedule

        dungeon = kwargs["dungeon"]
        self.units = dungeon["units"]
        self.created_at = time.time()
        self.id = dungeon["id"]
        self.name = dungeon["name"]
        self.description = dungeon["description"]
        self.min_level = dungeon["min_level"]
        self.max_level = dungeon["max_level"]
        self.channel = dungeon["channel"].lower()
        self.max_units = 100

        params = (self.id, self.channel)
        
        log.info("SpiffyRPG: initializing dungeon #%s - %s" % params)

        self.announcer = kwargs["announcer"]

        """
        Apparently scheduling these events can raise
        AssertionError even when you remove them first!
        """
        try:
            """
            self.start_dialogue_timer()
            self.start_spawn_timer()
            self.start_chaos_timer()
            self.start_player_regen_timer()
            """
            pass
        except AssertionError:
            log.error("SpiffyRPG: Error starting periodic events")
        
        if "max_level" in kwargs:
            self.max_level = kwargs["max_level"]

            log.info("SpiffyRPG: creating dungeon with max level %s" % self.max_level)

    def get_boss_units(self):
        return [unit for unit in self.units if unit.is_boss]

    def get_living_necromancer_units(self):
        return [unit for unit in self.units if unit.is_necromancer() \
                and unit.is_alive()]

    def check_dungeon_cleared(self, player):
        units = self.get_living_units()
        num_units = len(units)
        dungeon_cleared = num_units == 0

        log.info("SpiffyRPG: checking if %s has been cleared" % self.name)

        if dungeon_cleared:
            xp_needed_this_level = self.unit_level.get_xp_for_level(player.level)
            xp = int(xp_needed_this_level / 4)

            player.add_experience(xp)

            log.info("SpiffyRPG: adding %s xp to %s" % (xp, player.name))

            self.announcer.dungeon_cleared(dungeon=self,
                                           player=player,
                                           xp=xp)
        else:
            log.info("SpiffyRPG: %s has %s units" % (self.name, num_units))

    def destroy(self):
        self.units = []
        
        log.info("SpiffyRPG: destroying %s" % self.name)
        
        try:
            """
            self.schedule.removeEvent("spawn_timer")
            self.schedule.removeEvent("dialogue_timer")
            self.schedule.removeEvent("chaos_timer")
            """
            self.schedule.removeEvent("player_regen_timer")
        except:
            pass

    def start_player_regen_timer(self):
        log.info("SpiffyRPG: starting player regen interval")

        regen_interval = 300

        self.schedule.addPeriodicEvent(self.regenerate_players,
                                  regen_interval,
                                  name="player_regen_timer")

    def start_chaos_timer(self):
        log.info("SpiffyRPG: starting chaos interval")

        spawn_interval = 300

        self.schedule.addPeriodicEvent(self.herald_chaos,
                                  spawn_interval,
                                  name="chaos_timer")

    def regenerate_players(self):
        """
        When a player dies in a dungeon they stay dead until
        they are regenerated over time
        """
        log.info("SpiffyRPG: regenerating players in %s" % self.name)

        wounded_players = self.get_wounded_players()

        if len(wounded_players) > 0:
            for player in wounded_players:
                total_hp = player.calculate_hp()
                regen_hp = int(total_hp * .25)

                player.regenerate_hp(regen_hp)
        else:
            log.info("SpiffyRPG: no wounded/dead players in %s" % self.name)

    def herald_chaos(self):
        """
        Finds units in the dungeon with the Undead effect.
        In the future this could be expanded to consider
        other effects.
        
        chance_for_chaos = random.randrange(1, 100) < 20
        if not chance_for_chaos:
            return
        """
        
        units = self.get_living_units_with_effect(effect_id=self.effect_id_undead)

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

                log.info("SpiffyRPG: starting chaos battle: %s vs %s" % \
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
                log.info("SpiffyRPG: %s has nobody to party with" % attacker_title)
        else:
            log.info("SpiffyRPG: no undead units!")

    def start_spawn_timer(self):
        log.info("SpiffyRPG: starting monster spawn interval")

        spawn_interval = 300

        self.schedule.addPeriodicEvent(self.check_population,
                                  spawn_interval,
                                  name="spawn_timer",
                                  now=False)

    def check_population(self):
        units = self.get_living_units()
        live_unit_count = len(units)

        if live_unit_count < self.max_units:
            log.info("%s is under population cap %s" % \
            (live_unit_count, self.max_units))

            quantity = self.max_units - live_unit_count

            self.populate(quantity)
        else:
            log.info("SpiffyRPG: [%s] %s units present" % (self.name, live_unit_count))

    def start_dialogue_timer(self):
        log.info("SpiffyRPG: starting monster dialogue interval")

        dialogue_interval = 3600

        self.schedule.addPeriodicEvent(self.random_unit_dialogue,
                                  dialogue_interval,
                                  name="dialogue_timer",
                                  now=False)

    def random_unit_dialogue(self):
        """ Add random chance here """
        units = self.get_living_units()

        if len(units) > 0:
            dialogue_chance = random.randrange(1, 50) < 100

            if dialogue_chance:
                unit = random.choice(units)

                dialogue = unit.dialogue_intro()

                log.info("SpiffyRPG: %s says '%s' to %s" % \
                (unit.get_title(), dialogue, self.channel))

                self.announcer.unit_dialogue(unit, dialogue)
            else:
                log.info("SpiffyRPG: dialoguing by not random enough")
        else:
            log.info("SpiffyRPG: no units in %s, not dialoguing" % self.name)

    def _is_nick_in_channel(self, irc, nick):
        return nick in irc.state.channels[GAME_CHANNEL].users

    def spawn_player_unit(self, **kwargs):
        """
        Spawns a player unit using its user_id
        """
        user_id = kwargs["user_id"]

        unit = self.player_unit_collection.get_player_by_user_id(user_id=user_id)

        if unit is not None:
            """
            Only spawn player units that are actually in the channel
            """
            nick_is_here = self._is_nick_in_channel(self.irc, unit.nick)

            if nick_is_here:
                self.add_unit(unit)

                return unit

    def populate(self, **kwargs):
        """
        Permanent units in this dungeon
        """
        collections = kwargs["collections"]

        self.dungeon_unit_collection = collections["dungeon_unit_collection"]

        dungeon_units = self.dungeon_unit_collection.get_units_by_dungeon_id(self.id)

        for unit in dungeon_units:
            self.add_unit(unit)

        """
        Unlike NPCs, players have a user_id which corresponds to their Limnoria
        user ID
        """
        user_lookup = self.get_user_lookup_from_channel()
        self.player_unit_collection = PlayerUnitCollection(db=self.db)

        """ Get players """
        player_units = self.player_unit_collection.get_players()

        for player in player_units:
            if self._is_nick_in_channel(self.irc, player.nick):
                self.add_unit(player)

    def get_user_lookup_from_channel(self):
        """ 
        Add players to the dungeon by iterating the nick list
        and checking for user ids.
        """
        nicks = self.irc.state.channels[GAME_CHANNEL].users
        ignoreMe = self.collections["ignore_nicks"]
        look_up_user_ids = {}
        look_up_nicks = {}
        player_user_id_list = []

        for nick in nicks:
            if not nick:
                continue

            """ Skip bot nick """
            if nick == self.irc.nick:
                continue

            """ Skip ignored nicks """
            if nick in ignoreMe:
                continue

            try:
                hostmask = self.irc.state.nickToHostmask(nick)
            except KeyError:
                hostmask = None

            user_id = None

            if hostmask is None:
                continue

            try:
                user_id = ircdb.users.getUserId(hostmask)
            except KeyError:
                log.info("SpiffyRPG: %s is not registered." % nick)
            
            """ Registered users only """
            if user_id is None:
                continue

            look_up_nicks[nick] = user_id
            look_up_user_ids[user_id] = nick
            player_user_id_list.append(str(user_id))

        return {
            "look_up_nicks": look_up_nicks,
            "look_up_user_ids": look_up_user_ids,
            "player_user_id_list": player_user_id_list
        }

    def add_unit(self, unit):
        if unit not in self.units:
            items = unit.items

            if unit.is_player:
                log.info("SpiffyRPG: spawning a level %s player %s (%s) with %s HP in %s" % \
                    (unit.level, unit.get_name(), unit.get_title(), unit.get_hp(), self.name))
            else:
                log.info("SpiffyRPG: spawning a level %s NPC: %s (%s) with %s HP in %s" % \
                    (unit.level, unit.get_name(), unit.get_title(), unit.get_hp(), self.name))
            
            self.units.append(unit)
        else:
            log.info("SpiffyRPG: not adding duplicate unit %s" % (unit.get_name()))

    def remove_unit(self, unit):
        units = []

        log.info("SpiffyRPG: [%s] Unit %s#%s died" % (self.name, unit.get_title(), unit.id))

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

    def get_unit_by_name(self, name):
        lower_name = name.lower()

        for unit in self.units:
            unit_name_match = unit.get_name().lower().startswith(lower_name)
            nick_match = unit.nick.lower().startswith(lower_name)

            if unit_name_match or nick_match:
                return unit

    def get_living_unit_by_name(self, name):
        unit = self.get_unit_by_name(name)
        
        if unit.is_alive():
            return unit

    def get_dead_unit_by_name(self, name):
        unit = self.get_unit_by_name(name)
        
        if not unit.is_alive():
            return unit

    def get_living_players(self):
        return [unit for unit in self.units if unit.is_player and unit.is_alive()]

    def get_dead_players(self):
        return [unit for unit in self.units if unit.is_player and not unit.is_alive()]

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