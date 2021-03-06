#!/usr/bin/env python
# -*- coding: utf-8 -*-
###
# Copyright (c) 2015, butterscotchstallion
# All rights reserved.
#
#
###
from supybot.commands import *
import supybot.callbacks as callbacks
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.log as log
import supybot.ircdb as ircdb
import supybot.conf as conf
import supybot.world as supyworld
import re
import time
from SpiffyWorld import Database, Worldbuilder, \
    Battle as SpiffyBattle, PlayerAnnouncer

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('SpiffyRPG')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x

SQLITE_DB_FILENAME = "SpiffyRPG.sqlite3.db"
GAME_CHANNEL = "#SpiffyRPG"


class SpiffyRPG(callbacks.Plugin):

    """A gluten-free IRC RPG"""
    threaded = True

    def __init__(self, irc):
        self.db = None
        self.SpiffyWorld = None
        self.irc = irc
        self.welcome_messages = {}
        self.welcome_message_cooldown_in_seconds = 600

        self.__parent = super(SpiffyRPG, self)
        self.__parent.__init__(irc)

        self._init_world()

    def _get_user_id(self, irc, prefix):
        try:
            return ircdb.users.getUserId(prefix)
        except KeyError:
            pass

    def _get_user_id_by_irc_and_msg(self, irc, msg):
        user_id = None

        if hasattr(msg, "prefix"):
            user_id = self._get_user_id(irc, msg.prefix)

        if hasattr(msg, "nick"):
            hostmask = irc.state.nickToHostmask(msg.nick)
            user_id = self._get_user_id(irc, hostmask)

        return user_id

    def _is_alphanumeric_with_dashes(self, input):
        return re.match('^[\w-]+$', input) is not None

    def _is_valid_char_name(self, char_name):
        return len(char_name) > 1 and len(char_name) <= 16 \
            and self._is_alphanumeric_with_dashes(char_name)

    def _is_valid_char_class(self, unit_type):
        col = self.SpiffyWorld.unit_type_collection
        return col.get_unit_type_by_name(unit_type)

    def _is_nick_in_channel(self, irc, nick):
        return nick in irc.state.channels[GAME_CHANNEL].users

    def _get_character_class_list(self):
        col = self.SpiffyWorld.unit_type_collection
        return col.get_unit_type_name_list()

    def _get_unit_type_id_by_name(self, unit_type):
        col = self.SpiffyWorld.unit_type_collection
        unit_type = col.get_unit_type_by_name(unit_type)

        if unit_type is not None:
            return unit_type.id

    def _init_world(self):
        """
        We need the nicks in the channel in order to initialize
        the world.
        """
        db_path = conf.supybot.directories.data.dirize(SQLITE_DB_FILENAME)

        if self.db is None:
            database = Database(path=db_path, log=log)
            self.db = database.get_connection()

        assert self.db is not None

        if self.SpiffyWorld is None:
            log.info("Initializing world.")

            worldbuilder = Worldbuilder(db=self.db,
                                        irc=self.irc,
                                        ircmsgs=ircmsgs,
                                        ircutils=ircutils,
                                        log=log)
            spiffy_world = worldbuilder.build_world()

            self.SpiffyWorld = spiffy_world

            self._add_players_from_channel(new_player_nick=None)

        assert self.SpiffyWorld is not None

    def _add_players_from_channel(self, **kwargs):
        nicks_in_channel = []
        ignore_nicks = self.registryValue("ignoreNicks")
        new_player_nick = None

        if "new_player_nick" in kwargs:
            new_player_nick = kwargs["new_player_nick"]

        if GAME_CHANNEL in self.irc.state.channels:
            nicks_in_channel = self.irc.state.channels[GAME_CHANNEL].users

        for nick in nicks_in_channel:
            if not nick:
                continue

            if nick in ignore_nicks:
                continue

            # Skip bot nick
            if nick == self.irc.nick:
                continue

            unit_collection = self.SpiffyWorld.unit_collection

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

            if user_id is not None:
                player = unit_collection.get_player_by_user_id(user_id)

                if player is not None:
                    player.nick = nick
                    dungeon = self.SpiffyWorld.get_dungeon_by_channel(GAME_CHANNEL)
                    dungeon.add_unit(player)

                    if new_player_nick is not None:
                        if player.nick == new_player_nick:
                            return player
                else:
                    log.error("No player with user_id %s" % user_id)

    def _get_dungeon_and_player(self, irc, user):
        dungeon = self.SpiffyWorld.get_dungeon_by_channel(GAME_CHANNEL)
        user_id = user.id

        if dungeon is not None:
            player = dungeon.get_unit_by_user_id(user_id)

            if player is not None:
                return {
                    "dungeon": dungeon,
                    "player": player
                }
            else:
                irc.error("Cannot find player with user id %s" % user_id)
        else:
            irc.error("No dungeon")

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
                battle = SpiffyBattle(log=log)

                return {
                    "dungeon": dungeon,
                    "player": player,
                    "battle": battle
                }

    def _start_player_battle_with_weapon(self, **kwargs):
        """
        1. Get dungeon and player
        2. Equip player with desired item type
        3. Start battle and add combatants
        4. Add round
        """
        irc = kwargs["irc"]
        player_user = kwargs["player_user"]
        target_name = kwargs["target_name"]
        weapon_type = kwargs["weapon_type"]

        dungeon_info = self._get_dungeon_and_player(irc, player_user)

        if dungeon_info is not None:
            dungeon = dungeon_info["dungeon"]
            player = dungeon_info["player"]

            target_unit = dungeon.get_living_unit_by_name(target_name)

            if target_unit is None:
                irc.error("Invalid target")
                return

            equip_ok = player.equip_item_by_type(item_type=weapon_type)

            if equip_ok is not None:
                new_battle = SpiffyBattle(log=log)
                can_start_round = new_battle.can_add_round(attacker=player,
                                                           target=target_unit)

                if can_start_round is True:
                    """
                    NPCs equip a random weapon that is not what the player
                    chose each battle. This could probably be moved somewhere
                    else. Perhaps into Battle?
                    """
                    if target_unit.is_npc:
                        target_unit.equip_random_weapon(avoid_weapon_type=weapon_type)

                    """
                    Find the last battle, or create a new one if there isn't
                    one already.
                    """
                    bm = self.SpiffyWorld.battlemaster
                    battle = bm.get_battle_by_combatant(combatant=target_unit)

                    if battle is None:
                        battle = new_battle
                        battle.add_combatant(player)
                        battle.add_combatant(target_unit)

                        added_successfully = bm.add_battle(battle=battle)

                        """
                        When a combatant is currently engaged in combat,
                        they cannot be added to another battle.
                        """
                        if added_successfully is not True:
                            irc.error(added_successfully)
                            return

                        """
                        Announce challenge accepted if this is a new
                        battle.

                        dungeon.announcer.challenge_accepted(attacker=player,
                                                             target=target_unit)
                        """

                    battle.start_round(battle=battle,
                                       irc=irc,
                                       ircmsgs=ircmsgs,
                                       dungeon=dungeon,
                                       ircutils=ircutils)

                else:
                    formatted_error \
                        = "Cannot start round {} vs {} because {}".format(player,
                                                                          target_unit,
                                                                          can_start_round)
                    log.error(formatted_error)
                    irc.error(can_start_round)
            else:
                irc.error("You can't equip that.")
        else:
            log.error("SpiffyWorld: Player %s not found!" % player_user)
            irc.error("Player not found")

    """
    Game commands
    """
    def inspect(self, irc, msg, args, user, target):
        """
        Inspects a unit or item
        """
        dungeon_info = self._get_dungeon_and_player(irc, user)

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
        else:
            irc.error("Unable to get dungeon/user")

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
                player_announcer = PlayerAnnouncer(irc=irc,
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

    def rock(self, irc, msg, args, user, target_name):
        """
        rock <target> - attacks your target with a Rock type weapon
        """
        self._start_player_battle_with_weapon(irc=irc,
                                              player_user=user,
                                              target_name=target_name,
                                              weapon_type="rock")
    rock = wrap(rock, ["user", "text"])

    def paper(self, irc, msg, args, user, target_name):
        """
        paper <target> - attacks your target with a Paper type weapon
        """
        self._start_player_battle_with_weapon(irc=irc,
                                              player_user=user,
                                              target_name=target_name,
                                              weapon_type="paper")

    paper = wrap(paper, ["user", "text"])

    def scissors(self, irc, msg, args, user, target_name):
        """
        scissors <target> - attacks your target with a Scissors type weapon
        """
        self._start_player_battle_with_weapon(irc=irc,
                                              player_user=user,
                                              target_name=target_name,
                                              weapon_type="scissors")

    scissors = wrap(scissors, ["user", "text"])

    def lizard(self, irc, msg, args, user, target_name):
        """
        lizard <target> - attacks your target with a Lizard type weapon
        """
        self._start_player_battle_with_weapon(irc=irc,
                                              player_user=user,
                                              target_name=target_name,
                                              weapon_type="lizard")

    lizard = wrap(lizard, ["user", "text"])

    def spock(self, irc, msg, args, user, target_name):
        """
        spock <target> - attacks your target with a Spock type weapon
        """
        self._start_player_battle_with_weapon(irc=irc,
                                              player_user=user,
                                              target_name=target_name,
                                              weapon_type="spock")

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
                player_announcer = PlayerAnnouncer(irc=irc,
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

                combatant_announcer = PlayerAnnouncer(irc=irc,
                                                      destination=combatant.nick)

                player_announcer = PlayerAnnouncer(irc=irc,
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
            players = self.SpiffyWorld.unit_collection.get_top_players_by_xp()

            for player in players:
                dungeon.announcer.unit_info(
                    unit=player, irc=irc, dungeon=dungeon)

    topplayers = wrap(topplayers, ["user"])

    def help(self, irc, msg, args):
        """
        help - shows basic commands
        """
        help_msg = "Basic commands: .look, .i, .rock, .paper, .scissors, \
        .lizard, .spock (Read more: http://git.io/vR8f1)"

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
        user_id = user.id
        dungeon = self.SpiffyWorld.get_dungeon_by_channel(GAME_CHANNEL)

        if dungeon is not None:
            player = dungeon.get_unit_by_user_id(user_id)

            if player is not None:
                equipped_item = player.equip_item_by_name(item_name=item_name)
                announcer = PlayerAnnouncer(irc=irc,
                                            destination=msg.nick,
                                            ircutils=ircutils,
                                            ircmsgs=ircmsgs)

                if equipped_item is not None:
                    announcer.item_equip(player=player,
                                         item=equipped_item)
                else:
                    announcer.item_equip_failed(player=player,
                                                item_name=equipped_item.name)
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
                announcer = PlayerAnnouncer(irc=irc,
                                            destination=msg.nick,
                                            ircutils=ircutils,
                                            ircmsgs=ircmsgs)

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
        user_id = user.id

        char_name = msg.nick
        channel = GAME_CHANNEL
        dungeon = self.SpiffyWorld.get_dungeon_by_channel(channel)

        if dungeon is not None:
            valid_registration = self._is_valid_char_class(character_class)

            if valid_registration:
                unit_type_id = self._get_unit_type_id_by_name(
                    character_class)

                if unit_type_id is not None:
                    log.info("SpiffyRPG: %s -> register '%s' the '%s' with class id %s " %
                             (msg.nick, char_name, character_class, unit_type_id))

                    self.SpiffyWorld.unit_model.register_new_player(
                        user_id, char_name, unit_type_id)
                    dungeon.announcer.new_player(char_name, character_class)

                    if not supyworld.testing:
                        irc.queueMsg(ircmsgs.voice(GAME_CHANNEL, msg.nick))
                else:
                    log.error(
                        "SpiffyRPG: error determining class id from '%s'" % character_class)
            else:
                classes = self._get_unit_type_list()
                irc.reply(
                    "Please choose one of the following classes: %s" % classes, notice=True)
        else:
            irc.error("No dungeon!")

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
                announcer = PlayerAnnouncer(irc=irc,
                                            destination=msg.nick,
                                            ircutils=ircutils,
                                            ircmsgs=ircmsgs)

                announcer.inventory(player=unit, irc=irc)
        else:
            log.error("SpiffyRPG: could not find dungeon %s" % msg.args[0])

    fitems = wrap(fitems, ["text"])

    """ Limnoria callbacks """

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
        if supyworld.testing:
        """
        player = self._add_players_from_channel(new_player_nick=msg.nick)

        if player is not None:
            """ Voice recognized users """
            irc.queueMsg(ircmsgs.voice(GAME_CHANNEL, msg.nick))

Class = SpiffyRPG
