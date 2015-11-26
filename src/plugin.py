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
        self.channel = GAME_CHANNEL

    def _get_db(self):
        #if self.db is not None:
        #    return self.db
        import sqlite3

        filename = conf.supybot.directories.data.dirize(SQLITE_DB_FILENAME)
        db = sqlite3.connect(filename, check_same_thread=False)
        db.row_factory = sqlite3.Row

        #log.debug("DB: connecting to %s" % filename)

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

    def get_top_players_by_xp(self):
        db = self._get_db()
        cursor = db.cursor()

        cursor.execute("""SELECT p.id,
                          p.character_class_id,
                          p.character_name,
                          p.created_at,
                          p.user_id,
                          p.experience_gained,
                          c.name AS class_name
                          FROM spiffyrpg_players p
                          JOIN spiffyrpg_character_classes c ON c.id = p.character_class_id
                          ORDER BY p.experience_gained DESC
                          LIMIT 3""")

        return cursor.fetchall()

    def add_player_experience(self, player_id, experience_gained):
        db = self._get_db()
        cursor = db.cursor()

        params = (experience_gained, player_id)

        cursor.execute("""UPDATE spiffyrpg_players
                          SET experience_gained = experience_gained + ?
                          WHERE id = ?""", 
                       params)

        db.commit()

    def update_player_role(self, player_id, character_class_id):
        db = self._get_db()
        cursor = db.cursor()

        params = (character_class_id, player_id)

        cursor.execute("""UPDATE spiffyrpg_players
                          SET character_class_id = ?
                          WHERE id = ?""", 
                       params)

        db.commit()

    def get_character_classes(self):
        db = self._get_db()
        cursor = db.cursor()

        cursor.execute("""SELECT id, name
                          FROM spiffyrpg_character_classes""")

        return cursor.fetchall()

    def remove_expired_effects(self):
        db = self._get_db()
        cursor = db.cursor()
        now = datetime.now()

        cursor.execute("""DELETE FROM spiffyrpg_player_effects
                          WHERE 1=1
                          AND expires_at < ?
                          AND is_persistent = 0""", (now,))

        db.commit()

    def get_max_player_level(self):
        db = self._get_db()
        cursor = db.cursor()

        cursor.execute("""SELECT MAX(experience_gained) AS xp_max
                          FROM spiffyrpg_players""")

        player = cursor.fetchone()

        if player is not None:
            return player["xp_max"]

        cursor.close()

    def get_effect_by_name(self, effect_name):
        db = self._get_db()
        cursor = db.cursor()
        wildcard_effect = "%s%%" % effect_name

        cursor.execute("""SELECT e.id,
                          e.name,
                          e.description,
                          e.operator,
                          e.hp_percent_adjustment,
                          e.critical_strike_chance_adjustment,
                          e.damage_percent_adjustment,
                          e.chance_to_hit_adjustment
                          FROM spiffyrpg_effects e
                          WHERE 1=1
                          AND name LIKE ?""", (wildcard_effect,))

        effect = cursor.fetchone()

        if effect is not None:
            return effect

        cursor.close()

    def add_effect_battle_fatigue(self, player_id, duration=300):
        battle_fatigue = 2
        
        self.add_player_effect(player_id, battle_fatigue, duration)

    def add_effect_realm_king(self, player_id):
        log.info("SpiffyRPG: player %s -> Realm King" % player_id)
        realm_king = 3
        duration = 0
        is_persistent = 1

        self.add_player_effect(player_id, realm_king, duration, is_persistent)

    def add_player_effect(self, player_id, effect_id, duration=300, is_persistent=0):
        db = self._get_db()
        cursor = db.cursor()
        now = time.time()

        expires_at = now + duration
        params = (effect_id, player_id, expires_at, is_persistent, now)

        cursor.execute("""INSERT INTO spiffyrpg_player_effects(
                          effect_id,
                          player_id,
                          expires_at,
                          is_persistent,
                          created_at)
                          VALUES(?, ?, ?, ?)""", params)

    def get_player_effects(self, player_id):
        db = self._get_db()
        cursor = db.cursor()
        now = time.time()
        cursor.execute("""SELECT e.id,
                          e.name,
                          e.description,
                          e.operator,
                          e.hp_percent_adjustment,
                          e.critical_strike_chance_adjustment,
                          e.damage_percent_adjustment,
                          e.chance_to_hit_adjustment,
                          p.expires_at
                          FROM spiffyrpg_effects e
                          JOIN spiffyrpg_player_effects p ON p.effect_id = e.id
                          WHERE 1=1
                          AND p.expires_at > ?
                          AND p.player_id = ?
                          ORDER BY name""", (now, player_id,))

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
    
    def get_win_dialogue(self, character_class_id):
        db = self._get_db()
        cursor = db.cursor()

        cursor.execute("""SELECT dialogue
                          FROM spiffyrpg_character_dialogue
                          WHERE 1=1
                          AND character_class_id = ?
                          AND dialogue_type = 'win'
                          ORDER BY RANDOM()
                          LIMIT 1""", (character_class_id,))

        win = cursor.fetchone()

        if win is not None:
            return dict(win)["dialogue"]

    def get_monster_win_dialogue(self, monster_id):
        db = self._get_db()
        cursor = db.cursor()

        cursor.execute("""SELECT dialogue
                          FROM spiffyrpg_monster_dialogue
                          WHERE 1=1
                          AND monster_id = ?
                          AND dialogue_type = 'win'
                          ORDER BY RANDOM()
                          LIMIT 1""", (monster_id,))

        win = cursor.fetchone()

        if win is not None:
            return dict(win)["dialogue"]

    def get_realm_king_player_id(self):
        db = self._get_db()
        cursor = db.cursor()

        cursor.execute("""SELECT p.id
                          FROM spiffyrpg_players p
                          ORDER BY experience_gained DESC
                          LIMIT 1""")

        realm_king = cursor.fetchone()

        if realm_king is not None:
            return dict(realm_king)["id"]

    def remove_realm_king_effect(self):
        log.info("SpiffyRPG: removing realm kings")

        db = self._get_db()
        cursor = db.cursor()

        cursor.execute("""DELETE FROM spiffyrpg_player_effects
                          WHERE id = 3""", params)

    def get_player_intro(self, character_class_id):
        db = self._get_db()
        cursor = db.cursor()

        # character_class_id = ?
        cursor.execute("""SELECT dialogue
                          FROM spiffyrpg_character_dialogue
                          WHERE 1=1
                          AND character_class_id = ?
                          AND dialogue_type = 'intro'
                          ORDER BY RANDOM()
                          LIMIT 1""", (character_class_id,))

        intro = cursor.fetchone()

        if intro is not None:
            return dict(intro)["dialogue"]

    def get_monster_intro(self, monster_id):
        db = self._get_db()
        cursor = db.cursor()

        cursor.execute("""SELECT dialogue
                          FROM spiffyrpg_monster_dialogue
                          WHERE 1=1
                          AND monster_id = ?
                          AND dialogue_type = 'intro'
                          ORDER BY RANDOM()
                          LIMIT 1""", (monster_id,))

        intro = cursor.fetchone()

        if intro is not None:
            return dict(intro)["dialogue"]

    def get_monster_by_class_id(self, class_id):
        db = self._get_db()
        cursor = db.cursor()

        # character_class_id = ?
        cursor.execute("""SELECT id,
                          name AS character_name,
                          description
                          FROM spiffyrpg_monsters
                          WHERE 1=1
                          ORDER BY RANDOM()
                          LIMIT 1""")

        monster = cursor.fetchone()

        if monster is not None:
            return dict(monster)

    def get_finishing_move_by_monster_id(self, monster_id):
        db = self._get_db()
        cursor = db.cursor()

        cursor.execute("""SELECT name
                          FROM spiffyrpg_monster_finishing_moves
                          WHERE monster_id = ?
                          ORDER BY RANDOM()
                          LIMIT 1""", (monster_id,))

        move = cursor.fetchone()

        if move is not None:
            return move["name"]

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

    def get_battle_event(self):
        db = self._get_db()
        cursor = db.cursor()

        cursor.execute("""SELECT name,
                          description
                          FROM spiffyrpg_battle_events
                          WHERE 1=1
                          ORDER BY RANDOM()
                          LIMIT 1""")

        event = cursor.fetchone()

        if event is not None:
            return dict(event)

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

class SpiffyAnnouncer:
    """
    Handles announcing events and other things
    """
    def __init__(self, **kwargs):
        self._irc = kwargs["irc"]

    def announce(self, message):
        self._send_channel_notice(message)

    def _b(self, input):
        return ircutils.bold(input)

    def _c(self, input, text_color):
        return ircutils.mircColor(input, fg=text_color)

    def _get_effect_text(self, input):
        return ircutils.mircColor(input, fg="light blue")

    def _get_role_color(self, role_id):
        role_colors = {
            1: "purple",
            2: "teal",
            3: "yellow"
        }

        return role_colors[role_id]

    def _get_player_role(self, player):
        return ircutils.bold(ircutils.mircColor(player.class_name, \
            self._get_role_color(player.class_id)))

    def _get_player_title(self, unit):
        role_colors = {
            1: "light grey",
            2: "teal",
            3: "yellow"
        }

        bold_title = self._b(unit.title)
        indicator = self._get_unit_indicator(unit)

        if unit.is_player:
            role_color = role_colors[unit.class_id]
            bold_title = self._c(bold_title, role_color)

        title = "%s %s" % (indicator, bold_title)

        return title

    def _get_unit_indicator(self, unit):
        indicator = self._c(u"•", "light gray")

        if unit.is_player:
            indicator = self._c(indicator, "dark blue") 
        else:
            log.info("#%s %s is not a player " % (unit.id, unit.name))

        """ Add NPC here """

        return indicator

    def _get_dungeon_title(self, dungeon):
        return self._c(dungeon.name, "light green")

    def _get_duration(self, seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        existed_timestamp = "%02d:%02d" % (m, s)
 
        if h > 0:
            existed_timestamp = "%d:%s" % (h, existed_timestamp)

        return existed_timestamp

    def dungeon_map(self, **kwargs):
        dungeon = kwargs["dungeon"]
        seconds = int(time.time() - dungeon.created_at)
        duration = self._b(self._get_duration(seconds))
        dungeon_title = self._get_dungeon_title(dungeon)
        units = dungeon.get_living_units()
        unit_count = len(units)
        bold_unit_count = self._b(unit_count)

        announcement_msg = "You are in %s. This dungeon has existed for %s." % \
        (dungeon_title, duration)

        announcement_msg += " %s has %s monsters lurking about" % \
        (dungeon_title, bold_unit_count)

        self.announce(announcement_msg)

    def dungeon_cleared(self, **kwargs):
        dungeon = kwargs["dungeon"]
        player = kwargs["player"]
        xp = kwargs["xp"]

        player_title = self._get_player_title(player)
        formatted_xp = self._b(self._c("{:,}".format(xp), "green"))
        internet_points = self._c("Internet Points", "purple")
        dungeon_name = self._get_dungeon_title(dungeon)
        params = (player_title, formatted_xp, internet_points, dungeon_name)

        announcement_msg = "%s gains %s %s for clearing %s" % params

        self.announce(announcement_msg)

    def dungeon_look(self, **kwargs):
        dungeon = kwargs["dungeon"]
        player = kwargs["player"]
        units = kwargs["units"]
        words = ["looks around", "inspects the surroundings of", 
        "scans the area of"]
        look_phrase = random.choice(words)
        player_name = self._get_player_title(player)
        dungeon_name = self._get_dungeon_title(dungeon)

        if len(units) > 0:
            unit_titles = []
            
            
            msg = "%s %s %s and sees " % \
            (player_name, look_phrase, dungeon_name)
            
            for unit in units:
                unit_name = self._b(unit.name)
                unit_level = self._c(unit.level, "green")
                unit_titles.append("%s (%s)" % (unit_name, unit_level))

            msg += ", ".join(unit_titles)
        else:
            msg = "%s %s %s but sees nothing of import" % \
            (player_name, look_phrase, dungeon_name)

        #self._irc.reply(msg, notice=True)
        self.announce(msg)

    def dungeon_inspect(self, **kwargs):
        dungeon = kwargs["dungeon"]
        player = kwargs["player"]
        target = kwargs["target"]
        levels = kwargs["levels"]

        inspect_target = dungeon.get_unit_by_name(target)

        if inspect_target is not None:
            log.info("SpiffyRPG: inspecting %s" % inspect_target)

            if inspect_target.is_player:
                self.player_info(target, levels)
            else:
                self.unit_info(unit=inspect_target,
                               player=player, 
                               dungeon=dungeon)
        else:
            self.dungeon_look_failure(player=player, 
                                      dungeon=dungeon)

    def dungeon_look_failure(self, **kwargs):
        words = ["looks around", "inspects the surroundings", 
        "scans the area of"]
        look_phrase = random.choice(words)
        player_name = self._get_player_title(kwargs["player"])
        dungeon_name = self._get_dungeon_title(kwargs["dungeon"])

        msg = "%s %s %s but sees nothing of import" % \
        (player_name, look_phrase, dungeon_name)

        self.announce(msg)

    def dungeon_init(self, dungeon):
        """
        %s is now initializing with %s units!
        """
        name = self._b(dungeon.name)
        unit_count = len(dungeon.get_units())
        num_units = self._b(unit_count)
        params = (name, num_units)

        announcement_msg = "%s appears. There seem to be %s monsters lurking about." % params

        self.announce(announcement_msg)

    def unit_spawned(self, unit):
        """
        A level %s %s appears!
        """
        msg = self._c("A level ", "light blue")
        bold_level = self._c(unit.level, "green")
        unit_name = self._c(unit.name, "yellow")

        msg += "%s %s" % (self._b(bold_level), self._b(unit_name))

        msg += self._c(" appears!", "light blue")

        self.announce(msg)

    def new_realm_king(self, player):
        """
        %s the level %s %s is the new Realm King!
        """
        title = self._get_player_title(player)
        level = ircutils.bold(player["level"])
        player_class = self._get_player_role(player)
        params = (title, level, player_class)

        announcement_msg = "%s the level %s %s is the new Realm King!" % params

        self.announce(announcement_msg)

    def top_players(self, top_players, levels):
        for player in top_players:
            self.player_info(player, levels)

    def player_role_change(self, player, role_name, role_id):
        """
        %s is now a level %s %s!
        """
        player_title = self._get_player_title(player)
        params = (player_title, player.get_level())
        msg = "%s is now a level %s" % params
        colored_msg = ircutils.mircColor(msg, fg="brown")
        colored_role = ircutils.mircColor(role_name, self._get_role_color(role_id))
        announcement_msg = "%s %s!" % (colored_msg, colored_role)

        self.announce(announcement_msg)

    def effect_applied_to_player(self, player, effect, duration):
        """
        %s is now affected by %s (%m)
        """
        bold_title = ircutils.bold(player["title"])
        blue_name = self._get_effect_text(effect["name"])
        blue_desc = self._get_effect_text(effect["description"])
        minutes = int(duration / 60)

        effect_name_with_desc = "%s - %s" % (blue_name, blue_desc)

        announcement_msg = "%s is now affected by %s (%sm)" % \
        (bold_title, effect_name_with_desc, minutes)

        self.announce(announcement_msg)

    def player_dialogue(self, player, dialogue, destination=GAME_CHANNEL):
        """
        %s: %s
        """
        bold_title = self._get_player_title(player)
        orange_dialogue = self._c(dialogue, "orange")
        padded_level = str(player.level).zfill(2)
        bold_level = self._b(padded_level)

        params = (bold_level, bold_title, orange_dialogue)
        announcement_msg = "[%s] %s says %s" % params

        self._irc.queueMsg(ircmsgs.notice(destination, announcement_msg))

    def monster_intro(self, monster, intro):
        colored_intro = ircutils.mircColor(intro, fg="orange")
        bold_title = ircutils.bold(monster.title)
        params = (bold_title, colored_intro)
        announcement_msg = "%s: %s" % params

        self._send_channel_notice(announcement_msg)

    def unit_info(self, **kwargs):
        """
        %s is a level %s with %s %s and has existed in %s for %s seconds.
        """
        unit = kwargs["unit"]
        dungeon = kwargs["dungeon"]
        seconds = int(time.time() - unit.created_at)
        duration = self._get_duration(seconds)
        existed = self._b(duration)

        pink_heart = self._c(u"♥", "pink")
        unit_title = self._b(unit.name)
        level = self._b(unit.level)
        hp = self._b(unit.hp)
        body_count = len(unit.slain_foes)
        unit_slain_count = self._c(body_count, "red")
        dungeon_name = self._get_dungeon_title(dungeon)
        foe_word = "foes"

        if body_count == 1:
            foe_word = "foe"

        cname = self._c(unit.class_name, "light green")
        msg = "%s is a level %s %s with %s %s and has " % (unit_title, level, cname, hp, pink_heart)
        msg += "existed in %s for %s. %s has slain %s %s." % \
        (dungeon_name, existed, unit_title, unit_slain_count, foe_word)

        self.announce(msg)

    def player_info(self, player, levels):
        """
        %s is a level %s %s. %s XP remains until %s
        """
        bold_title = self._get_player_title(player)
        bold_class = self._get_player_role(player)

        player_xp = player.experience

        xp_req_for_this_level = player.get_xp_required_for_next_level() + 1
        
        """ If this is one, they're max level """
        if xp_req_for_this_level == 1:
            xp_req_for_this_level = levels[-1][1]

        percent_xp = round(((float(player_xp) / float(xp_req_for_this_level)) * 100), 1)

        if percent_xp <= 20:
            xp_color = "yellow"
        elif percent_xp > 20 and percent_xp < 75:
            xp_color = "white"
        elif percent_xp >= 75:
            xp_color = "green"

        colored_xp = self._c(percent_xp, xp_color)

        # + 1 xp because you don't level until you breach the limit
        formatted_xp = "{:,}".format(xp_req_for_this_level)
        bold_xp_needed_this_level = self._b(formatted_xp)
        bold_next_level = self._b(player.get_level() + 1)
        bold_hp = self._b(player.hp)
        pink_heart = self._c(u"♥", "pink")
        bold_level = self._b(player.get_level())

        # xp gained
        formatted_xp_gained = "{:,}".format(player_xp)
        bold_cur_xp = self._b(formatted_xp_gained)

        # X/X (x%)
        xp_combo = "/".join([bold_cur_xp, bold_xp_needed_this_level])
        xp_combo += " (%s%%)" % (colored_xp)

        params = (bold_title, bold_level, bold_class, bold_hp, pink_heart)
        announcement_msg = "%s is a level %s %s with %s %s" % params
        announcement_msg += " %s to level %s" % \
        (xp_combo, bold_next_level)

        # Effects!
        if len(player.effects):
            log.info("SpiffyRPG: effects: %s" % player.effects)

            effects = []

            for effect in player.effects:
                duration = int((time.time() - effect["expires_at"]) / 60)
                bold_effect_name = ircutils.bold(effect["name"])
                bold_duration = ircutils.bold(duration)
                
                effects.append("%s (%s minutes)" % (bold_effect_name, bold_duration))

            effects_str = ", ".join(effects)

            announcement_msg += ". %s is affected by %s" % (bold_title, effects_str)

        #self._irc.reply(announcement_msg)
        self._send_channel_notice(announcement_msg)

    def player_gained_level(self, player):
        """
        Player_1 has gained level X! 
        """
        params = (self._get_player_title(player), self._b(player.level))

        announcement_msg = "%s ascends to level %s!" % params

        self._send_channel_notice(announcement_msg)

    def new_player(self, char_name, char_class):
        """
        Player_1, the IRC Troll has joined the game!
        """
        params = (self._b(char_name), self._b(char_class))

        announcement_msg = "%s the %s joined the game!" % params

        self._send_channel_notice(announcement_msg)

    def battle_in_progress(self, irc, battle):
        """
        Battle in progress: %s vs %s!
        """
        params = (ircutils.bold(battle["attacker"]["title"]), 
                  ircutils.bold(battle["target"]["title"]))

        announcement_msg = "Battle in progress: %s vs %s!" % params

        self._send_channel_notice(announcement_msg)

    def battle_started(self, irc, attacker, target):
        """
        Battle started! %s vs %s!
        """
        announcement_msg = "Battle started! %s vs %s" % \
        (ircutils.bold(attacker["title"]), ircutils.bold(target["title"]))

        self._send_channel_notice(announcement_msg)

    def title_shuffle(self, title):
        return "%s%s%s" % \
        (title[0], "".join(title[1:-1]).shuffle(), title[-1])

    def player_victory(self, **kwargs):
        """
        $1 reduced to -22 ♥; $2` survived with 60 ♥. $2 gains +15 Internet Points
        """
        player_1 = kwargs["player_1"]
        player_2 = kwargs["player_2"]
        attack = kwargs["attack"]

        green_xp = self._c("{:,}".format(kwargs["xp_gained"]), "green")
        bonus_xp = ""
        internet_points = self._c("Internet Points", "purple")
        pink_heart = self._c(u"♥", "pink")

        #player_1.title = self.title_shuffle(player_1.title)
        #player_2.title = self.title_shuffle(player_2.title)

        player_1_title = self._get_player_title(player_1)
        player_2_title = self._get_player_title(player_2)
        attack_name = self._c(attack["name"], "light green")
        player_2_hp = self._c(player_2.hp, "red")
        player_1_hp = self._c(player_1.hp, "green")

        attack_word = "hit"

        if attack["is_critical_strike"]:
          attack_word = self._b(self._c("critically struck", "red"))

        damage = self._c(attack["damage"], "red")

        params = (player_1_title, attack_name, attack_word, player_2_title, 
        damage, pink_heart, player_2_hp, player_1_title, player_1_hp, pink_heart)

        announcement_msg = "%s's %s %s %s for %s, reducing %s to %s. %s survived with %s %s" % params
        #announcement_msg += "%s attacked % times for %s damage." % ()

        if not player_1.is_monster:
          announcement_msg += ". %s gains %s %s" % (player_1_title, green_xp, internet_points)

        self._send_channel_notice(announcement_msg)

    def last_player_standing(self, player):
        pass

    def player_attack(self, **kwargs):
        danger_low_hp_threshold = 20
        attack_word = "hits"
        player_1 = kwargs["player_1"]
        player_2 = kwargs["player_2"]
        attack = kwargs["attack"]

        if attack["is_critical_strike"]:
            attack_word = ircutils.mircColor("critically strikes", fg="red", bg="black")

        # Check player_1 hp for danger
        if player_1.hp <= danger_low_hp_threshold:
            player_1_hp = self._c(player_1.hp, "red")
        else:
            player_1_hp = self._c(player_1.hp, "green")

        # Check player_2's hp for danger
        if player_2.hp <= danger_low_hp_threshold:
            player_2_hp = self._c(player_2.hp, "red")
        else:
            player_2_hp = self._c(player_2.hp, "green")
        
        """ Formatted attack damage """
        formatted_damage = "{:,}".format(attack["damage"])
        red_damage = self._c(formatted_damage, "red")

        """ Color attack names by whether it's a killing blow """
        if attack["is_killing_blow"]:
            attack_verb = self._b(self._c(attack["name"], "red"))
            you_die = self._b(self._c("You die.", "red"))
        else:
            attack_verb = self._b(self._c(attack["name"], "light green"))
            you_die = ""

        damage_type = attack["damage_type"]
        player_title = self._get_player_title(player_1)
        
        params = (player_title, attack_verb, attack_word, red_damage, 
        damage_type, you_die)

        announcement_msg = "%s's %s %s you for %s %s. %s" % params

        self._send_player_notice(player_2.nick, announcement_msg)

    def _send_player_notice(self, nick, msg):
        self._irc.queueMsg(ircmsgs.notice(nick, msg))

    def _send_channel_notice(self, message):
        """
        All event communication should be sent as a channel notice
        """
        self._irc.queueMsg(ircmsgs.notice(GAME_CHANNEL, message))

class SpiffyBattle:
    party = []
    last_attacker_player_id = None
    attacks = []

    def __init__(self, **kwargs):
        self.party = []
        self.db = kwargs["db"]
        self.announcer = kwargs["announcer"]
        self.player_level = SpiffyPlayerLevel()

    def start(self):
        attacker, opponent = self._get_vs()

        """ Once an attacker is chosen, show them intro dialogue 
        self.announcer.player_dialogue(attacker, 
                                       attacker.get_intro_dialogue(),
                                       GAME_CHANNEL)
                                       #opponent.nick)
        """

        """ Now start round robin """
        self.round_robin(attacker=attacker, 
                         opponent=opponent)

    def round_robin(self, **kwargs):
        """
        The round robin system picks two random living
        players in the party to attack each other. When
        the party is empty, the battle is over.

        1. Choose two party members
        2. If 
        """
        attacker = kwargs["attacker"]
        opponent = kwargs["opponent"]

        if attacker is not None and opponent is not None:
          party_member_count = len(self.party)

          if party_member_count >= 2:
              """ Get an attack """
              attack = attacker.get_attack()

              """ Check if this is a killing blow """
              attack["is_killing_blow"] = (opponent.hp - attack["damage"]) <= 0

              """ Opponent incoming damage """
              opponent.apply_damage(attack["damage"])

              """ Record each attack """
              if attack not in self.attacks:
                  self.attacks.append(attack)

              """ Send attack info privately """
              if not opponent.is_monster:
                """
                self.announcer.player_attack(player_1=attacker, 
                                             player_2=opponent,
                                             attack=attack,
                                             destination=opponent.nick)
                """

              """ If this attack was a killing blow, announce death """
              if attack["is_killing_blow"]:
                  log.info("SpiffyRPG: %s struck killing blow on %s" % \
                    (attacker.title, opponent.title))

              """ After each attack, remove anyone that is dead """
              self.party = self._remove_dead_party_members()

              """ If anyone is left, get another """
              if len(self.party) > 0:
                  vs = self._get_vs()

                  if vs is not None:
                      self.round_robin(attacker=opponent, opponent=attacker)
                  else:
                      last_player_standing = self.party[0]

                      log.info("SpiffyRPG: %s WINS: %s" % \
                      (last_player_standing.title, last_player_standing.hp))
                      
                      log.info("SpiffyRPG: attacker=%s and target=%s" % \
                      (last_player_standing.title, opponent.title))

                      self._on_battle_completed(player_1=last_player_standing,
                                                player_2=opponent,
                                                attack=attack)

          elif party_member_count == 1:
              log.info("SpiffyRPG: one party member left: %s" % self.party[0].title)
              log.info("SpiffyRPG: attacker=%s and target=%s" % (attacker.title, opponent.title))

              self._on_battle_completed(player_1=attacker,
                                        player_2=opponent,
                                        attack=attack)

    def _get_xp_for_battle(self, **kwargs):
        target = kwargs["opponent"]
        xp = int(5 * kwargs["target_player_level"])

        if target.is_monster:
            xp *= 3

        return xp

    def _on_battle_completed(self, **kwargs):      
        log.info("SpiffyRPG: battle concluded")

        attacker = kwargs["player_1"]
        opponent = kwargs["player_2"]
        attack = kwargs["attack"]

        xp = 0

        if not attacker.is_monster:
            xp = self._get_xp_for_battle(target_player_level=attacker.level,
                                         opponent=opponent)
        else:
            attacker.add_slain_foe(opponent)

        self.announcer.player_victory(player_1=attacker, 
                                      player_2=opponent,
                                      attack=attack,
                                      xp_gained=xp,
                                      attacks=self.attacks)

        """ Win dialogue is sent to channel """
        self.announcer.player_dialogue(attacker,
                                       attacker.get_win_dialogue(),
                                       GAME_CHANNEL)

        if not attacker.is_monster:
            log.info("SpiffyRPG: adding %s xp to player %s" % (xp, attacker.name))

            attacker.add_experience(xp)

            attacker.experience += xp

            level_after_adding_xp = self.player_level.get_level_by_xp(attacker.experience)

            if level_after_adding_xp > attacker.level:
                log.info("SpiffyRPG: %s is now level %s!" % (attacker.title, level_after_adding_xp))
                self.announcer.player_gained_level(attacker)

    def _get_vs(self):
        attacker = self._get_party_member(exclude_player_id=self.last_attacker_player_id)

        if attacker is not None:
            opponent = self._get_party_member(exclude_player_id=attacker.id)
          
            self.last_attacker_player_id = attacker.id

            return (attacker, opponent)

    def _remove_dead_party_members(self):
        alive = []

        for p in self.party:
            if p.hp > 0:
                alive.append(p)
            else:
                log.info("SpiffyRPG: party members #%s - %s @ %sHP" % (p.id, p.name, p.hp))

        return alive

    def add_party_member(self, player):
        if player not in self.party:
            log.info("SpiffyRPG: adding %s to party" % player.name)

            self.party.append(player)

    def _get_party_member(self, **kwargs):
      for p in self.party:
          #live_player = p.hp > 0

          #if live_player and p.id != kwargs["exclude_player_id"]:
          if p.id != kwargs["exclude_player_id"]:
              return p

class SpiffyWorld:
  """
  Representation of the world
  """
  dungeons = []

  def __init__(self, **kwargs):
    self.announcer = kwargs["announcer"]
    self.battle = kwargs["battle"]

  def destroy(self):
    log.info("SpiffyRPG: destroying world.")

    for dungeon in self.dungeons:
        dungeon.destroy()

  def start(self):
    self.initialize_dungeons()

  def initialize_dungeons(self):
    if len(self.dungeons) == 0:
      log.info("SpiffyRPG: warning, no dungeons in this world!")

    for dungeon in self.dungeons:
      dungeon.initialize()

  def add_dungeon(self, dungeon):
    if dungeon is not None and dungeon not in self.dungeons:
      self.dungeons.append(dungeon)

  def get_dungeon_by_channel(self, channel):
    for dungeon in self.dungeons:
      if dungeon.channel[1:-1].lower() == channel[1:-1].lower():
        return dungeon

class SpiffyDungeon:
  """
  Representation of a dungeon within the world
  """
  units = []
  max_units = 10

  def __init__(self, **kwargs):
      self.db = kwargs["db"]
      self.announcer = kwargs["announcer"]
      channel = kwargs["channel"]
      dungeon = self.get_dungeon_by_channel(channel)
      
      if dungeon is not None:
          self.player_level = SpiffyPlayerLevel()
          self.created_at = time.time()
          self.id = dungeon["id"]
          self.name = dungeon["name"]
          self.description = dungeon["description"]
          self.min_level = dungeon["min_level"]
          self.max_level = dungeon["max_level"]

          self.channel = dungeon["channel"]
          self.monster_quantity = kwargs["monster_quantity"]

          """ Remove all timers on initialization """
          self.destroy()

          self.start_dialogue_timer()
          self.start_spawn_timer()

          if "max_level" in kwargs:
              self.max_level = kwargs["max_level"]
              log.info("SpiffyRPG: creating dungeon with max level %s" % self.max_level)

      else:
          log.error("SpiffyRPG: unable to find dungeon %s" % (channel,))

  def check_dungeon_cleared(self, player):
      units = self.get_living_units()
      num_units = len(units)
      dungeon_cleared = num_units == 0

      log.info("SpiffyRPG: checking if %s has been cleared" % self.name)

      if dungeon_cleared:
          xp_needed_this_level = self.player_level.get_xp_for_level(player.level)
          xp = int(xp_needed_this_level / 4)

          player.add_experience(xp)

          log.info("SpiffyRPG: adding %s xp to %s" % (xp, player.name))

          self.announcer.dungeon_cleared(dungeon=self,
                                         player=player,
                                         xp=xp)
      else:
          log.info("SpiffyRPG: %s has %s units" % (self.name, num_units))

  def destroy(self):
      log.info("SpiffyRPG: destroying %s" % self.name)
      
      try:
          self.units = []
          schedule.removeEvent("spawn_timer")
          schedule.removeEvent("dialogue_timer")
      except KeyError:
          pass

      self.units = []

  def start_spawn_timer(self):
      log.info("SpiffyRPG: starting monster spawn interval")

      spawn_interval = 300

      schedule.addPeriodicEvent(self.check_population,
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

      dialogue_interval = 600

      schedule.addPeriodicEvent(self.random_monster_dialogue,
                                dialogue_interval,
                                name="dialogue_timer",
                                now=False)

  def random_monster_dialogue(self):
      log.info("SpiffyRPG: monster talkin'")

      """ Add random chance here """
      units = self.get_living_units()

      if len(units) > 0:
          dialogue_chance = random.randrange(1, 20) < 100

          if dialogue_chance:
              unit = random.choice(units)

              dialogue = unit.get_intro_dialogue()

              self.announcer.player_dialogue(unit,
                                             dialogue,
                                             self.channel)
          else:
              log.info("SpiffyRPG: dialoguing by not random enough")
      else:
          log.info("SpiffyRPG: no units in %s, not dialoguing" % self.name)

  def initialize(self, **kwargs):
      """
      Later on we can add a dungeon id here to customize the 
      monsters spawned. Maybe make the base monster count a db 
      column.
      """
      if self.id:
          log.info("SpiffyRPG: initializing dungeon #%s - %s with %s monsters" \
          % (self.id, self.name, self.monster_quantity))

          self.populate(self.monster_quantity)
          self.announcer.dungeon_init(self)
      else:
        log.error("Cannot populate - no dungeon found.")

  def get_dungeon_by_channel(self, channel):
      cursor = self.db.cursor()

      cursor.execute("""SELECT id, 
                        name, channel, description, 
                        min_level, max_level
                        FROM spiffyrpg_dungeons
                        WHERE 1=1
                        AND channel = ?
                        LIMIT 1""", (channel.lower(),))

      dungeon = cursor.fetchone()
      
      cursor.close()

      if dungeon is not None:
          return dict(dungeon)

  def get_dungeon_by_id(self, id):
      cursor = self.db.cursor()

      cursor.execute("""SELECT id, name
                        FROM spiffyrpg_dungeons
                        WHERE 1=1
                        AND id = ?
                        LIMIT 1""", (id,))

      dungeon = cursor.fetchone()
      
      cursor.close()

      if dungeon is not None:
          return dict(dungeon)

  def populate(self, monster_quantity):
      """ Add random monsters monsters """
      monster_db = SpiffyMonsterDB(db=self.db)

      monsters = monster_db.spawn_many(monster_quantity=monster_quantity,
                                       min_level=self.min_level,
                                       max_level=self.max_level)

      if monsters is not None and len(monsters) > 0:
          for monster in monsters:
              log.info("SpiffyRPG: spawning a level %s %s with %s HP in %s" % \
              (monster.level, monster.name, monster.hp, self.name))

              self.add_unit(monster)
      else:
          log.info("SpiffyRPG: couldn't find any monsters to populate dungeon")

  def add_unit(self, unit):
      """
      self.announcer.unit_spawned(unit)
      """
      if unit not in self.units:
          self.units.append(unit)
      else:
          log.info("SpiffyRPG: not adding duplicate unit %s" % (unit.name))

  def remove_unit(self, unit):
      units = []

      log.info("SpiffyRPG: [%s] Unit %s#%s died" % (self.name, unit.name, unit.id))

      for u in self.units:
          if unit.id != u.id:
              units.append(u)

      self.units = units

  def get_unit_by_name(self, name):
      for unit in self.units:
          if unit.name.lower() == name.lower():
              return unit

  def get_living_units(self):
      alive = []

      for unit in self.units:
          if unit.hp > 0:
              alive.append(unit)

      if len(alive) > 0:
          alive = sorted(alive, key=lambda x: x.level, reverse=True)

      return alive

  def get_units(self):
      units = self.units

      if len(units) > 0:
          units = sorted(units, key=lambda x: x.level, reverse=True)

      return units

class SpiffyMonsterDB:
    """
    DB operations for multiple monsters
    """
    def __init__(self, **kwargs):
        self.db = kwargs["db"]

    def _get_monster_ids(self, **kwargs):
        """
        Fetches random monsters with a limit
        """
        cursor = self.db.cursor()
        limit = int(kwargs["limit"])

        query = """SELECT id
                   FROM spiffyrpg_monsters
                   WHERE 1=1
                   ORDER BY RANDOM() 
                   LIMIT %s""" % (limit,)

        cursor.execute(query)
        ids = cursor.fetchall()

        if ids is not None:
            id_list = []

            for i in ids:
              id_list.append(str(dict(i)["id"]))

            return id_list

        cursor.close()

    def spawn_many(self, **kwargs):
        cursor = self.db.cursor()
        monster_ids = self._get_monster_ids(limit=kwargs["monster_quantity"])

        if monster_ids is not None:
          comma_separated_string = ",".join(monster_ids)
          params = (comma_separated_string,)

          cursor.execute("""SELECT
                            m.id, 
                            m.name AS class_name,
                            un.name AS name
                            FROM spiffyrpg_monsters m
                            JOIN spiffyrpg_unit_names un ON un.unit_id = m.id
                            WHERE 1=1
                            AND m.id IN (%s)""" % params)

          monsters = cursor.fetchall()
          
          if len(monsters) > 0:
              augmented_monsters = []

              for m in monsters:
                  monster = dict(m)

                  """ 
                  The monster level is generated according to the level
                  range of the dungeon
                  """
                  augmented_monster = SpiffyMonster(min_level=kwargs["min_level"],
                                                    max_level=kwargs["max_level"],                                           
                                                    monster=monster,
                                                    db=self.db)

                  augmented_monsters.append(augmented_monster)

              return augmented_monsters

        else:
          log.error("SpiffyRPG: problem finding monsters")

        cursor.close()

class SpiffyMonster:
    """
    A monster!
    """
    def __init__(self, **kwargs):
        self.db = kwargs["db"]

        min_level = kwargs["min_level"]
        max_level = kwargs["max_level"]

        self.level = random.randrange(min_level, max_level)      
        self.hp = self.level * 20
        self.critical_strike_chance = random.randrange(10, 20)
        self.id = kwargs["monster"]["id"]
        self.name = kwargs["monster"]["name"]
        self.title = kwargs["monster"]["name"]
        self.is_monster = True
        self.is_player = False
        self.created_at = time.time()
        self.slain_foes = []
        self.class_name = kwargs["monster"]["class_name"]

    def add_slain_foe(self, foe):
        if foe not in self.slain_foes:
            self.slain_foes.append(foe)

    def get_attack(self):
        cursor = self.db.cursor()

        cursor.execute("""SELECT name
                          FROM spiffyrpg_monster_abilities
                          WHERE monster_id = ?
                          ORDER BY RANDOM()
                          LIMIT 1""", (self.id,))

        ability = cursor.fetchone()

        cursor.close()

        if ability is not None:
            a = dict(ability)

            a["damage"] = self._get_attack_damage()
            a["is_critical_strike"] = self.is_critical_strike()
            a["damage_type"] = random.choice(["Physical", "Magic"])

            return a

    def _get_attack_damage(self, **kwargs):
        return random.randrange(5, 10) * self.level

    def get_finishing_move(self):
        cursor = self.db.cursor()
        cursor.execute("""SELECT name
                          FROM spiffyrpg_monster_finishing_moves
                          WHERE monster_id = ?
                          ORDER BY RANDOM()
                          LIMIT 1""", (monster_id,))

        move = cursor.fetchone()
        
        cursor.close()

        if move is not None:
            return move["name"]

    def get_win_dialogue(self):
        cursor = self.db.cursor()

        cursor.execute("""SELECT dialogue
                          FROM spiffyrpg_monster_dialogue
                          WHERE 1=1
                          AND dialogue_type = 'win'
                          AND monster_id = ?
                          ORDER BY RANDOM()
                          LIMIT 1""", (self.id,))

        dialogue = cursor.fetchone()
        cursor.close()

        if dialogue is not None:
            return dialogue["dialogue"]

    def get_intro_dialogue(self,):
        cursor = self.db.cursor()

        cursor.execute("""SELECT dialogue
                          FROM spiffyrpg_monster_dialogue
                          WHERE 1=1
                          AND dialogue_type = 'intro'
                          AND monster_id = ?
                          ORDER BY RANDOM()
                          LIMIT 1""", (self.id,))

        dialogue = cursor.fetchone()
        cursor.close()

        if dialogue is not None:
            return dialogue["dialogue"]

    def is_critical_strike(self):
        return random.randrange(0, 100) < self.critical_strike_chance

    def get_title(self):
        self.monster["character_name"]

    def apply_damage(self, hp):
        self.hp = int(self.hp - hp)

        log.info("SpiffyRPG: %s takes %s damage; now has %sHP" % (self.title, hp, self.hp))

    def is_killing_blow(self, **kwargs):
        hp = self.hp

        return (hp - damage) > 0

    def is_alive(self):
        return self.hp > 0

class SpiffyPlayer:
    """
    Represents a player in SpiffyRPG and manages
    state information about the player
    """
    def __init__(self, **kwargs):
        self._announcer = kwargs["announcer"]
        self.db = kwargs["db"]
        self.player_level = SpiffyPlayerLevel()
        self.player_class = SpiffyPlayerClass()
        self.nick = kwargs["nick"]
        self.id = kwargs["player"]["id"]
        self.class_name = kwargs["player"]["class_name"]
        self.name = kwargs["player"]["character_name"]
        self.is_monster = False
        self.is_player = True

        self.class_id = kwargs["player"]["character_class_id"]
        xp = kwargs["player"]["experience_gained"]
        self.experience = xp
        self.level = self.get_level()
        self.hp = self._get_hp()
        self.title = kwargs["player"]["character_name"]
        self.is_vulnerable_to_magic = self.player_class.is_vulnerable_to_magic(self.class_id)
        self.is_vulnerable_to_physical = self.player_class.is_vulnerable_to_physical(self.class_id)
        self.effects = self.get_effects()

    def get_xp_required_for_next_level(self):
        return self.player_level.get_xp_for_next_level(self.level)

    def get_level(self):
        return self.player_level.get_level_by_xp(self.experience)

    def get_title(self):
        return self.name

    def apply_damage(self, damage):
        is_vulnerable_to_magic = self.player_class.is_vulnerable_to_magic(self.class_id)
        is_vulnerable_to_physical = self.player_class.is_vulnerable_to_physical(self.class_id)
        
        if is_vulnerable_to_physical or is_vulnerable_to_magic:
            damage *= 1.2

        self.hp = int(self.hp - damage)

        log.info("SpiffyRPG: %s - %s = %s" % (self.title, damage, self.hp))

    def get_items(self):
        return self.items

    def set_title(self, title):
        self.title = title
        self.name = title

        log.info("Player %s sets title to %s" % (self.id, self.title))

        cursor = self.db.cursor()
        params = (title, self.id)

        cursor.execute("""UPDATE spiffyrpg_players
                          SET character_name = ?
                          WHERE id = ?""", 
                       params)

        self.db.commit()
        cursor.close()

    def add_experience(self, experience):
        log.info("Player %s adding %s xp" % (self.title, experience))

        cursor = self.db.cursor()
        params = (experience, self.id)

        cursor.execute("""UPDATE spiffyrpg_players
                          SET experience_gained = experience_gained + ?
                          WHERE id = ?""", 
                       params)

        self.db.commit()
        cursor.close()

    def get_effects(self):
        cursor = self.db.cursor()
        now = time.time()

        cursor.execute("""SELECT e.id,
                          e.name,
                          e.description,
                          e.operator,
                          e.hp_percent_adjustment,
                          e.critical_strike_chance_adjustment,
                          e.damage_percent_adjustment,
                          e.chance_to_hit_adjustment,
                          p.expires_at
                          FROM spiffyrpg_effects e
                          JOIN spiffyrpg_player_effects p ON p.effect_id = e.id
                          WHERE 1=1
                          AND p.expires_at > ?
                          AND p.player_id = ?
                          ORDER BY name""", (now, self.id,))

        effects = cursor.fetchall()

        cursor.close()

        if effects:
          return effects
        else:
          return []

    def get_attack(self):
        cursor = self.db.cursor()

        cursor.execute("""SELECT name
                          FROM spiffyrpg_class_abilities
                          WHERE character_class_id = ?
                          AND min_level <= ?
                          ORDER BY RANDOM()
                          LIMIT 1""", (self.class_id, self.level))

        ability = cursor.fetchone()
        cursor.close()

        if ability is not None:
            a = dict(ability)

            a["damage"] = self._get_attack_damage()
            a["is_critical_strike"] = self.is_critical_strike()
            a["damage_type"] = self._get_damage_type()

            return a
    
    def _get_damage_type(self):
        internet_tough_guy = 2
        black_hat = 3

        if self.class_id in (2, 3):
          return "Physical"
        else:
          return "Magic"

    def _get_attack_damage(self, **kwargs):
        return random.randrange(1, 5) * self.level

    def get_finishing_move(self):
        cursor = self.db.cursor()

        cursor.execute("""SELECT name
                          FROM spiffyrpg_class_finishing_moves
                          WHERE character_class_id = ?
                          AND min_level <= ?
                          ORDER BY RANDOM()
                          LIMIT 1""", (self.character_class_id, self.level))

        move = cursor.fetchone()
        cursor.close()

        if move is not None:
            return move["name"]

    def get_intro_dialogue(self):
        cursor = self.db.cursor()

        cursor.execute("""SELECT dialogue
                          FROM spiffyrpg_character_dialogue
                          WHERE 1=1
                          AND character_class_id = ?
                          AND dialogue_type = 'intro'
                          ORDER BY RANDOM()
                          LIMIT 1""", (self.class_id,))

        intro = cursor.fetchone()
        cursor.close()

        if intro is not None:
            return dict(intro)["dialogue"]

    def get_win_dialogue(self):
        cursor = self.db.cursor()

        cursor.execute("""SELECT dialogue
                          FROM spiffyrpg_character_dialogue
                          WHERE 1=1
                          AND character_class_id = ?
                          AND dialogue_type = 'win'
                          ORDER BY RANDOM()
                          LIMIT 1""", (self.class_id,))

        intro = cursor.fetchone()
        cursor.close()

        if intro is not None:
            return dict(intro)["dialogue"]

    def _get_hp(self):
        return self.level * 20

    def _get_critical_strike_chance(self):
        OPEN_SOURCE_CONTRIBUTOR = 3

        if self.class_id == OPEN_SOURCE_CONTRIBUTOR:
            return 25
        else:
            return 5

    def is_critical_strike(self):
        return random.randrange(0, 100) < self._get_critical_strike_chance()

class SpiffyPlayerLevel:
    """
    Functionality related to player levels, total levels, etc
    """
    def get_level_by_xp(self, total_experience):
        player_level = 1
        levels = self.get_levels()
 
        for level, experience_needed in levels:
            if total_experience > experience_needed:
                player_level = level

        """ If this player is max level or higher, just choose last one """
        if total_experience > levels[-1][1]:
            player_level = levels[-1][0]

        return player_level

    def get_xp_for_level(self, player_level):
        xp = 1
        levels = self.get_levels()
 
        for level, experience_needed in levels:
            if level == player_level:
                return experience_needed

        return player_level

    def get_xp_for_next_level(self, level):
        xp = 0
        levels = self.get_levels()

        for xp_level, req_xp in levels:
            if xp_level == (level+1):
                xp = req_xp
                break

        return xp

    def get_levels(self):
        return [(1, 0),
                (2, 100),
                (3, 200),
                (4, 300),
                (5, 400),
                (6, 1000),
                (7, 1500),
                (8, 2500),
                (9, 3500),
                (10, 5000),
                (11, 6500),
                (12, 8000),
                (13, 9500),
                (14, 10500),
                (15, 12000),
                (16, 15000),
                (17, 18000),
                (18, 21000),
                (19, 24000),
                (20, 27000),
                (21, 30000),
                (22, 33000),
                (24, 36000),
                (25, 39000),
                (26, 42000),
                (27, 45000),
                (28, 48000),
                (29, 51000),
                (30, 54000),
                (31, 57000),
                (32, 60000),
                (33, 63000),
                (34, 66000),
                (35, 69000)
      ]

class SpiffyPlayerClass:
    """
    Represents different propertes of each class
    """
    OPEN_SOURCE_CONTRIBUTOR = 1
    INTERNET_TOUGH_GUY = 2
    BLACK_HAT = 3

    def is_vulnerable_to_magic(self, class_id):
        return class_id in (2, 3)

    def is_vulnerable_to_physical(self, class_id):
        return class_id == 1

    def get_damage_type(self, class_id):
        if class_id in (2, 3):
            return "Physical"
        else:
            return "Magic"

class SpiffyRPG(callbacks.Plugin):
    """A gluten-free IRC RPG"""
    threaded = True
    battle_in_progress = False
    realm_king_player_id = None
    
    def __init__(self, irc):
        self.__parent = super(SpiffyRPG, self)
        self.__parent.__init__(irc)

        self.announcer = SpiffyAnnouncer(irc=irc)
        self.player_class = SpiffyPlayerClass()
        self.player_level = SpiffyPlayerLevel()
        self.db = SpiffyRPGDB()
        self.battle = SpiffyBattle(db=self.db._get_db(),
                                   announcer=self.announcer)

        self.character_classes = self.db.get_character_classes()

        self.SpiffyWorld = SpiffyWorld(announcer=self.announcer,
                                       battle=self.battle)

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

    def _get_character_class_list(self):
        class_list = []

        for c in self.character_classes:
            class_list.append(ircutils.bold(c["name"]))

        return ", ".join(class_list)

    def _get_character_class_id_by_name(self, class_name):
        for c in self.character_classes:
            if c["name"].lower() == class_name.lower():
                return c["id"]

    def _init_world(self, a_channel):
        self.SpiffyWorld.destroy()

        max_xp = self.db.get_max_player_level()
        max_level = self.player_level.get_level_by_xp(max_xp)

        dungeon = SpiffyDungeon(channel=a_channel, 
                                db=self.db._get_db(),
                                announcer=self.announcer,
                                monster_quantity=10,
                                max_level=max_level)

        log.info("Initializing world with dungeon #%s" % dungeon.id)

        self.SpiffyWorld.add_dungeon(dungeon)
        self.SpiffyWorld.start()

    def inspect(self, irc, msg, args, user, target):
        """
        Inspects a unit or item
        """
        channel = msg.args[0]
        
        if ircutils.isChannel(channel):
            user_id = self._get_user_id(irc, msg.prefix)

            if user_id:
                p = self.db.get_player_by_user_id(user_id)

                if p is not None:
                    player = SpiffyPlayer(player=p, 
                                          db=self.db._get_db(), 
                                          announcer=self.announcer,
                                          nick=msg.nick)

                    dungeon = self.SpiffyWorld.get_dungeon_by_channel(channel)

                    if dungeon is not None:
                        unit = dungeon.get_unit_by_name(target)

                        """ Used for player info """
                        levels = self.player_level.get_levels()

                        self.announcer.dungeon_inspect(dungeon=dungeon,
                                                       target=target,
                                                       player=player,
                                                       levels=levels)
    inspect = wrap(inspect, ["user", "text"])

    def look(self, irc, msg, args, user):
        """
        Look around for anything of note nearby
        """
        channel = msg.args[0]
        
        if ircutils.isChannel(channel):
            user_id = self._get_user_id(irc, msg.prefix)

            if user_id:
                p = self.db.get_player_by_user_id(user_id)

                if p is not None:
                    player = SpiffyPlayer(player=p, 
                                          db=self.db._get_db(), 
                                          announcer=self.announcer,
                                          nick=msg.nick)

                    dungeon = self.SpiffyWorld.get_dungeon_by_channel(channel)

                    if dungeon is not None:
                        units = dungeon.get_living_units()
                        self.announcer.dungeon_look(dungeon=dungeon, 
                                                    player=player,
                                                    units=units)
    
    look = wrap(look, ["user"])

    def smap(self, irc, msg, args, user):
        """
        Examine your map to see where you are
        """
        channel = msg.args[0]
        
        if ircutils.isChannel(channel):
            user_id = self._get_user_id(irc, msg.prefix)

            if user_id:
                p = self.db.get_player_by_user_id(user_id)

                if p is not None:
                    player = SpiffyPlayer(player=p, 
                                          db=self.db._get_db(), 
                                          announcer=self.announcer,
                                          nick=msg.nick)

                    dungeon = self.SpiffyWorld.get_dungeon_by_channel(channel)

                    if dungeon is not None:
                        self.announcer.dungeon_map(dungeon=dungeon, 
                                                   player=player)
                    else:
                        irc.error("Dungeon not found!")
                else:
                  irc.error("Could not look up your player")
    
    smap = wrap(smap, ["user"])

    def title(self, irc, msg, args, user, title):
        """
        title <new title> - sets a new title for your character. Maximum 16 characters
        """
        is_channel = irc.isChannel(msg.args[0])

        if is_channel:
            user_id = self._get_user_id(irc, msg.prefix)
            p = self.db.get_player_by_user_id(user_id)

            if p is not None:
                player = SpiffyPlayer(player=p, 
                                      db=self.db._get_db(), 
                                      announcer=self.announcer,
                                      nick=msg.nick)

                player.set_title(title[0:15])

                levels = self.player_level.get_levels()

                self.announcer.player_info(player, levels)

    title = wrap(title, ["user", "text"])

    def attack(self, irc, msg, args, user, target):
        """
        attack <target> - Attack a non-player target in the dungeon
        """
        is_channel = irc.isChannel(msg.args[0])

        if is_channel:
            user_id = self._get_user_id(irc, msg.prefix)
            p = self.db.get_player_by_user_id(user_id)

            if p is not None:
                player = SpiffyPlayer(player=p, 
                                      db=self.db._get_db(), 
                                      announcer=self.announcer,
                                      nick=msg.nick)

                channel = msg.args[0]
                dungeon = self.SpiffyWorld.get_dungeon_by_channel(channel)

                if dungeon is not None:
                    unit = dungeon.get_unit_by_name(target)

                    if unit is not None:
                        log.info("SpiffyRPG: found unit with name %s" % unit.name)

                        battle = SpiffyBattle(db=self.db._get_db(),
                                              announcer=self.announcer)

                        battle.add_party_member(player)
                        battle.add_party_member(unit)
                        battle.start()

                        #dungeon.clear_dead_units()
                        dungeon.check_dungeon_cleared(player)
                        #dungeon.check_population()
                    else:
                      irc.error("You try to attack %s, but realize nothing is there" % ircutils.bold(target))
                else:
                    irc.error("Couldn't find dungeon with channel %s" % (channel))
            else:
                log.info("SpiffyRPG: non-player %s tried to attack" % player.title)
        else:
            irc.error("You must attack non-player units in the channel.")

    attack = wrap(attack, ["user", "text"])

    def sbattle(self, irc, msg, args, user, target_nick):
        """
        Battles another user: !sbattle <nick>
        """
        is_channel = irc.isChannel(msg.args[0])

        if is_channel:
          irc.error("Start battles in PM: /msg %s b %s" % (irc.nick, target_nick))
          return

        if not target_nick:
            target_nick = msg.nick

        attacker_user_id = self._get_user_id(irc, msg.prefix)
        is_target_same_as_attacker = msg.nick.lower() == target_nick.lower()

        if is_target_same_as_attacker:
            irc.reply("You attempt to attack yourself, but fail because you love yourself too much.")
            return

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
            irc.error("That user has not yet joined the realm.")
            return
 
        db = self.db._get_db()

        player_1 = SpiffyPlayer(player=attacker, 
                                db=db, 
                                announcer=self.announcer,
                                nick=msg.nick)

        player_2 = SpiffyPlayer(player=target, 
                                db=db, 
                                announcer=self.announcer,
                                nick=target_nick)

        self.battle.add_party_member(player_1)
        self.battle.add_party_member(player_2)
        self.battle.start()

    sbattle = wrap(sbattle, ["user", optional("text")])

    def srank(self, irc, msg, args):
        """
        Shows top 3 players by experience gained
        """
        tmp_players = self.db.get_top_players_by_xp()
        top_players = []
        db = self.db._get_db()

        if len(tmp_players) > 0:
            for p in tmp_players:
                d_p = dict(p)
                
                player = SpiffyPlayer(player=d_p, db=db, announcer=self.announcer,
                                nick=msg.nick)

                top_players.append(player)

            levels = self.player_level.get_levels()
            self.announcer.top_players(top_players, levels)
        else:
            irc.error("There are no players yet!")

    srank = wrap(srank)
    
    def srole(self, irc, msg, args, user, role):
        """
        Changes your role to something else
        """
        user_id = self._get_user_id(irc, msg.prefix)
        
        if user_id is not None:
            p = self.db.get_player_by_user_id(user_id)

            log.info("SpiffyRPG: %s changing to %s" % (p, role))

            if p is not None:
                player = SpiffyPlayer(player=p, db=self.db._get_db(), announcer=self.announcer,
                nick=msg.nick)
                class_id = self._get_character_class_id_by_name(role)

                if class_id is not None:
                    self.db.update_player_role(player.id, class_id)
                    
                    self.announcer.player_role_change(player, role, class_id)
                else:
                    classes = self._get_character_class_list()

                    irc.error("Please choose one of the following roles: %s" % classes)
            else:
                irc.error("You ain't no playa! Step off, homie.")

    srole = wrap(srole, ["user", "text"])

    def sinfo(self, irc, msg, args, target_nick):
        """
        Shows information about a player
        """
        if not target_nick:
            target_nick = msg.nick

        if not self._is_nick_in_channel(irc, target_nick):
            irc.error("I don't see that nick here")
            return

        info_target = msg.nick
        target_hostmask = irc.state.nickToHostmask(target_nick)
        user_id = self._get_user_id(irc, target_hostmask)
        
        if user_id is not None:
            player = self.db.get_player_by_user_id(user_id)
            db = self.db._get_db()

            player = SpiffyPlayer(player=player, db=db, announcer=self.announcer,
                            nick=msg.nick)
            levels = self.player_level.get_levels()

            if player is not None:
                self.announcer.player_info(player, levels)
            else:
                irc.error("That user has not joined the game :(")
        else:
            irc.error("I could not find anything on that user.")

    sinfo = wrap(sinfo, [optional("text")])

    def seffect(self, irc, msg, args, user, effect):
        """
        Applies an affect to target user
        """
        user_id = self._get_user_id(irc, msg.prefix)

        # user id should always be valid due to wrapper
        player = self.db.get_player_by_user_id(user_id)

        if player is None:
            irc.error("You don't seem to be registered. Please use !sjoin")          
            return

        effect = self.db.get_effect_by_name(effect)

        if effect is not None:
            five_minutes = 300
            two_minutes = 120
            duration = time.time() + five_minutes

            player["title"] = self._get_player_title(player)
            self.db.add_effect_battle_fatigue(player["id"], duration)
            self.announcer.effect_applied_to_player(irc, player, effect, duration)
        else:
            irc.error("I couldn't find an effect with that name")

    seffect = wrap(seffect, ["user", "text"])

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
                        irc.queueMsg(ircmsgs.voice(GAME_CHANNEL, msg.nick))
                    else:
                        log.error("SpiffyRPG: error determining class id from '%s'" % character_class)

                else:
                    classes = self._get_character_class_list()
                    irc.reply("Please choose one of the following classes: %s" % classes)

    sjoin = wrap(sjoin, ["user", "text"])

    """ Admin-only commands """

    def fdungeoninit(self, irc, msg, args, channel):
        """
        fdungeoninit - force a dungeon to reinitialize
        """
        if ircutils.isChannel(channel):
            self._init_world(channel)
        else:
            irc.error("No dungeons with that channel")

    fdungeoninit = wrap(fdungeoninit, ["text"])

    def fmove(self, irc, msg, unit, position):
        """
        fmove unitID positionID - Moves a unit to specified position
        """
        pass

    fmove = wrap(fmove, ["text"])

    def doPart(self, irc, msg):
      pass

    def doKick(self, irc, msg):
      pass

    def doJoin(self, irc, msg):
        """
        Announces players joining
        """
        is_bot_joining = msg.nick == irc.nick
        
        if is_bot_joining:
          channel = msg.args[0]

          """ Bot joined. Start world/dungeon """
          log.info("SpiffyRPG: bot joined %s - starting dungeon" % channel)

          self._init_world(channel)
        else:
          user_id = self._get_user_id(irc, msg.prefix)

          if user_id:
              player = self.db.get_player_by_user_id(user_id)

              if player is not None:
                  player = SpiffyPlayer(player=player, db=self.db._get_db(),
                  announcer=self.announcer, nick=msg.nick)

                  levels = self.player_level.get_levels()

                  self.announcer.player_info(player, levels)
                  irc.queueMsg(ircmsgs.voice(GAME_CHANNEL, msg.nick))

Class = SpiffyRPG


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
