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
import random
import re
import time

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
        self.channel = GAME_CHANNEL

    def _get_db(self):
        #if self.db is not None:
        #    return self.db
        import sqlite3

        filename = conf.supybot.directories.data.dirize(SQLITE_DB_FILENAME)
        db = sqlite3.connect(filename, check_same_thread=False)
        db.row_factory = sqlite3.Row

        log.debug("DB: connecting to %s" % filename)

        return db

    def register_new_player(self, user_id, char_name, class_id):
        db = self._get_db()
        cursor = db.cursor()
        created_at = time.time()
        params = (user_id, char_name, class_id, created_at)
        cursor.execute("""INSERT INTO spiffyrpg_players(user_id,
                          character_name, 
                          character_class_id,
                          created_at)
                          VALUES (?, ?, ?, ?)""", params)
        db.commit()

    def get_player_by_user_id(self, user_id):
        db = self._get_db()
        cursor = db.cursor()

        log.info("SpiffyRPG: looking up user id %s" % user_id)

        params = (user_id,)
        cursor.execute("""SELECT p.id,
                          p.character_class_id,
                          p.character_name,
                          p.created_at,
                          p.user_id,
                          p.experience_gained,
                          c.name AS class_name
                          FROM spiffyrpg_players p
                          JOIN spiffyrpg_character_classes c ON c.id = p.character_class_id
                          WHERE user_id = ?""", params)
        player = cursor.fetchone()

        if player is not None:
            return dict(player)

    def add_player_experience(self, player_id, experience_gained):
        db = self._get_db()
        cursor = db.cursor()

        params = (experience_gained, player_id)

        cursor.execute("""UPDATE spiffyrpg_players
                          SET experience_gained = experience_gained + ?
                          WHERE id = ?""", 
                       params)

        db.commit()

    def get_character_classes(self):
        db = self._get_db()
        cursor = db.cursor()

        cursor.execute("""SELECT id, name
                          FROM spiffyrpg_character_classes""")

        return cursor.fetchall()

    def get_class_ability(self, class_id, player_level):
        db = self._get_db()
        cursor = db.cursor()

        cursor.execute("""SELECT name
                          FROM spiffyrpg_class_abilities
                          WHERE character_class_id = ?
                          AND min_level <= ?
                          ORDER BY RANDOM()
                          LIMIT 1""", (class_id, player_level))

        ability = cursor.fetchone()

        if ability is not None:
            return ability["name"]
    
    def get_finishing_move_by_class_id(self, class_id, player_level):
        db = self._get_db()
        cursor = db.cursor()

        cursor.execute("""SELECT name
                          FROM spiffyrpg_class_finishing_moves
                          WHERE character_class_id = ?
                          AND min_level <= ?
                          ORDER BY RANDOM()
                          LIMIT 1""", (class_id, player_level))

        move = cursor.fetchone()

        if move is not None:
            return move["name"]

    def add_battle(self, battle):
        db = self._get_db()
        cursor = db.cursor()

        params = (battle["attacker_player_id"], 
                  battle["target_player_id"],
                  battle["winner_player_id"],
                  battle["loser_player_id"],
                  time.time())

        cursor.execute("""INSERT INTO spiffyrpg_battles(
                       attacker_player_id,
                       target_player_id,
                       winner_player_id,
                       loser_player_id,
                       created_at)
                       VALUES(?, ?, ?, ?, ?)""", 
                       params)

        db.commit()

        return cursor.lastrowid

SpiffyRPGDB = plugins.DB("SpiffyRPG", {"sqlite3": SqliteSpiffyRPGDB})

class Announcer:
    """
    Handles announcing events and other things
    """
    def announce(irc, message):
        self._send_channel_notice(irc, message)

    def player_suicide(self, irc, player):
        """
        """
        euphemisms = ["bought the farm", "bit the big one", 
        "reached their expiration date", "did themselves in", 
        "commits seppuku", "told u they were hardcore", 
        "used a permanent solution to a temporary problem",
        "dug their own grave", "sleeps with the fishes now",
        "joins the mathletes", "took their own life", "gave up the ghost"]

        death = random.choice(euphemisms)
        title = ircutils.bold(player["title"])

        announcement_msg = "%s %s" % (title, death)

        self._send_channel_notice(irc, announcement_msg)

    def player_exhausted(self, irc, player):
        bold_title = ircutils.bold(player["title"])
        announcement_msg = "%s collapses from exhaustion" % bold_title

        self._send_channel_notice(irc, announcement_msg)

    def attack_miss(self, irc, attacker, target, attack_verb):
        """
        %'s attackverb missed %s!
        """
        bold_attacker = ircutils.bold(attacker["title"])
        bold_verb = ircutils.bold(attack_verb)
        bold_missed = ircutils.bold("missed")
        bold_target = ircutils.bold(target["title"])

        params = (bold_attacker, bold_verb, bold_missed, bold_target)

        announcement_msg = "%s's %s %s %s!" % params

        self._send_channel_notice(irc, announcement_msg)

    def player_info(self, irc, player):
        """
        %s is a level %s %s. %s XP remains until %s
        """
        bold_title = ircutils.bold(player["title"])
        bold_class = ircutils.bold(player["class_name"])
        formatted_xp = "{:,}".format(int(player["xp_for_this_level"]))
        bold_xp_needed_this_level = ircutils.bold(formatted_xp)
        bold_next_level = ircutils.bold(player["level"] + 1)
        bold_hp = ircutils.bold(player["hp"])
        bold_level = ircutils.bold(player["level"])
        formatted_xp_gained = "{:,}".format(int(player["experience_gained"]))
        bold_cur_xp = ircutils.bold(formatted_xp_gained)
        xp_combo = "/".join([bold_cur_xp, bold_xp_needed_this_level])

        params = (bold_title, bold_level, bold_class, bold_hp)
        announcement_msg = "%s is a level %s %s with %s HP. " % params
        announcement_msg += "%s XP to level %s" % \
        (xp_combo, bold_next_level)

        self._send_channel_notice(irc, announcement_msg)

    def player_gained_level(self, irc, player):
        """
        Player_1 has gained level X! 
        """
        params = (ircutils.bold(player["title"]), ircutils.bold(player["level"]))

        announcement_msg = "%s ascends to level %s!" % params

        self._send_channel_notice(irc, announcement_msg)

    def new_player(self, irc, char_name, char_class):
        """
        Player_1, the IRC Troll has joined the game!
        """
        params = (ircutils.bold(char_name), ircutils.bold(char_class))

        announcement_msg = "%s the %s joined the game!" % params

        self._send_channel_notice(irc, announcement_msg)

    def battle_in_progress(self, irc, battle):
        """
        Battle in progress: %s vs %s!
        """
        params = (ircutils.bold(battle["attacker"]["title"]), 
                  ircutils.bold(battle["target"]["title"]))

        announcement_msg = "Battle in progress: %s vs %s!" % params

        self._send_channel_notice(irc, announcement_msg)

    def battle_started(self, irc, attacker, target):
        """
        Battle started! %s vs %s!
        """
        announcement_msg = "Battle started! %s vs %s" % \
        (ircutils.bold(attacker["title"]), ircutils.bold(target["title"]))

        self._send_channel_notice(irc, announcement_msg)

    def attacker_victory_target_exhausted(self, irc, attacker, target, battle, xp):
        """
        %s earned %s experience because %s decided to take a nap
        """
        attacker_title = ircutils.bold(attacker["title"])
        target_title = ircutils.bold(target["title"])
        green_xp = ircutils.mircColor(xp, fg="green")
        params = (attacker_title, green_xp, target_title)

        announcement_msg = "%s earned %s experience because %s decided to take a nap" % params

        self._send_channel_notice(irc, announcement_msg)

    def player_victory(self, irc, attacker, target, battle, experience):
        """
        Player is victorious
        - Show win/loss ratio
        - Streak
        """
        attacker_title = ircutils.bold(attacker["title"])
        target_title = ircutils.bold(target["title"])
        red_hp = ircutils.mircColor(battle["target_hp"], fg="red")
        green_xp = ircutils.mircColor(experience, fg="green")
        defeat_words = killing_blows =  ["abolishing", "annihilating", "butchering", 
        "creaming", "defeating", "destroying", "devastating", "disfiguring", "dismantling", 
        "embarrassing", "exterminating", "felling", "goofing up", "making a mess of", 
        "nullifying", "putting the kibosh on", "quashing", "quelling", "raining destruction on", 
        "ravaging", "ruining", "shattering", "shattering", "slaying", "snuffing out", "stamping out", 
        "wrecking"]
        defeat_word = random.choice(defeat_words)
        params = (target_title, red_hp, attacker_title, green_xp, defeat_word, target_title)
        announcement_msg = "%s's HP was reduced to %s. %s earns %s XP for %s %s" % params

        self._send_channel_notice(irc, announcement_msg)

    def player_attack(self, irc, attack_info):
        """
        attack_info = {
            "attacker_title": attacker_title,
            "target_title": target_title,
            "attack_damage": attack_damage,
            "damage_type": damage_type,
            "battle": battle
        }
        """
        battle = attack_info["battle"]
        bold_attacker_title = ircutils.bold(attack_info["attacker_title"])
        bold_target_title = ircutils.bold(attack_info["target_title"])
        attacker_hp = ircutils.mircColor(battle["attacker_hp"], fg="green")
        danger_low_hp_threshold = 5
        attack_word = "hits"

        if attack_info["is_critical_strike"]:
            attack_word = ircutils.mircColor("critically strikes", fg="pink", bg="yellow")

        if battle["attacker_hp"] <= danger_low_hp_threshold:
            attacker_hp = ircutils.mircColor(battle["attacker_hp"], fg="red")

        target_hp = ircutils.mircColor(battle["target_hp"], fg="green")

        if battle["target_hp"] <= danger_low_hp_threshold:
            target_hp = ircutils.mircColor(battle["target_hp"], fg="red")

        red_damage = ircutils.mircColor(attack_info["attack_damage"], fg="red")

        if attack_info["is_killing_blow"]:
            attack_verb = ircutils.bold(ircutils.mircColor(attack_info["attack_verb"], fg="red"))
        else:
            attack_verb = ircutils.bold(attack_info["attack_verb"])

        damage_type = attack_info["damage_type"]
        bonus_damage = ircutils.mircColor(attack_info["bonus_damage"], fg="green")

        params = (bold_attacker_title, attack_verb, attack_word,
                  bold_target_title, red_damage, damage_type, bonus_damage)

        announcement_msg = "%s's %s %s %s for %s %s (%s bonus damage)" % params

        self._send_channel_notice(irc, announcement_msg)

    def _send_channel_notice(self, irc, message):
        """
        All event communication should be sent as a channel notice
        """
        irc.queueMsg(ircmsgs.notice(GAME_CHANNEL, message))

class Battle:
    def __init__(db):
        self.db = db

class Player:
    """
    Represents a player in SpiffyRPG and manages
    state information about the player
    """
    def get_items(self):
        return self.items

    def get_chance_to_hit(self, player):
        rand_chance = random.randrange(1, 80)

        return rand_chance

    def is_hit(self, chance_to_hit):
        return chance_to_hit < 80

class PlayerClass:
    """
    Represents different propertes of each class
    """
    OPEN_SOURCE_CONTRIBUTOR = 1
    INTERNET_TOUGH_GUY = 2
    BLACK_HAT = 3

    def is_vulnerable_to_magic(self, class_id):
        return class_id in (self.INTERNET_TOUGH_GUY, self.BLACK_HAT)

    def is_vulnerable_to_physical(self, class_id):
        return class_id in (self.OPEN_SOURCE_CONTRIBUTOR,)

    def get_damage_type(self, class_id):
        if class_id in (self.INTERNET_TOUGH_GUY, self.BLACK_HAT):
            return "Physical"
        else:
            return "Magic"

class SpiffyRPG(callbacks.Plugin):
    """A gluten-free IRC RPG"""
    threaded = True
    battle_in_progress = False
    battle = {}

    def __init__(self, irc):
        self.__parent= super(SpiffyRPG, self)
        self.__parent.__init__(irc)

        self.announcer = Announcer()
        self.player = Player()
        self.player_class = PlayerClass()
        self.db = SpiffyRPGDB()

        self.character_classes = self.db.get_character_classes()

    def _get_user_id(self, irc, prefix):
        try:
            return ircdb.users.getUserId(prefix)
        except KeyError:
            irc.errorNotRegistered(Raise=True)

    def _is_alphanumeric_with_dashes(self, input):
        return re.match('^[\w-]+$', input) is not None

    def _is_valid_char_name(self, char_name):
        return len(char_name) > 1 and len(char_name) <= 16 \
        and self._is_alphanumeric_with_dashes(char_name)

    def _is_valid_char_class(self, char_class):
        for id, class_name in self.character_classes:
            if class_name.lower() == char_class.lower():
                return True

    def _is_nick_in_channel(self, irc, nick):
        return nick in irc.state.channels[GAME_CHANNEL].users

    def _get_player_experience_for_next_level(self, level):
        xp = 0
        levels = self._get_experience_levels()

        for xp_level, req_xp in levels:
            if xp_level == (level+1):
                xp = req_xp
                break

        return xp

    def _get_experience_levels(self):
        return [
            (1, 0),
            (2, 100),
            (3, 200),
            (4, 300),
            (5, 400),
            (6, 1000),
            (7, 1500),
            (8, 2500),
            (9, 3500),
            (10, 5000)
        ]

    def _get_player_level_by_total_experience(self, total_experience):
        player_level = 1
        levels = self._get_experience_levels()
 
        for level, experience_needed in levels:
            if total_experience > experience_needed:
                player_level = level

        return player_level

    def _get_experience_for_battle(self, target_player_level):
        return int(5 * target_player_level)

    def _get_hp_by_player(self, player):
        player_level = self._get_player_level_by_total_experience(player["experience_gained"])
        hp = player_level * 20

        return hp

    def _get_player_title(self, player):
        return player["character_name"]

    def _get_attack_damage(self, attacker, target):
        # TODO get player items and determine formula based
        # on which items a player has. If a player has no items
        # then this is a melee attack based on strength
        damage = random.randrange(1, 5) * attacker["level"]
        vulnerability_damage = damage * 1.2
        target_class_id = target["character_class_id"]
        bonus_damage = 0

        # Magic
        if self.player_class.is_vulnerable_to_magic(target_class_id):
            bonus_damage += vulnerability_damage

        # Physical
        if self.player_class.is_vulnerable_to_physical(target_class_id):
            bonus_damage += vulnerability_damage

        bonus_damage = int(bonus_damage)
        damage += bonus_damage

        # Critical strike
        is_critical_strike = random.randrange(0, 100) < self._get_critical_strike_chance(attacker)

        if is_critical_strike:
            damage *= 2

        return {
            "is_critical_strike": is_critical_strike,
            "attack_damage": int(damage),
            "bonus_damage": bonus_damage,
            "damage_type": self.player_class.get_damage_type(attacker["character_class_id"])
        }

    def _get_critical_strike_chance(self, class_id):
        OPEN_SOURCE_CONTRIBUTOR = 3

        if class_id == OPEN_SOURCE_CONTRIBUTOR:
            return 25
        else:
            return 5

    def _on_battle_concluded(self, winner, loser):
        pass

    def _attacker_wins(self, irc, attacker, target, is_target_exhausted):
        victorious_battle_experience = self._get_experience_for_battle(target["level"])
        attacker["experience_gained"] += victorious_battle_experience

        self.db.add_player_experience(attacker["id"], victorious_battle_experience)

        log.info("SpiffyRPG: attacker wins; exhausted is %s", is_target_exhausted)

        if is_target_exhausted:
            self.announcer.attacker_victory_target_exhausted(irc, attacker, target, \
            victorious_battle_experience)
        else:
            self.announcer.player_victory(irc, attacker, target, self.battle, \
            victorious_battle_experience)

        current_level = self._get_player_level_by_total_experience(attacker["experience_gained"])
        attacker["level"] = current_level

        if current_level > self.battle["attacker_level_before_battle"]:
            attacker["title"] = self._get_player_title(attacker)
            self.announcer.player_gained_level(irc, attacker)

        self.battle_in_progress = False

    def _target_wins(self, irc, attacker, target, is_attacker_exhausted):
        victorious_battle_experience = self._get_experience_for_battle(target["level"])
        target["experience_gained"] += victorious_battle_experience

        self.db.add_player_experience(target["id"], victorious_battle_experience)

        log.info("SpiffyRPG: target wins; exhausted is %s", is_attacker_exhausted)

        # Special message when we are victorious over someone who is
        # exhausted
        if is_attacker_exhausted:
            self.announcer.attacker_victory_target_exhausted(irc, target, attacker, self.battle, \
            victorious_battle_experience)
        else:
            self.announcer.player_victory(irc, target, attacker, self.battle, \
            victorious_battle_experience)

        current_level = self._get_player_level_by_total_experience(target["experience_gained"])
        target["level"] = current_level

        if current_level > self.battle["target_level_before_battle"]:
            target["title"] = self._get_player_title(target)
            self.announcer.player_gained_level(irc, target)

        self.battle_in_progress = False

    def _attack_target_player(self, irc, attacker, target):
        """
        Performs an attack or announces a death where applicable
        """
        max_miss_count = 3
        self.battle["attacker_level_before_battle"] = attacker["level"]
        self.battle["target_level_before_battle"] = target["level"]

        def target_is_alive():
            return self.battle["target_hp"] > 0

        def attacker_is_alive():
            return self.battle["attacker_hp"] > 0

        def attacker_is_exhausted(max_miss_count):
            return self.battle["attacker_miss_count"] >= max_miss_count

        def target_is_exhausted(max_miss_count):
            return self.battle["target_miss_count"] >= max_miss_count

        params = (attacker["title"], self.battle["attacker_miss_count"],
        target["title"], self.battle["target_miss_count"])

        log.info("SpiffyRPG: %s has missed %s times and %s has missed %s times" % params)

        if attacker_is_exhausted(max_miss_count):
            self.announcer.player_exhausted(irc, attacker)
            self._target_wins(irc, target, attacker, True)
        elif target_is_exhausted(max_miss_count):
            self.announcer.player_exhausted(irc, target)
            self._attacker_wins(irc, attacker, target, True)

        if attacker_is_exhausted(max_miss_count) or target_is_exhausted(max_miss_count):
            self.battle_in_progress = False
            return

        """
        Two possibilities here: 
        1. attacker and target are alive
        2. attacker is alive and target is dead
        """
        if attacker_is_alive() and target_is_alive():
            chance_to_hit = self.player.get_chance_to_hit(attacker)
            is_hit = self.player.is_hit(chance_to_hit)
            attack_verb = self._get_attack_verb_by_player(attacker)
            is_killing_blow = False

            if is_hit:
                attack_damage_info = self._get_attack_damage(attacker, target)

                target_hp_if_hit = self.battle["target_hp"] - attack_damage_info["attack_damage"]
                is_killing_blow = target_hp_if_hit <= 0

                if is_killing_blow:
                    attack_verb = self._get_finishing_move_by_class_id(attacker["character_class_id"],
                                                                       attacker["level"])

                attack_info = {
                    "attacker_title": attacker["title"],
                    "target_title": target["title"],
                    "attack_damage": attack_damage_info["attack_damage"],
                    "battle": self.battle,
                    "is_critical_strike": attack_damage_info["is_critical_strike"],
                    "attack_verb": attack_verb,
                    "damage_type": attack_damage_info["damage_type"],
                    "bonus_damage": attack_damage_info["bonus_damage"],
                    "is_killing_blow": is_killing_blow
                }

                """ Announce the attack, if successful """
                self.announcer.player_attack(irc, attack_info)

                # Subtract attack damage from target hp
                self.battle["target_hp"] -= attack_damage_info["attack_damage"]

                """ It is possible for a single attack to win """
                if attacker_is_alive() and target_is_alive():
                    """ Now the target attempts to respond to the attacker """
                    chance_to_hit = self.player.get_chance_to_hit(target)
                    is_hit = self.player.is_hit(chance_to_hit)

                    """ Target is attempting to respond to attack """
                    if is_hit:
                        self._attack_target_player(irc, target, attacker)
                    else:
                        """ Target missed! """
                        self.battle["target_miss_count"] += 1
                        attack_verb = self._get_attack_verb_by_player(target)
                        self.announcer.attack_miss(irc, attacker, target, attack_verb)

                        """ Attacker responds """
                        self._attack_target_player(irc, attacker, target)

                elif attacker_is_alive() and not target_is_alive():
                    self._attacker_wins(irc, attacker, target, False)
                elif not attacker_is_alive() and target_is_alive():
                    self._target_wins(irc, target, attacker, False)
            else:
                self.battle["attacker_miss_count"] += 1
                self.announcer.attack_miss(irc, attacker, target, attack_verb)
                self._attack_target_player(irc, target, attacker)

        elif attacker_is_alive() and not target_is_alive():
            self._attacker_wins(irc, attacker, target, False)
        elif not attacker_is_alive() and target_is_alive():
            self._target_wins(irc, target, attacker, False)

    def _get_attack_verb_by_player(self, attacker):
        return self.db.get_class_ability(attacker["character_class_id"],
                                         attacker["level"])


    def _get_finishing_move_by_class_id(self, class_id, player_level):
        return self.db.get_finishing_move_by_class_id(class_id, player_level)

    def _get_character_class_list(self):
        class_list = []

        for c in self.character_classes:
            class_list.append(ircutils.bold(c["name"]))

        return ", ".join(class_list)

    def _get_character_class_id_by_name(self, class_name):
        for c in self.character_classes:
            if c["name"].lower() == class_name.lower():
                return c["id"]

    def sbattle(self, irc, msg, args, user, target_nick):
        """
        Battles another user: !sbattle <nick>
        """
        attacker_user_id = self._get_user_id(irc, msg.prefix)
        is_target_same_as_attacker = msg.nick == target_nick

        # Get attacker user id
        if not attacker_user_id:
            log.error("Oops, I can't determine your user id!")
            return

        # Make sure the target is in this channel
        target_nick_is_here = self._is_nick_in_channel(irc, target_nick)

        if not target_nick_is_here:
            irc.error("That nick doesn't appear to be here")
            return

        target_hostmask = irc.state.nickToHostmask(target_nick)
        target_user_id = self._get_user_id(irc, target_hostmask)

        # Make sure we can get the target user id
        if target_user_id is None:
            log.error("SpiffyRPG: could not find user id for nick '%s'" % target_nick)
            return

        # Get attacker
        attacker = self.db.get_player_by_user_id(attacker_user_id)

        if attacker is None:
            log.error("Couldn't find player by user id %s" % attacker_user_id)            
            return

        # Get player
        target = self.db.get_player_by_user_id(target_user_id)

        if target is None:
            log.error("Couldn't find target by user id %s" % target_user_id)
            irc.error("That user doesn't seem to be registered. Use !sjoin")
            return

        # Add levels
        attacker["level"] = self._get_player_level_by_total_experience(attacker["experience_gained"])
        target["level"] = self._get_player_level_by_total_experience(target["experience_gained"])

        # Titles
        attacker["title"] = self._get_player_title(attacker)
        target["title"] = self._get_player_title(target)

        self.battle["attacker_miss_count"] = 0
        self.battle["target_miss_count"] = 0

        # attacker attacks
        # determine if they hit
        # get attack damage based on modifiers
        # subtract hp from loser
        # then repeat with target attacking
        if self.battle_in_progress:
            self.announcer.battle_in_progress(irc, self.battle)
        else:
            self.battle["attacker"] = attacker
            self.battle["target"] = target
            
            # Update battle info
            self.battle["attacker_hp"] = self._get_hp_by_player(attacker)
            self.battle["target_hp"] = self._get_hp_by_player(target)

            """
            #1 - If the attacker is trying to fight themselves, let's do
            something interesting!
            """
            if is_target_same_as_attacker:
                attack_damage_info = self._get_attack_damage(attacker, target)

                attack_info = {
                    "attacker_title": attacker["title"],
                    "target_title": target["title"],
                    "attack_damage": self.battle["attacker_hp"],
                    "battle": self.battle,
                    "is_critical_strike": True,
                    "attack_verb": self.db.get_finishing_move_by_class_id(attacker["character_class_id"],
                                                                          attacker["level"]),
                    "damage_type": attack_damage_info["damage_type"],
                    "bonus_damage": attack_damage_info["bonus_damage"],
                    "is_killing_blow": True
                }

                self.announcer.player_attack(irc, attack_info)
                self.announcer.player_suicide(irc, attacker)
            else:
                self.battle_in_progress = True

                # Initiate attack!
                self._attack_target_player(irc, attacker, target)

    sbattle = wrap(sbattle, ["user", "text"])

    def sinfo(self, irc, msg, args, target_nick):
        """
        Shows information about a player
        """
        if not self._is_nick_in_channel(irc, target_nick):
            irc.error("I don't see that nick here")

        info_target = msg.nick
        target_hostmask = irc.state.nickToHostmask(target_nick)
        user_id = self._get_user_id(irc, target_hostmask)
        
        if user_id is not None:
            player = self.db.get_player_by_user_id(user_id)
            xp = player["experience_gained"]
            player["hp"] = self._get_hp_by_player(player)            
            player["level"] = self._get_player_level_by_total_experience(xp)
            player["xp_for_this_level"] = \
            self._get_player_experience_for_next_level(player["level"])
            player["title"] = self._get_player_title(player)

            if player is not None:
                self.announcer.player_info(irc, player)
            else:
                irc.error("That user has not joined the game :(")
        else:
            irc.error("I could not find anything on that user.")

    sinfo = wrap(sinfo, ["text"])

    def sjoin(self, irc, msg, args, user, character_class):
        """
        Joins the game: !sjoin <character class>
        """
        user_id = self._get_user_id(irc, msg.prefix)

        if user_id is not None:
            player = self.db.get_player_by_user_id(user_id)

            char_name = msg.nick

            if player is not None:
                irc.error("You're already registered!")
            else:
                valid_registration = self._is_valid_char_class(character_class)

                if valid_registration:
                    class_id = self._get_character_class_id_by_name(character_class)

                    if class_id is not None:
                        log.info("SpiffyRPG: %s -> register '%s' the '%s' with class id %s " % (msg.nick, char_name, character_class, class_id))

                        self.db.register_new_player(user_id, char_name, class_id)
                        self.announcer.new_player(irc, char_name, character_class)
                    else:
                        log.error("SpiffyRPG: error determining class id from '%s'" % character_class)

                else:
                    classes = self._get_character_class_list()
                    irc.reply("Please choose one of the following classes: %s" % classes)

    sjoin = wrap(sjoin, ["user", "text"])

Class = SpiffyRPG


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
