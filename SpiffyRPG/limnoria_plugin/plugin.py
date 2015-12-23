#!/usr/bin/env python
# -*- coding: utf-8 -*-
###
# Copyright (c) 2015, butterscotchstallion
# All rights reserved.
#
#
###
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.ircmsgs as ircmsgs
import supybot.log as log
import supybot.ircdb as ircdb
import supybot.conf as conf
import supybot.dbi as dbi
import supybot.schedule as schedule
import random
import re
import time
from datetime import datetime

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('SpiffyRPG')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x

SQLITE_DB_FILENAME = "SpiffyRPG.sqlite3.db"
GAME_CHANNEL = "#SpiffyRPG"


class SqliteSpiffyRPGDB(dbi.DB):

    """
    This class manages the database used in SpiffyRPG
    """
    db = None

    def __init__(self, filename):
        """ For whatever reason this has to be here """
        self.channel = GAME_CHANNEL

    def _get_db(self):
        try:
            import sqlite3

            filename = conf.supybot.directories.data.dirize(SQLITE_DB_FILENAME)

            db = sqlite3.connect(filename, check_same_thread=False)
            db.row_factory = sqlite3.Row

            return db
        except e:
            log.info("SpiffyRPGDB: problem connecting to db %s" % e)

SpiffyRPGDB = plugins.DB("SpiffyRPG", {"sqlite3": SqliteSpiffyRPGDB})


class SpiffyRPG(callbacks.Plugin):

    """A gluten-free IRC RPG"""
    threaded = True

    def __init__(self, irc):
        self.__parent = super(SpiffyRPG, self)
        self.__parent.__init__(irc)
        self.irc = irc
        self.welcome_messages = {}
        self.welcome_message_cooldown_in_seconds = 600

        db_lib = SpiffyRPGDB()
        self.db = db_lib._get_db()
        self.unit_level = SpiffyUnitLevel()
        self.unit_db = SpiffyUnitDB(db=self.db)
        self.classes = self.unit_db.get_unit_types()

        ignore_nicks = self.registryValue("ignoreNicks")

        self.SpiffyWorld = SpiffyWorld(irc=self.irc,
                                       db=self.db,
                                       ignore_nicks=ignore_nicks,
                                       unit_db=self.unit_db)

        self.SpiffyWorld.start()

    def _get_user_id(self, irc, prefix):
        try:
            return ircdb.users.getUserId(prefix)
        except KeyError:
            pass

    def _get_user_id_by_irc_and_msg(self, irc, msg):
        user_id = None

        if hasattr(msg, "prefix"):
            user_id = self._get_user_id(irc, msg.prefix)
        elif hasattr(msg, "nick"):
            hostmask = irc.state.nickToHostmask(msg.nick)
            user_id = self._get_user_id(irc, hostmask)

        return user_id

    def _is_alphanumeric_with_dashes(self, input):
        return re.match('^[\w-]+$', input) is not None

    def _is_valid_char_name(self, char_name):
        return len(char_name) > 1 and len(char_name) <= 16 \
            and self._is_alphanumeric_with_dashes(char_name)

    def _is_valid_char_class(self, type):
        for id, unit_type_name in self.unit_types:
            if unit_type_name.lower() == type.lower():
                return True

    def _is_nick_in_channel(self, irc, nick):
        return nick in irc.state.channels[GAME_CHANNEL].users

    def _get_character_class_list(self):
        class_list = []

        for c in self.classes:
            class_list.append(ircutils.bold(c["name"]))

        return ", ".join(class_list)

    def _get_unit_type_id_by_name(self, type):
        for c in self.unit_types:
            if c["name"].lower() == type.lower():
                return c["id"]

    def _init_world(self):
        """
        We need the nicks in the channel in order to initialize
        the world.
        """
        self.SpiffyWorld.start()

    def _get_dungeon_and_user_id(self, irc, msg):
        """
        Get user_id, dungeon id, and user. This occurs before
        almost every user interaction
        """
        user_id = self._get_user_id_by_irc_and_msg(irc, msg)

        if user_id is None:
            log.info("SpiffyRPG: problem finding user_id for %s" % msg)

        dungeon = self.SpiffyWorld.get_dungeon_by_channel(GAME_CHANNEL)

        if dungeon is not None and user_id is not None:
            player = dungeon.get_unit_by_user_id(user_id)

            if player is not None:
                battle = SpiffyBattle(db=self.db,
                                      irc=irc,
                                      destination=GAME_CHANNEL,
                                      dungeon=dungeon)
                unick = msg.nick
                pnick = player.nick
                attacker_announcer = SpiffyPlayerAnnouncer(irc=irc,
                                                           destination=unick)
                target_announcer = SpiffyPlayerAnnouncer(irc=irc,
                                                         destination=pnick)

                battle.set_challenger_announcer(attacker_announcer)
                battle.set_opponent_announcer(target_announcer)

                return {
                    "dungeon": dungeon,
                    "player": player,
                    "battle": battle
                }

    """
    Game commands
    """
    def inspect(self, irc, msg, args, user, target):
        """
        Inspects a unit or item
        """
        dungeon_info = self._get_dungeon_and_user_id(irc, msg)

        if dungeon_info is not None:
            player = dungeon_info["player"]
            dungeon = dungeon_info["dungeon"]

            if not target:
                target = msg.nick

            unit = dungeon.get_unit_by_name(target)

            if unit is not None:
                dungeon.announcer.inspect_target(player=player,
                                                 unit=unit,
                                                 dungeon=dungeon,
                                                 irc=irc)
            else:
                dungeon.announcer.look_failure(player=player,
                                               dungeon=dungeon,
                                               irc=irc)

    inspect = wrap(inspect, ["user", optional("text")])

    def look(self, irc, msg, args, user):
        """
        Look around for anything of note nearby
        """
        dungeon_info = self._get_dungeon_and_user_id(irc, msg)

        if dungeon_info is not None:
            dungeon = dungeon_info["dungeon"]
            player = dungeon_info["player"]

            stage = player.get_stage_by_level(level=player.level)
            units = dungeon.get_living_hostiles_at_stage(stage=stage)

            dungeon.announcer.look(dungeon=dungeon,
                                   player=player,
                                   units=units,
                                   irc=irc,
                                   is_seance=False)

    look = wrap(look, ["user"])

    def use(self, irc, msg, args, user, item_name):
        """
        use <item name> - Use an item in your inventory.
        """
        dungeon_info = self._get_dungeon_and_user_id(irc, msg)

        if dungeon_info is not None:
            player = dungeon_info["player"]

            inventory_item = player.get_item_from_inventory_by_name(
                item_name=item_name)

            if inventory_item is not None:
                item_used_successfully = player.use_item(item=inventory_item)
                pnick = player.nick
                player_announcer = SpiffyPlayerAnnouncer(irc=irc,
                                                         destination=pnick)

                if item_used_successfully is not None:
                    player_announcer.use_item(item=inventory_item,
                                              irc=irc)
                else:
                    irc.error(
                        "That item is not usable or has no charges left.")
            else:
                irc.error("Item not found!")

    use = wrap(use, ["user", "text"])

    def seance(self, irc, msg, args, user):
        """
        Attempt to communicate with the spirits of the dead
        """
        dungeon_info = self._get_dungeon_and_user_id(irc, msg)

        if dungeon_info is not None:
            dungeon = dungeon_info["dungeon"]
            player = dungeon_info["player"]

            dead = dungeon.get_dead_units()

            if len(dead) > 0:
                dungeon.announcer.look(dungeon=dungeon,
                                       player=player,
                                       units=dead,
                                       irc=irc,
                                       is_seance=True)
            else:
                dungeon.announcer.seance_failed(dungeon=dungeon,
                                                player=player)

    seance = wrap(seance, ["user"])

    def smap(self, irc, msg, args, user):
        """
        Examine your map to see where you are
        """
        dungeon_info = self._get_dungeon_and_user_id(irc, msg)

        if dungeon_info is not None:
            dungeon = dungeon_info["dungeon"]
            player = dungeon_info["player"]

            dungeon.announcer.open_map(dungeon=dungeon,
                                       player=player)
        else:
            irc.error("You seem to have misplaced your map.")

    smap = wrap(smap, ["user"])

    def title(self, irc, msg, args, user, title):
        """
        title <new title> - sets a new title for your character. \
        Maximum 16 characters
        """
        dungeon_info = self._get_dungeon_and_user_id(irc, msg)

        if dungeon_info is not None:
            dungeon = dungeon_info["dungeon"]
            player = dungeon_info["player"]

            player.set_title(title[0:16])

            dungeon.announcer.unit_info(unit=player, irc=irc, dungeon=dungeon)

    title = wrap(title, ["user", "text"])

    def rock(self, irc, msg, args, user, target):
        """
        rock <target> - attacks your target with a Rock type weapon
        """
        dungeon_info = self._get_dungeon_and_user_id(irc, msg)

        if dungeon_info is not None:
            dungeon = dungeon_info["dungeon"]
            player = dungeon_info["player"]
            unit = dungeon.get_living_unit_by_name(target)

            log.info("Attempting to rock %s" % unit)

            if unit is not None:
                equip_ok = player.equip_item_by_type(item_type="rock")

                if equip_ok:
                    can_battle = player.can_battle_unit(unit=unit)

                    if can_battle is True:
                        """
                        The target unit of the attack now equips a weapon!
                        """
                        if not unit.is_player:
                            unit.equip_random_weapon(avoid_weapon_type="rock")

                        battle = dungeon_info["battle"]
                        battle.add_party_member(player)
                        battle.add_party_member(unit)
                        battle.start()
                    else:
                        irc.error("You can't attack that. %s" % can_battle)
                else:
                    dungeon.announcer.unit_death(unit=player)
        else:
            irc.error("That target appears to be dead or non-existent")

    rock = wrap(rock, ["user", "text"])

    def paper(self, irc, msg, args, user, target):
        """
        paper <target> - attacks your target with a Paper type weapon
        """
        dungeon_info = self._get_dungeon_and_user_id(irc, msg)

        if dungeon_info is not None:
            dungeon = dungeon_info["dungeon"]
            player = dungeon_info["player"]
            unit = dungeon.get_living_unit_by_name(target)

            if unit is not None:
                equip_ok = player.equip_item_by_type(item_type="paper")

                if equip_ok:
                    can_battle = player.can_battle_unit(unit=unit)

                    if can_battle is True:
                        """
                        The target unit of the attack now equips a weapon!
                        """
                        if not unit.is_player:
                            unit.equip_random_weapon(avoid_weapon_type="paper")

                        battle = dungeon_info["battle"]
                        battle.add_party_member(player)
                        battle.add_party_member(unit)
                        battle.start()
                    else:
                        irc.error("You can't attack that. %s" % can_battle)
                else:
                    dungeon.announcer.unit_death(unit=player)
        else:
            irc.error("That target appears to be dead or non-existent")

    paper = wrap(paper, ["user", "text"])

    def scissors(self, irc, msg, args, user, target):
        """
        scissors <target> - attacks your target with a Scissors type weapon
        """
        dungeon_info = self._get_dungeon_and_user_id(irc, msg)

        if dungeon_info is not None:
            dungeon = dungeon_info["dungeon"]
            player = dungeon_info["player"]
            unit = dungeon.get_living_unit_by_name(target)

            if unit is not None:
                equip_ok = player.equip_item_by_type(item_type="scissors")

                if equip_ok:
                    can_battle = player.can_battle_unit(unit=unit)

                    if can_battle is True:
                        """
                        The target unit of the attack now equips a weapon!
                        """
                        if not unit.is_player:
                            unit.equip_random_weapon(
                                avoid_weapon_type="scissors")

                        battle = dungeon_info["battle"]
                        battle.add_party_member(player)
                        battle.add_party_member(unit)
                        battle.start()
                    else:
                        irc.error("You can't attack that. %s" % can_battle)
                else:
                    dungeon.announcer.unit_death(unit=player)
        else:
            irc.error("That target appears to be dead or non-existent")

    scissors = wrap(scissors, ["user", "text"])

    def lizard(self, irc, msg, args, user, target):
        """
        lizard <target> - attacks your target with a Lizard type weapon
        """
        dungeon_info = self._get_dungeon_and_user_id(irc, msg)

        if dungeon_info is not None:
            dungeon = dungeon_info["dungeon"]
            player = dungeon_info["player"]
            unit = dungeon.get_living_unit_by_name(target)

            if unit is not None:
                equip_ok = player.equip_item_by_type(item_type="lizard")

                if equip_ok:
                    can_battle = player.can_battle_unit(unit=unit)

                    if can_battle is True:
                        """
                        The target unit of the attack now equips a weapon!
                        """
                        if not unit.is_player:
                            unit.equip_random_weapon(
                                avoid_weapon_type="lizard")

                        battle = dungeon_info["battle"]
                        battle.add_party_member(player)
                        battle.add_party_member(unit)
                        battle.start()
                    else:
                        irc.error("You can't attack that. %s" % can_battle)
                else:
                    dungeon.announcer.unit_death(unit=player)
        else:
            irc.error("That target appears to be dead or non-existent")

    lizard = wrap(lizard, ["user", "text"])

    def spock(self, irc, msg, args, user, target):
        """
        spock <target> - attacks your target with a Spock type weapon
        """
        dungeon_info = self._get_dungeon_and_user_id(irc, msg)

        if dungeon_info is not None:
            dungeon = dungeon_info["dungeon"]
            player = dungeon_info["player"]
            unit = dungeon.get_living_unit_by_name(target)

            if unit is not None:
                equip_ok = player.equip_item_by_type(item_type="spock")

                if equip_ok:
                    can_battle = player.can_battle_unit(unit=unit)

                    if can_battle is True:
                        """
                        The target unit of the attack now equips a weapon!
                        """
                        if not unit.is_player:
                            unit.equip_random_weapon(avoid_weapon_type="spock")

                        battle = dungeon_info["battle"]
                        battle.add_party_member(player)
                        battle.add_party_member(unit)
                        battle.start()
                    else:
                        irc.error("You can't attack that. %s" % can_battle)
                else:
                    dungeon.announcer.unit_death(unit=player)
        else:
            irc.error("That target appears to be dead or non-existent")

    spock = wrap(spock, ["user", "text"])

    def sup(self, irc, msg, args, user, target):
        """
        Greet a target
        """
        dungeon_info = self._get_dungeon_and_user_id(irc, msg)

        if dungeon_info is not None:
            dungeon = dungeon_info["dungeon"]
            player = dungeon_info["player"]
            unit = dungeon.get_living_unit_by_name(target)

            msg = "SpiffyRPG: interaction failed: unit is %s and " % unit
            msg += "player is %s" % player

            if unit is not None:
                dialogue = unit.dialogue_sup()

                if dialogue is not None:
                    dungeon.announcer.unit_dialogue(unit, dialogue)
            else:
                log.error(msg)

    sup = wrap(sup, ["user", "text"])

    def accept(self, irc, msg, args, user, target_nick):
        """
        accept <nick> - Accepts a challenge from another player
        """
        dungeon_info = self._get_dungeon_and_user_id(irc, msg)

        if dungeon_info is not None:
            dungeon = dungeon_info["dungeon"]
            player = dungeon_info["player"]
            combatant = dungeon.get_living_unit_by_name(target_nick)

            if combatant is not None:
                player.add_battle(combatant=combatant, rounds=3)
                combatant.add_battle(combatant=player, rounds=3)
                pnick = player.nick
                player_announcer = SpiffyPlayerAnnouncer(irc=irc,
                                                         destination=pnick)

                player_announcer.challenge_accepted(combatant=combatant)

                dungeon.announcer.challenge_accepted(attacker=player,
                                                     target=combatant)
            else:
                irc.error("That target seems to be dead or non-existent.")

    accept = wrap(accept, ["user", "something"])

    def challenge(self, irc, msg, args, user, unit_name):
        """
        challenge <target> - Challenge target to battle
        """

        """
        1. Get player and unit
        2. Get last battle for player and target and make sure
           both are not None
        3. The unit that did not go last is the attacker, or the challenger

        """
        dungeon_info = self._get_dungeon_and_user_id(irc, msg)

        if dungeon_info is not None:
            dungeon = dungeon_info["dungeon"]
            player = dungeon_info["player"]
            combatant = dungeon.get_living_unit_by_name(unit_name)

            if combatant is not None:
                can_battle = player.can_battle_unit(unit=combatant)

                if can_battle is not True:
                    irc.error("You can't challenge that: %s" % can_battle)
                    return

                last_battle = player.get_last_incomplete_battle(
                    combatant=combatant)

                """
                If there is an existing battle, they cannot challenge
                """
                if last_battle is not None:
                    irc.error("You're already battling that")
                    return

                combatant_announcer = SpiffyPlayerAnnouncer(irc=irc,
                                                            destination=combatant.nick)

                player_announcer = SpiffyPlayerAnnouncer(irc=irc,
                                                         destination=player.nick)

                """
                New battle if this is a NPC
                """
                if combatant.is_npc:
                    player.add_battle(combatant=combatant, rounds=3)
                    combatant.add_battle(combatant=player, rounds=3)

                    dungeon.announcer.challenge_accepted(attacker=player,
                                                         target=combatant)

                    player_announcer.challenge_accepted(combatant=combatant)
                else:
                    """
                    We don't really need to tell players that their challenge
                    was sent to a NPC since the NPC always accepts.
                    """
                    player_announcer.challenge_sent(combatant=combatant)

                    """
                    Combatant is not a player. Let them know they've
                    received a challenge.
                    """
                    combatant_announcer.challenge_received(combatant=player)

                    """
                    Schedule challenge forfeit if the challenge
                    was not accepted within the timeout.

                    challenge_timeout = 30

                    def check_challenge_timeout():
                        challenge = combatant.get_last_battle_by_combatant(combatant=player)

                        if challenge is not None:
                            seconds_since_challenge = time.time() - challenge.created_at

                            if seconds_since_challenge >= challenge_timeout:
                                player.cancel_challenge(combatant=combatant)

                    schedule.addEvent(check_challenge_timeout,
                                      time.time() + challenge_timeout,
                                      name="check_challenge_timeout")
                    """
            else:
                irc.error("Invalid target")

    challenge = wrap(challenge, ["user", "text"])

    def topplayers(self, irc, msg, args, user):
        """
        Shows top 3 players by experience gained
        """
        dungeon_info = self._get_dungeon_and_user_id(irc, msg)

        if dungeon_info is not None:
            dungeon = dungeon_info["dungeon"]
            players = dungeon.player_unit_collection.get_top_players_by_xp()

            for player in players:
                dungeon.announcer.unit_info(
                    unit=player, irc=irc, dungeon=dungeon)

    topplayers = wrap(topplayers, ["user"])

    def help(self, irc, msg, args):
        """
        help - shows basic commands
        """
        help_msg = "Basic commands: .look, .i, .rock, .paper, .scissors, .lizard, .spock (Read more: http://git.io/vR8f1)"

        irc.reply(help_msg, notice=True)

    help = wrap(help)

    def srole(self, irc, msg, args, user, role):
        """
        Changes your role to something else
        """
        user_id = self._get_user_id(irc, msg.prefix)
        channel = msg.args[0]

        if user_id is not None:
            dungeon = self.SpiffyWorld.get_dungeon_by_channel(channel)

            if dungeon is not None:
                player = dungeon.get_unit_by_user_id(user_id)
                unit_type_id = self._get_unit_type_id_by_name(role)

                if unit_type_id is not None:
                    self.db.update_player_role(player.id, unit_type_id)

                    self.announcer.player_role_change(
                        player, role, unit_type_id)
                else:
                    classes = self._get_unit_type_list()

                    irc.error(
                        "Please choose one of the following roles: %s" % classes)

    srole = wrap(srole, ["user", "text"])

    def item(self, irc, msg, args, user, item_name):
        """
        Searches for an item by its name
        """
        item = self.SpiffyWorld.item_collection.get_item_by_item_name(
            item_name)

        if item is not None:
            dungeon = self.SpiffyWorld.get_dungeon_by_channel(GAME_CHANNEL)

            if dungeon is not None:
                user_id = self._get_user_id(irc, msg.prefix)
                player = dungeon.get_unit_by_user_id(user_id)

                """
                In order to provide information about items in a
                unit's inventory, we use the one in their inventory
                if they have it. This facilitates proper representation
                of item properties like Charges
                """
                if player.has_item(item=item):
                    item = player.get_item_from_inventory_by_name(
                        item_name=item.name)

                dungeon.announcer.item_info(item=item,
                                            player=player,
                                            irc=irc)
        else:
            irc.error("The tomes hold no mention of this artifact.")

    item = wrap(item, ["user", "text"])

    def effect(self, irc, msg, args, user, effect_name):
        """
        Searches for an effect by its name
        """
        effect = self.SpiffyWorld.effects_collection.get_effect_by_name(
            name=effect_name)

        if isinstance(effect, SpiffyEffect):
            dungeon = self.SpiffyWorld.get_dungeon_by_channel(GAME_CHANNEL)

            if dungeon is not None:
                dungeon.announcer.effect_info(effect=effect, irc=irc)
        else:
            irc.error("The tomes hold no mention of this spell.")

    effect = wrap(effect, ["user", "text"])

    def equip(self, irc, msg, args, user, item_name):
        """
        Equips an item from your inventory
        """
        user_id = None

        try:
            user_id = self._get_user_id(irc, msg.prefix)
        except KeyError:
            log.error("SpiffyRPG: error getting user id for %s" % msg.prefix)

        dungeon = self.SpiffyWorld.get_dungeon_by_channel(GAME_CHANNEL)

        if dungeon is not None:
            player = dungeon.get_unit_by_user_id(user_id)

            if player is not None:
                player.equip_item_by_name(item_name=item_name)
            else:
                irc.error(
                    "A hulking terror emerges from the darkness and consumes you.")
        else:
            irc.error(
                "You attempt to equip that item, but suddenly burst into flames!")

    equip = wrap(equip, ["user", "text"])

    def inventory(self, irc, msg, args, user):
        """
        Items in your inventory.
        """
        user_id = None

        try:
            user_id = self._get_user_id(irc, msg.prefix)
        except KeyError:
            log.error("SpiffyRPG: error getting user id for %s" % msg.prefix)

        dungeon = self.SpiffyWorld.get_dungeon_by_channel(GAME_CHANNEL)

        if dungeon is not None:
            player = dungeon.get_unit_by_user_id(user_id)

            if player is not None:
                announcer = SpiffyPlayerAnnouncer(irc=irc,
                                                  destination=msg.nick)

                announcer.inventory(player=player, irc=irc)
        else:
            irc.error("Your bags explode, blanketing you in flames!")

    inventory = wrap(inventory, ["user"])

    def raisedead(self, irc, msg, args, user, target):
        """
        Attempts to raise your target from the dead
        """
        user_id = self._get_user_id(irc, msg.prefix)
        dungeon = self.SpiffyWorld.get_dungeon_by_channel(GAME_CHANNEL)

        if dungeon is not None:
            player = dungeon.get_unit_by_user_id(user_id)
            unit = dungeon.get_dead_unit_by_name(target)

            if unit is not None:
                undead_effect = self.SpiffyWorld.effects_collection.get_effect_undead()

                unit.apply_effect(undead_effect)

                dungeon.announcer.effect_raise_dead(player=player,
                                                    unit=unit)

                dungeon.announcer.unit_info(unit=unit,
                                            dungeon=dungeon,
                                            irc=irc)

                player.add_raised_unit(unit=unit)
            else:
                irc.error(
                    "You attempt to perform the ritual, but something seems amiss.")
        else:
            log.error("Trying to raise dead but there is no dungeon")

    raisedead = wrap(raisedead, ["user", "text"])

    def seffect(self, irc, msg, args, user, effect):
        """
        Casts a spell
        """
        channel = msg.args[0]
        dungeon = self.SpiffyWorld.get_dungeon_by_channel(channel)
        user_id = self._get_user_id(irc, msg.prefix)

        if dungeon is not None:
            effect = self.db.get_effect_by_name(effect)

            if effect is not None:
                log.info("SpiffyRPG: found effect %s" % effect)

                five_minutes = 300
                two_minutes = 120
                duration = time.time() + five_minutes

                player = dungeon.get_unit_by_user_id(user_id)

                self.db.add_player_effect(player.id, effect.id)
                self.dungeon_announcer.effect_applied_to_player(
                    player, effect, duration)
            else:
                irc.error("You search your spell book, finding nothing.")

    seffect = wrap(seffect, ["user", "text"])

    def sjoin(self, irc, msg, args, user, character_class):
        """
        Choose a class: Zen Master, Hacker, or Troll
        """
        user_id = self._get_user_id(irc, msg.prefix)

        if user_id is not None:
            char_name = msg.nick
            channel = GAME_CHANNEL
            dungeon = self.SpiffyWorld.get_dungeon_by_channel(channel)

            if dungeon is not None:
                """ Add player to dungeon """
                player = dungeon.spawn_player_unit(user_id=user_id)

                if player is not None:
                    valid_registration = self._is_valid_char_class(
                        character_class)

                    if valid_registration:
                        unit_type_id = self._get_unit_type_id_by_name(
                            character_class)

                        if unit_type_id is not None:
                            log.info("SpiffyRPG: %s -> register '%s' the '%s' with class id %s " %
                                     (msg.nick, char_name, character_class, unit_type_id))

                            self.db.register_new_player(
                                user_id, char_name, unit_type_id)
                            dungeon.announcer.new_player(
                                irc, char_name, character_class)
                            irc.queueMsg(ircmsgs.voice(GAME_CHANNEL, msg.nick))
                        else:
                            log.error(
                                "SpiffyRPG: error determining class id from '%s'" % character_class)
                    else:
                        classes = self._get_unit_type_list()
                        irc.reply(
                            "Please choose one of the following classes: %s" % classes, notice=True)
        else:
            log.info(
                "SpiffyRPG: %s is trying to join but is not registered" % msg.nick)

    sjoin = wrap(sjoin, ["user", "text"])

    """
    =================================================================
    = Admin-only commands                                           =
    =================================================================
    """

    def fspawn(self, irc, msg, args, unit_level, unit_type_name):
        """
        Spawns a NPC - <level> <zen master|hacker|troll>
        """
        dungeon = self.SpiffyWorld.get_dungeon_by_channel(msg.args[0])

        if dungeon is not None:
            unit_type_id = self._get_unit_type_id_by_name(unit_type_name)

            dungeon.spawn_unit(level=unit_level, unit_type_id=unit_type_id)
        else:
            log.error("SpiffyRPG: could not find dungeon %s" % msg.args[0])

    fspawn = wrap(fspawn, ["something", optional("anything")])

    def fhostile(self, irc, msg, args, unit_name):
        """
        fhostile <unit name> - changes unit's combat status to hostile
        """
        dungeon = self.SpiffyWorld.get_dungeon_by_channel(GAME_CHANNEL)

        if dungeon is not None:
            unit = dungeon.get_unit_by_name(unit_name)

            if unit is not None:
                unit.combat_status = "hostile"
                irc.reply("%s's combat status has been set to HOSTILE" %
                          unit.get_name(), notice=True)
            else:
                irc.error("Couldn't find that unit")

    fhostile = wrap(fhostile, ["text"])

    def fitem(self, irc, msg, args, item_name):
        """
        fitem <item name> - add this item to your inventory
        """
        dungeon = self.SpiffyWorld.get_dungeon_by_channel(GAME_CHANNEL)

        if dungeon is not None:
            item = self.SpiffyWorld.item_collection.get_item_by_item_name(
                item_name=item_name)

            if item is None:
                irc.error("Could not find that item!")
                return

            user_id = self._get_user_id(irc, msg.prefix)
            unit = dungeon.get_unit_by_user_id(user_id)

            if unit is not None:
                unit.items.append(item)

                irc.reply("%s has been added to your inventory" %
                          item.name, notice=True)
            else:
                irc.error("Couldn't find that unit")

    fitem = wrap(fitem, ["text"])

    def fkill(self, irc, msg, args, unit_name):
        """
        Kill target unit
        """
        dungeon = self.SpiffyWorld.get_dungeon_by_channel(GAME_CHANNEL)

        if dungeon is not None:
            user_id = self._get_user_id(irc, msg.prefix)
            unit = dungeon.get_unit_by_name(unit_name)
            player = dungeon.get_player_by_user_id(user_id)

            if unit is not None:
                unit.apply_damage(damage=unit.calculate_hp(),
                                  attacker=player)

                dungeon.announcer.unit_death(unit=unit,
                                             slain_by=player)
        else:
            log.error("SpiffyRPG: could not find dungeon %s" % GAME_CHANNEL)

    fkill = wrap(fkill, ["text"])

    def flevel(self, irc, msg, args, level):
        """
        Change your level
        """
        dungeon = self.SpiffyWorld.get_dungeon_by_channel(GAME_CHANNEL)

        if dungeon is not None:
            user_id = self._get_user_id(irc, msg.prefix)
            unit = dungeon.get_unit_by_user_id(user_id)

            if unit is not None:
                int_level = int(level)
                xp_for_level = self.unit_level.get_xp_for_level(int_level) + 1

                log.info("SpiffyRPG: setting xp for %s to %s (level %s)" %
                         (unit.get_name(), xp_for_level, int_level))

                unit.experience = xp_for_level
                unit.level = self.unit_level.get_level_by_xp(unit.experience)
                unit.on_unit_level()

                dungeon.announcer.unit_info(unit=unit,
                                            dungeon=dungeon,
                                            irc=irc)
        else:
            log.error("SpiffyRPG: could not find dungeon %s" % msg.args[0])

    flevel = wrap(flevel, ["something"])

    def fitems(self, irc, msg, args, unit_name):
        """
        Shows the items of another unit
        """
        dungeon = self.SpiffyWorld.get_dungeon_by_channel(GAME_CHANNEL)

        if dungeon is not None:
            unit = dungeon.get_unit_by_name(unit_name)

            if unit is not None:
                announcer = SpiffyPlayerAnnouncer(irc=irc,
                                                  destination=msg.nick)

                announcer.inventory(player=unit, irc=irc)
        else:
            log.error("SpiffyRPG: could not find dungeon %s" % msg.args[0])

    fitems = wrap(fitems, ["text"])

    def fchaos(self, irc, msg, args):
        """
        Heralds chaos
        """
        dungeon = self.SpiffyWorld.get_dungeon_by_channel(msg.args[0])

        if dungeon is not None:
            dungeon.herald_chaos()
        else:
            log.error("SpiffyRPG: could not find dungeon %s" % msg.args[0])

    fchaos = wrap(fchaos)

    def fmove(self, irc, msg, unit, position):
        """
        fmove unitID positionID - Moves a unit to specified position
        """
        pass

    fmove = wrap(fmove, ["text"])

    def doQuit(self, irc, msg):
        user_id = None
        nick = msg.nick

        try:
            hostmask = irc.state.nickToHostmask(nick)
            user_id = ircdb.users.getUserId(hostmask)
        except KeyError:
            log.info("SpiffyRPG: error getting hostmask for %s" % nick)

        if user_id is not None:
            dungeon = self.SpiffyWorld.get_dungeon_by_channel(GAME_CHANNEL)

            if dungeon is not None:
                unit = dungeon.get_unit_by_user_id(user_id)

                if unit is not None:
                    log.info("SpiffyRPG: removing %s from dungeon" %
                             unit.get_name())

                    dungeon.remove_unit(unit)

    doPart = doQuit
    doKick = doQuit

    def doNick(self, irc, msg):
        """
        Update player's nick if they change it
        """
        old_nick = msg.prefix.split('!')[0]
        new_nick = msg.args[0]

        user_id = None

        try:
            hostmask = irc.state.nickToHostmask(new_nick)
            user_id = ircdb.users.getUserId(hostmask)
        except KeyError:
            log.info("SpiffyRPG: error getting hostmask for %s" % new_nick)

        if user_id is not None:
            dungeon = self.SpiffyWorld.get_dungeon_by_channel(GAME_CHANNEL)

            if dungeon is not None:
                unit = dungeon.get_player_by_user_id(user_id)

                if unit is not None:
                    unit.nick = new_nick

                    log.info("SpiffyRPG: nick change: %s is now known as %s, updating unit %s" %
                             (old_nick, new_nick, unit.get_name()))

    def doJoin(self, irc, msg):
        """
        Announces players joining
        """
        is_bot_joining = hasattr(msg, "nick") and msg.nick == irc.nick

        if is_bot_joining:
            log.info("SpiffyRPG: bot joining")
            self._init_world()
        else:
            user_id = self._get_user_id_by_irc_and_msg(irc, msg)

            if user_id is not None:
                dungeon = self.SpiffyWorld.get_dungeon_by_channel(GAME_CHANNEL)

                if dungeon is not None:
                    player = dungeon.spawn_player_unit(user_id=user_id)

                    if player is not None:
                        """ Voice recognized users """
                        irc.queueMsg(ircmsgs.voice(GAME_CHANNEL, msg.nick))

                        if player.id in self.welcome_messages:
                            last_welcome = time.time() - \
                                self.welcome_messages[player.id]
                        else:
                            last_welcome = time.time() - \
                                self.welcome_message_cooldown_in_seconds

                        if last_welcome > self.welcome_message_cooldown_in_seconds:
                            dungeon.announcer.unit_info(
                                unit=player, dungeon=dungeon, irc=irc)
                            self.welcome_messages[player.id] = time.time()
                        else:
                            log.info(
                                "SpiffyRPG: not welcoming %s because cooldown" % player.name)
                    else:
                        log.error(
                            "SpiffyRPG: could not find player with user_id %s" % user_id)

Class = SpiffyRPG
