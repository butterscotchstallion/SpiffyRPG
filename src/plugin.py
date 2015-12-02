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

class SpiffyAnnouncer(object):
    """
    There are two types of announcements:
    1. Dungeon (Public) - announcements made in the channel. SpiffyDungeonAnnouncer
       fulfills this role.
    2. Player (Private) - announcements made directly to the player

    The destination of the announcement is set when the announcer
    is instantiated.
    """
    is_public = True

    def __init__(self, **kwargs):
        self._irc = kwargs["irc"]
        self.is_public = kwargs["public"]
        self.destination = kwargs["destination"]
        unit_levels = SpiffyUnitLevel()
        self.levels = unit_levels.get_levels()

    def _get_player_role(self, player):
        role = player.get_title()
        role_color = self._get_role_color(player.unit_type_id)
        
        return self._b(self._c(role, role_color))

    def _get_unit_title(self, unit):
        role_colors = {
            1: "light grey",
            2: "teal",
            3: "yellow"
        }

        bold_title = self._b(unit.name)
        indicator = self._get_unit_indicator(unit)

        if unit.is_player and unit.unit_type_id in role_colors:
            role_color = role_colors[unit.unit_type_id]
            bold_title = self._c(bold_title, role_color)

        title = "%s %s" % (indicator, bold_title)

        return title

    def _get_role_color(self, role_id):
        role_colors = {
            1: "green",
            5: "purple",
            2: "teal",
            3: "yellow",
            7: "brown"
        }

        return role_colors[role_id]

    def _get_unit_indicator(self, unit):
        indicator = self._c(u"•", "light gray")

        if unit.is_player:
            indicator = self._c(indicator, "dark blue") 
        else:
            log.info("#%s %s is not a player " % (unit.id, unit.get_title()))

        """ Add NPC here """

        return indicator

    def _get_item_type_indicator(self, item_type):
        indicator = ""
        lower_item_type = item_type.lower()

        if lower_item_type == "rock":
            indicator = "R"
        elif lower_item_type == "paper":
            indicator = "P"
        elif lower_item_type == "scissors":
            indicator = "S"
        elif lower_item_type == "lizard":
            indicator = "L"
        elif lower_item_type == "spock":
            indicator = "V"

        return self._b(indicator)

    def announce(self, message):
        if self.is_public:
            self._send_channel_notice(message)
        else:
            self._send_player_notice(message)

    def _b(self, input):
        return ircutils.bold(input)

    def _c(self, input, text_color):
        return ircutils.mircColor(input, fg=text_color)

    def _get_effect_text(self, input):
        return ircutils.mircColor(input, fg="light blue")

    def _get_duration(self, seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        existed_timestamp = "%02d:%02d" % (m, s)
 
        if h > 0:
            existed_timestamp = "%d:%s" % (h, existed_timestamp)

        return existed_timestamp

    def _send_player_notice(self, message):
        self._irc.queueMsg(ircmsgs.notice(self.destination, message))

    def _send_channel_notice(self, message):
        """
        All event communication should be sent as a channel notice
        """
        self._irc.queueMsg(ircmsgs.notice(GAME_CHANNEL, message))

class SpiffyBattle:
    def __init__(self, **kwargs):
        self.party = []
        self.db = kwargs["db"]
        self.announcer = SpiffyBattleAnnouncer(irc=kwargs["irc"],
                                               destination=kwargs["destination"],
                                               public=True)
        self.unit_level = SpiffyUnitLevel()
    
    def is_hit(self, **kwargs):
        """
        Get the attacker and target weapon type,
        and determine who wins the round. The winner
        of the round deals damage
        """
        attacker = kwargs["attacker"]
        target = kwargs["target"]
        is_hit = False
        is_draw = False
        hit_word = "draw"

        """ Attacker weapon """
        attacker_weapon = attacker.get_equipped_weapon()
        attacker_weapon_type = attacker_weapon["item_type"]

        """ Target weapon """
        target_weapon = target.get_equipped_weapon()
        target_weapon_type = target_weapon["item_type"]

        """ Rock crushes Scissors """
        if attacker_weapon_type == "rock" and \
        target_weapon_type == "scissors":
            is_hit = True
            hit_word = "crushes"

        """ Scissors cuts Paper """
        if attacker_weapon_type == "scissors" and \
        target_weapon_type == "paper":
            is_hit = True
            hit_word = "cuts"

        """ Paper covers Rock """
        if attacker_weapon_type == "paper" and \
        target_weapon_type == "rock":
            is_hit = True
            hit_word = "covers"

        """ Lizard eats Paper """
        if attacker_weapon_type == "lizard" and \
        target_weapon_type == "paper":
            is_hit = True
            hit_word = "eats"

        """ Spock vaporizes Rock """
        if attacker_weapon_type == "spock" and \
        target_weapon_type == "rock":
            is_hit = True
            hit_word = "vaporizes"

        """ Lizard poisons Spock """
        if attacker_weapon_type == "lizard" and \
        target_weapon_type == "spock":
            is_hit = True
            hit_word = "poisons"

        """ Rock crushes Lizard """
        if attacker_weapon_type == "rock" and \
        target_weapon_type == "lizard":
            is_hit = True
            hit_word = "crushes"

        """ Spock smashes Scissors """
        if attacker_weapon_type == "spock" and \
        target_weapon_type == "scissors":
            is_hit = True
            hit_word = "smashes"

        """ Paper disproves Spock """
        if attacker_weapon_type == "paper" and \
        target_weapon_type == "spock":
            is_hit = True
            hit_word = "disproves"

        """ Scissors decapitate Lizard """
        if attacker_weapon_type == "scissors" and \
        target_weapon_type == "lizard":
            is_hit = True
            hit_word = "decapitates"

        """ Draw! """
        if attacker_weapon_type == target_weapon_type:
            is_draw = True

        log.info("SpiffyRPG: %s's %s vs %s's %s: hit is %s" % \
        (attacker.name, attacker_weapon_type, target.name, target_weapon_type, is_hit))

        return {
            "is_hit": is_hit,
            "attacker_weapon": attacker_weapon,
            "target_weapon": target_weapon,
            "is_draw": is_draw,
            "hit_word": hit_word
        }

    def start(self):
        """
        Once an attacker is chosen, show them intro dialogue
        self.announcer.unit_dialogue(attacker, 
                                       attacker.dialogue_intro(),
                                       GAME_CHANNEL)
                                       #opponent.nick)
        """
        attacker = self.party[0]
        target = self.party[1]

        """
        We initialize this way because in the case of a draw,
        we're going to randomize the winner/loser anyway. If
        it's not a draw, then winner and loser will be 
        overwritten appropriately.
        """
        winner = attacker
        loser = target

        """
        Check if the attacker hit. If the attacker hits successfully,
        the round is over. If not, the target has an opportunity to
        strike.
        """
        hit_info = self.is_hit(attacker=attacker,
                               target=target)

        """
        In the case of a draw, there will be no attack info,
        as there was no attack!
        """
        attack_info = None
        attack_hit_target = hit_info["is_hit"]

        if attack_hit_target:
            """
            Target takes damage from attacker but only 
            if they hit. Whether or not the hit lands
            is based on what the target is wielding.
            A draw is possible, in which case neither side
            takes damage.
            """
            attack_info = attacker.get_attack(attacker=attacker,
                                              target=target)
            target.apply_damage(attack_info["damage"])

            """ Target takes damage. Attacker wins """
            winner = attacker
            loser = target
        else:
            """
            If the attacker did not strike the target, this could
            be a draw. The target may only strike if it's not a draw.
            """
            if not hit_info["is_draw"]:
                hit_info = self.is_hit(attacker=target,
                                       target=attacker)

                attack_info = target.get_attack(target=attacker,
                                                attacker=target)

                attacker.apply_damage(attack_info["damage"])

                """ Attacker takes damage, target wins """
                winner = target
                loser = attacker

        self.on_battle_completed(winner=winner,
                                 loser=loser,
                                 hit_info=hit_info,
                                 attack_info=attack_info)

    
    def on_battle_completed(self, **kwargs):
        """
        After the battle has completed, iterate rounds
        and calculate the summary.
        """
        log.info("SpiffyRPG: battle concluded")

        winner = kwargs["winner"]
        loser = kwargs["loser"]
        hit_info = kwargs["hit_info"]
        attack_info = kwargs["attack_info"]
        xp = 0

        """
        It is possible to have a draw! No XP in that case.
        """
        if hit_info["is_draw"]:
            self.announcer.draw(hit_info=hit_info,
                                winner=winner,
                                loser=loser)
        else:
            if winner.is_player:
                xp = self.get_xp_for_battle(winner=winner,
                                            loser=loser)

            """
            The winner gains HP upon victory, whether they
            are player or NPC
            """
            hp_bonus = winner.add_victory_hp_bonus()

            self.announcer.unit_victory(winner=winner,
                                        loser=loser,
                                        attack=attack_info,
                                        hit_info=hit_info,
                                        xp_gained=xp,
                                        hp_gained=hp_bonus)
            
            """ Win dialogue is sent to channel 
            self.announcer.unit_dialogue(attacker,
                                         attacker.get_win_dialogue(),
                                         GAME_CHANNEL)
            """

            """
            Only players gain experience...so far.
            """
            if winner.is_player:
                """
                We only announce to players that they've gained HP.
                """
                if hp_bonus > 0:
                    """
                    announcer = SpiffyPlayerAnnouncer(irc=self.announcer._irc,
                                                      destination=winner.nick)
                    announcer.victory_hp_bonus(hp=hp_bonus)
                    """

                log.info("SpiffyRPG: adding %s xp to player %s" % (xp, winner.name))

                winner.add_experience(xp)

                winner.experience += xp

                level_after_adding_xp = self.unit_level.get_level_by_xp(winner.experience)

                if level_after_adding_xp > winner.level:
                    log.info("SpiffyRPG: %s is now level %s!" % (winner.name, level_after_adding_xp))
                    winner.level = level_after_adding_xp

                    self.announcer.player_gained_level(winner)
            else:
                log.info("SpiffyRPG: %s won but they ain't no not a playa!" % winner.name)

    def get_xp_for_battle(self, **kwargs):
        loser = kwargs["loser"]
        winner = kwargs["winner"]
        xp = int(5 * loser.level)

        if not loser.is_player:
            xp *= 3

        if winner.level > (loser.level+3):
            level_diff = winner.level - loser.level

            xp /= level_diff
        else:
            level_diff = winner.level - loser.level

            """ Level difference must be at least one """
            if level_diff >= 1:
                log.info("SpiffyRPG: %s (%s) is lower level than %s (%s) - multiplying by %s" % \
                (winner.name, winner.level, loser.name, loser.level, level_diff))

                xp *= level_diff

        return xp
    
    def add_party_member(self, unit):
        if unit not in self.party:
            if unit.is_alive():
                log.info("SpiffyRPG: adding %s to party" % unit.name)

                self.party.append(unit)
            else:
                log.error("SpiffyRPG: cannot add dead unit %s" % unit)

class SpiffyWorld:
    """
    Representation of the world
    """
    dungeons = []

    def __init__(self, **kwargs):
        self._irc = kwargs["irc"]
        self.ignore_nicks = kwargs["ignore_nicks"]
        self.unit_db = kwargs["unit_db"]

        log.info("SpiffyRPG: SpiffyWorld initializing!")

        """
        Realm announcer could be happening here, iterating
        each dungeon (channel) and announcing
        """

    def destroy(self):
        log.info("SpiffyRPG: destroying world!")

        for dungeon in self.dungeons:
            dungeon.destroy()

    def start(self):
        self.initialize_dungeons()

    def initialize_dungeons(self):
        if len(self.dungeons) > 0:
            for dungeon in self.dungeons:
                dungeon.initialize(irc=self._irc,
                                   ignore_nicks=self.ignore_nicks,
                                   unit_db=self.unit_db)
        else:
            log.info("SpiffyRPG: warning, no dungeons in this world!")

    def add_dungeon(self, dungeon):
      if dungeon is not None and dungeon not in self.dungeons:
          self.dungeons.append(dungeon)

    def get_dungeon_by_channel(self, channel):
        lower_channel = channel.lower()

        for dungeon in self.dungeons:
            """ dungeon.channel is lowered on instantiation """
            if dungeon.channel == lower_channel:
                return dungeon

        log.error("SpiffyRPG: error finding dungeon with channel '%s'" % channel)

class SpiffyBattleAnnouncer(SpiffyAnnouncer):
    """
    Announcements specific to battles events
    """
    def __init__(self, **kwargs):
        announcer_parent = super(SpiffyBattleAnnouncer, self)
        announcer_parent.__init__(irc=kwargs["irc"],
                                  destination=kwargs["destination"],
                                  public=True)

    def player_gained_level(self, player):
        """
        Player_1 has gained level X! 
        """
        params = (self._b(self._c("DING!", "yellow")),
                  self._get_unit_title(player), 
                  self._b(player.level))

        announcement_msg = "%s %s ascends to level %s!" % params

        self.announce(announcement_msg)

    def draw(self, **kwargs):
        """
        $target $blocks $attacker's $attack
        """
        hit_info = kwargs["hit_info"]
        attacker, target = (kwargs["winner"], kwargs["loser"])
        attacker_name = self._b(attacker.name)
        attacker_item = self._c(hit_info["attacker_weapon"]["name"], "light green")
        target_name = self._b(target.name)
        target_item = self._c(hit_info["target_weapon"]["name"], "light green")

        avoidance = ("blocks", "parries", "dodges", "escapes",
        "misses", "sidesteps", "circumvents", "evades", "fends off",
        "eludes", "deflects", "wards off")
        avoidance_word = self._b(random.choice(avoidance))
        
        params = (target_name, avoidance_word, attacker_name, attacker_item)

        announcement_msg = "%s %s %s's %s!" % params

        self.announce(announcement_msg)

    def unit_victory(self, **kwargs):
        """
        $1 reduced to -22 ♥; $2` survived with 60 ♥. $2 gains +15 Internet Points
        """
        winner = kwargs["winner"]
        loser = kwargs["loser"]
        hit_info = kwargs["hit_info"]
        hp_gained = kwargs["hp_gained"]
        attack = kwargs["attack"]
        winner_weapon = hit_info["attacker_weapon"]
        loser_weapon = hit_info["target_weapon"]
        winner_attack = winner_weapon["name"]
        winner_item_type = self._get_item_type_indicator(winner_weapon["item_type"])
        loser_item_type = self._get_item_type_indicator(loser_weapon["item_type"])

        green_xp = self._c("{:,}".format(kwargs["xp_gained"]), "green")
        bonus_xp = ""
        internet_points = self._c("Internet Points", "purple")
        pink_heart = self._c(u"♥", "pink")

        winner_title = self._get_unit_title(winner)
        loser_title = self._get_unit_title(loser)
        attack_name = self._c(winner_attack, "light green")
        winner_hp = self._c(winner.get_hp(), "red")
        loser_hp = self._c(loser.get_hp(), "green")

        attack_word = self._b(self._c(hit_info["hit_word"], "red"))

        #if attack["is_critical_strike"]:
        #    attack_word = self._b(self._c("critically struck", "red"))

        damage = self._c(attack["damage"], "red")

        params = (winner_title, attack_name, winner_item_type, attack_word, loser_title, 
        loser_item_type, damage, winner_title, winner_hp, pink_heart)

        announcement_msg = "%s's %s [%s] %s %s [%s] for %s. %s survived with %s %s" % params
        #announcement_msg += "%s attacked % times for %s damage." % ()

        if winner.is_player and kwargs["xp_gained"] > 0:
            announcement_msg += " %s gains %s %s" % (winner_title, green_xp, internet_points)

        if hp_gained > 0:
            announcement_msg += " and gained %s %s for winning" % (self._b(hp_gained), pink_heart)

        self._send_channel_notice(announcement_msg)

    def unit_attack(self, **kwargs):
        """
        $attacker's $attack ($type) hits $target ($type) for
        $damage

        Later we can expand this to be have flavored messages
        based on the equipped item.
        """
        attack = kwargs["attack"]
        attacker = attack["attacker"]
        target = attack["target"]        
        attacker_title = self._b(attacker.name)
        target_title = self._b(target.name)
        damage = self._b(attack["damage"])
        is_hit = attack["damage"] > 0

        attacker_item = attacker.get_equipped_weapon()
        attacker_item_type = attacker_item["item_type"][0].upper()

        attack_name = self._b(attacker_item["name"])

        target_item = target.get_equipped_weapon()
        target_item_type = target_item["item_type"][0].upper()

        params = (attacker_title, attack_name, attacker_item_type, \
        target_title, target_item_type, damage)

        announcement_msg = "%s's %s [%s] hits %s [%s] for %s damage" % params
        
        self.announce(announcement_msg)

    def unit_miss(self, **kwargs):
        """
        $attacker's $attack ($type) hits $target ($type) for
        $damage

        Later we can expand this to be have flavored messages
        based on the equipped item.
        """
        attack = kwargs["attack"]
        attacker = attack["attacker"]
        target = attack["target"]        
        attacker_title = self._b(attacker.name)
        target_title = self._b(target.name)
        damage = self._b(attack["damage"])
        is_hit = attack["damage"] > 0

        attacker_item = attacker.get_equipped_weapon()
        attacker_item_type = attacker_item["item_type"][0].upper()

        attack_name = self._b(attacker_item["name"])

        target_item = target.get_equipped_weapon()
        target_item_type = target_item["item_type"][0].upper()

        params = (attacker_title, attack_name, attacker_item_type, \
        target_title)

        announcement_msg = "%s's %s [%s] misses %s!" % params
        
        self.announce(announcement_msg)

class SpiffyDungeonAnnouncer(SpiffyAnnouncer):
    """
    Announcements specific to dungeon events
    """
    def __init__(self, **kwargs):
        announcer_parent = super(SpiffyDungeonAnnouncer, self)
        announcer_parent.__init__(irc=kwargs["irc"],
                                  destination=kwargs["destination"],
                                  public=True)

    def unit_death(self, **kwargs):
        """
        This occurs when the player tries to do something
        silly, like attack with a weapon type that doesn't exist.
        """
        unit = kwargs["unit"]
        unit_name = self._b(unit.name)

        deaths = ("%s was eaten by wolves" % unit_name, 
                  "%s's router was melted by DDoS" % unit_name,
                  "%s's computer was compromised by malware" % unit_name,
                  "%s ate expired Taco Bell" % unit_name,
                  "%s was eaten by a grue" % unit_name,
                  "%s bought the farm" % unit_name)

        announcement_msg = self._b(random.choice(deaths))

        self.announce(announcement_msg)

    def unit_dialogue(self, unit, dialogue):
        """
        %s: %s
        """
        if dialogue is None:
            log.error("SpiffyWorld: dialogue error for unit %s" % unit.name)
            return

        bold_title = self._get_unit_title(unit)
        orange_dialogue = self._c(dialogue, "orange")
        padded_level = str(unit.level).zfill(2)
        bold_level = self._b(padded_level)

        params = (bold_level, bold_title, orange_dialogue)

        announcement_msg = "[%s] %s says %s" % params

        self.announce(announcement_msg)

    def _get_dungeon_title(self, dungeon):
        return self._c(dungeon.name, "light green")

    def get_rarity_indicator(self, **kwargs):
        rarity = kwargs["rarity"]
        rarity_map = {
            "common": "light gray",
            "uncommon": "green",
            "rare": "dark blue",
            "dank": "purple" 
        }

        if rarity not in rarity_map:
            rarity = "common"

        indicator_color = rarity_map[rarity]

        indicator = self._c(u"•", indicator_color)

        return indicator

    def item_info(self, **kwargs):
        item = kwargs["item"]
        item_name = self._b(item["name"])
        rarity_indicator = self.get_rarity_indicator(rarity=item["rarity"])
        bold_item_type_label = self._b("Item type")
        params = (rarity_indicator, 
                  item_name,
                  item["min_level"],
                  bold_item_type_label,
                  item["item_type"])

        announcement_msg = "%s %s (%s) :: %s: %s" % params

        self._irc.reply(announcement_msg)

    def unit_attack(self, **kwargs):
        danger_low_hp_threshold = 20
        attack_word = "hits"
        player_1 = kwargs["player_1"]
        player_2 = kwargs["player_2"]
        attack = kwargs["attack"]

        if attack["is_critical_strike"]:
            attack_word = ircutils.mircColor("critically strikes", fg="red", bg="black")

        # Check player_1 hp for danger
        if player_1.hp <= danger_low_hp_threshold:
            winner_hp = self._c(player_1.hp, "red")
        else:
            winner_hp = self._c(player_1.hp, "green")

        # Check player_2's hp for danger
        if player_2.hp <= danger_low_hp_threshold:
            loser_hp = self._c(player_2.hp, "red")
        else:
            loser_hp = self._c(player_2.hp, "green")
        
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
        player_title = self._get_unit_title(player_1)
        
        params = (player_title, attack_verb, attack_word, red_damage, 
        damage_type, you_die)

        announcement_msg = "%s's %s %s you for %s %s. %s" % params

        self._send_player_notice(announcement_msg)

    def effect_raise_dead(self, **kwargs):
        """
        %s raises %s from the dead!
        """
        player = kwargs["player"]
        unit = kwargs["unit"]
        ptitle = self._get_unit_title(player)
        utitle = self._b(unit.get_title())

        announcement_msg = "%s raises %s from the dead!" % \
        (ptitle, utitle)

        self.announce(announcement_msg)

    def new_realm_king(self, player):
        """
        %s the level %s %s is the new Realm King!
        """
        title = self._get_unit_title(player)
        level = ircutils.bold(player["level"])
        player_class = self._get_player_role(player)
        params = (title, level, player_class)

        announcement_msg = "%s the level %s %s is the new Realm King!" % params

        self.announce(announcement_msg)

    def top_players(self, top_players):
        for player in top_players:
            self.player_info(player)

    def dialogue_intro(self, unit, intro):
        colored_intro = ircutils.mircColor(intro, fg="orange")
        bold_title = ircutils.bold(unit.title)
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
        hp = unit.get_hp()

        if not unit.is_alive():
            hp = self._c(hp, "red")

        colored_hp = self._b(hp)

        body_count = len(unit.slain_foes)
        unit_slain_count = self._c(body_count, "red")
        dungeon_name = self._get_dungeon_title(dungeon)
        foe_word = "foes"
        life_status = ""
        stage = unit.get_stage_by_level(level=unit.level)

        if body_count == 1:
            foe_word = "foe"

        if not unit.is_alive() and not unit.is_undead():
            life_status = self._c("dead ", "red")

        cname = self._c(unit.get_title(), "light green")
        msg = "%s is a %slevel %s %s [%s] with %s %s and has " % \
        (unit_title, life_status, level, cname, stage, hp, pink_heart)
        msg += "existed in %s for %s. %s has slain %s %s." % \
        (dungeon_name, existed, unit_title, unit_slain_count, foe_word)

        if len(unit.effects) > 0:
            msg += " %s: " % self._b("Effects")
            fx = []

            for effect in unit.effects:
                fx.append("%s" % self._c(effect["name"], "light blue"))

            msg += ", ".join(fx)

        self.announce(msg)

    def player_info(self, **kwargs):
        """
        %s is a level %s %s. %s XP remains until %s
        """
        player = kwargs["player"]
        bold_title = self._get_unit_title(player)
        bold_class = self._get_player_role(player)

        player_xp = player.experience

        xp_req_for_this_level = player.get_xp_required_for_next_level() + 1
        
        """ If this is one, they're max level """
        if xp_req_for_this_level == 1:
            xp_req_for_this_level = self.levels[-1][1]

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

        stage = player.get_stage_by_level(level=player.level)

        params = (bold_title, bold_level, bold_class, stage, bold_hp, pink_heart)
        announcement_msg = "%s is a level %s %s [%s] with %s %s" % params
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

        #num_raised_units = len(player.raised_units)
        #if num_raised_units > 0:
        #    announcement_msg += " %s has raised %s units." % (bold_title, num_raised_units)

        #self._irc.reply(announcement_msg)
        self._send_channel_notice(announcement_msg)

    def new_player(self, char_name, char_class):
        """
        Player_1, the IRC Troll has joined the game!
        """
        params = (self._b(char_name), self._b(char_class))

        announcement_msg = "%s the %s joined the game!" % params

        self._send_channel_notice(announcement_msg)

    def seance_failed(self, **kwargs):
        player = kwargs["player"]
        dungeon = kwargs["dungeon"]
        dungeon_title = self._get_dungeon_title(dungeon)
        player_title = self._get_unit_title(player)

        announcement_msg = "%s does not sense the dead nearby %s" % \
        (player_title, dungeon_title)

        self.announce(announcement_msg)

    def undead_attacker(self, **kwargs):
        dungeon = kwargs["dungeon"]
        attacker = kwargs["attacker"]
        target = kwargs["target"]
        attacker_title = self._get_unit_title(attacker)

        self.unit_dialogue(attacker, kwargs["dialogue"])

    def open_map(self, **kwargs):
        dungeon = kwargs["dungeon"]
        seconds = int(time.time() - dungeon.created_at)
        duration = self._b(self._get_duration(seconds))
        dungeon_title = self._get_dungeon_title(dungeon)
        
        """
        "players": {
              "living": 0,
              "dead": 0
          },
          "npc": {
              "hostile": {
                  "living": 0,
                  "dead": 0
              },
              "friendly": {
                  "living": 0,
                  "dead": 0
              }
          }
        """
        unit_distro = dungeon.get_unit_status_distribution()
        hlive = unit_distro["npc"]["hostile"]["living"]
        hdead = unit_distro["npc"]["hostile"]["dead"]
        hundead = unit_distro["npc"]["hostile"]["undead"]
        flive = unit_distro["npc"]["friendly"]["living"]
        fdead = unit_distro["npc"]["friendly"]["dead"]
        fundead = unit_distro["npc"]["friendly"]["undead"]
        plive = unit_distro["players"]["living"]
        pdead = unit_distro["players"]["dead"]
        pundead = unit_distro["players"]["undead"]

        unit_list_description = "%s/%s/%s hostiles, %s/%s/%s friendly, and %s/%s/%s players" % \
        (hlive, hdead, hundead, flive, fdead, fundead, plive, pdead, pundead)

        announcement_msg = "You have been in %s for %s." % \
        (dungeon_title, duration)

        announcement_msg += " %s has %s" % \
        (dungeon_title, unit_list_description)

        self.announce(announcement_msg)

    def on_clear(self, **kwargs):
        dungeon = kwargs["dungeon"]
        player = kwargs["player"]
        xp = kwargs["xp"]

        player_title = self._get_unit_title(player)
        formatted_xp = self._b(self._c("{:,}".format(xp), "green"))
        internet_points = self._c("Internet Points", "purple")
        dungeon_name = self._get_dungeon_title(dungeon)
        params = (player_title, formatted_xp, internet_points, dungeon_name)

        announcement_msg = "%s gains %s %s for clearing %s" % params

        self.announce(announcement_msg)

    def look(self, **kwargs):
        dungeon = kwargs["dungeon"]
        player = kwargs["player"]
        units = kwargs["units"]
        words = ["looks around", "inspects the surroundings of", 
        "scans the area of"]
        is_seance = kwargs["is_seance"]
        look_phrase = random.choice(words)
        player_name = self._get_unit_title(player)
        dungeon_name = self._get_dungeon_title(dungeon)

        if len(units) > 0:
            unit_titles = []
            
            if is_seance:
                msg = "%s channels the spirits of the dead in %s and senses " % \
                (player_name, dungeon_name)
            else:
                msg = "%s %s %s and sees " % \
                (player_name, look_phrase, dungeon_name)
            
            for unit in units:
                unit_name = self._b(unit.name)

                if is_seance:
                    unit_name = self._c(unit_name, "red")

                unit_level = self._c(unit.level, "green")
                unit_titles.append("%s (%s)" % (unit_name, unit_level))

            msg += ", ".join(unit_titles)
        else:
            msg = "%s %s %s but sees nothing of import" % \
            (player_name, look_phrase, dungeon_name)

        #self._irc.reply(msg, notice=True)
        self.announce(msg)

    def inspect_target(self, **kwargs):
        """
        Inspects a target in the dungeon. This will
        show player info it the target is not a NPC.
        """
        dungeon = kwargs["dungeon"]
        player = kwargs["player"]
        search = kwargs["target"]

        unit = dungeon.get_unit_by_name(search)

        if unit is not None:
            log.info("SpiffyRPG: inspecting %s" % unit.name)

            if unit.is_player:
                self.player_info(player=unit)
            else:
                """ TODO: account for difference between NPCs and items """
                self.unit_info(unit=unit,
                               player=player,
                               dungeon=dungeon)
        else:
            self.look_failure(player=player,
                              dungeon=dungeon)

    def look_failure(self, **kwargs):
        words = ["looks around", "inspects the surroundings", 
        "scans the area of"]
        look_phrase = random.choice(words)
        player_name = self._get_unit_title(kwargs["player"])
        dungeon_name = self._get_dungeon_title(kwargs["dungeon"])

        msg = "%s %s %s but sees nothing of import" % \
        (player_name, look_phrase, dungeon_name)

        self.announce(msg)

    def unit_spawned(self, unit):
        """
        A level %s %s appears!
        """
        msg = self._c("A level ", "light blue")
        bold_level = self._c(unit.level, "green")
        unit_name = self._c(unit.get_title(), "yellow")

        msg += "%s %s" % (self._b(bold_level), self._b(unit_name))

        msg += self._c(" appears!", "light blue")

        self.announce(msg)

class SpiffyDungeon:
    """
    Representation of a dungeon within the world
    """
    units = []
    max_units = 10
    effect_id_undead = 4

    def __init__(self, **kwargs):
        self.db = kwargs["db"]
        self.irc = kwargs["irc"]
        self.unit_db = kwargs["unit_db"]
        self.unit_level = SpiffyUnitLevel()
        dungeon = self.get_dungeon_by_channel(GAME_CHANNEL)
        
        if dungeon is not None:            
            self.created_at = time.time()
            self.id = dungeon["id"]
            self.name = dungeon["name"]
            self.description = dungeon["description"]
            self.min_level = dungeon["min_level"]
            self.max_level = dungeon["max_level"]

            self.channel = dungeon["channel"].lower()
            self.unit_quantity = kwargs["unit_quantity"]

            self.announcer = SpiffyDungeonAnnouncer(irc=self.irc,
                                                    destination=self.channel)

            self.battle = SpiffyBattle(db=self.db,
                                       irc=kwargs["irc"],
                                       destination=self.channel)

            """ Remove all timers on initialization """
            self.destroy()

            """
            Apparently scheduling these events can throw
            even when you remove them first!
            """
            try:
                #self.start_dialogue_timer()
                self.start_spawn_timer()
                #self.start_chaos_timer()
                self.start_player_regen_timer()
            except:
                pass
            
            if "max_level" in kwargs:
                self.max_level = kwargs["max_level"]

                log.info("SpiffyRPG: creating dungeon with max level %s" % self.max_level)

        else:
            log.error("SpiffyRPG: unable to find dungeon %s" % (GAME_CHANNEL,))

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
            schedule.removeEvent("spawn_timer")
            schedule.removeEvent("dialogue_timer")
            schedule.removeEvent("chaos_timer")
            schedule.removeEvent("player_regen_timer")
        except:
            pass

    def start_player_regen_timer(self):
        log.info("SpiffyRPG: starting player regen interval")

        regen_interval = 300

        schedule.addPeriodicEvent(self.regenerate_players,
                                  regen_interval,
                                  name="player_regen_timer")

    def start_chaos_timer(self):
        log.info("SpiffyRPG: starting chaos interval")

        spawn_interval = 300

        schedule.addPeriodicEvent(self.herald_chaos,
                                  spawn_interval,
                                  name="chaos_timer")

    def regenerate_players(self):
        """
        When a player dies in a dungeon they stay dead until
        they are regenerated over time
        """
        log.info("SpiffyRPG: regenerating players in %s" % self.name)

        dead_players = self.get_wounded_players()

        if len(dead_players) > 0:
            for player in dead_players:
                total_hp = player._get_hp()
                regen_hp = total_hp * .25

                player.regenerate_hp(regen_hp)
        else:
            log.info("SpiffyRPG: no dead players in %s" % self.name)

    def herald_chaos(self):
        """
        Finds units in the dungeon with the Undead effect.
        In the future this could be expanded to consider
        other effects.
        """
        #chance_for_chaos = random.randrange(1, 100) < 20
        #if not chance_for_chaos:
        #    return

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

        dialogue_interval = 3600

        schedule.addPeriodicEvent(self.random_unit_dialogue,
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

                self.announcer.unit_dialogue(unit,
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
            self._irc = kwargs["irc"]
            self.ignore_nicks = kwargs["ignore_nicks"]

            log.info("SpiffyRPG: initializing dungeon #%s - %s with %s monsters" \
            % (self.id, self.name, self.unit_quantity))

            """ Regular monsters """
            self.populate(self.unit_quantity)
            #self.announcer.open_map(dungeon=self)
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

    def populate(self, unit_quantity):
        units = []
     
        """ Random NPCs """
        unit_id_list = self.unit_db.get_unit_ids(limit=unit_quantity)

        """ Special units """
        special_ids = self.unit_db.get_turkey_ids(limit=5)

        for sid in special_ids:
            if sid not in unit_id_list:
                unit_id_list.append(str(sid))

        """
        Player lookup
        """
        look_up = self.get_user_lookup_from_channel()
        look_up_user_ids = look_up["look_up_user_ids"]
        look_up_nicks = look_up["look_up_nicks"]
        player_user_id_list = look_up["player_user_id_list"]

        if len(player_user_id_list) > 0:
            player_unit_list = self.unit_db.get_units(user_ids=player_user_id_list)

            if len(player_unit_list) > 0:
                for p in player_unit_list:
                    unit_id_list.append(str(p["id"]))
            else:
                log.info("SpiffyRPG: couldn't find players to add to dungeon")

        """
        1. Get dialogue
        2. Get unit effects
        2. Get items
        3. Get item effects
        4. 
        """
        dialogues_lookup = self.unit_db.get_unit_dialogue(unit_ids=unit_id_list)
        items_lookup = self.unit_db.get_unit_items(unit_ids=unit_id_list)
        unit_effects_lookup = self.unit_db.get_unit_effects(unit_ids=unit_id_list)        
        db_units = self.unit_db.get_units(unit_ids=unit_id_list)
        base_items_lookup = self.unit_db.get_base_items_lookup()
        unit_type_titles_lookup = self.unit_db.get_unit_type_titles_lookup()

        item_ids = []

        for u in db_units:
            unit = dict(u)
            unit_id = unit["id"]
            unit["items"] = []
            unit_type_id = unit["unit_type_id"]

            """
            The unit titles lookup contains all of the titles
            for this unit type. The titles behave like ranks,
            so the title changes with the level. Each title
            has a required level, and the unit's level determines 
            that.
            """
            if unit_type_id in unit_type_titles_lookup:
                unit["titles"] = unit_type_titles_lookup[unit_type_id]
            else:
                log.info("SpiffyRPG: anomalous unit! unit type %s not in titles" % unit_type_id)

            """
            Items - items can have effects, so once we've
            got the items we need to build a list of IDs
            in order to get the effects of each item. 
            """
            if unit["id"] in items_lookup:
                """ item_ids is used to look up the item effects """
                for item in items_lookup[unit_id]:
                    item_ids.append(str(item["id"]))
                    unit["items"].append(item)

                """ If unit has any items, find the effects for those items """
                if len(item_ids) > 0:
                    item_effects_lookup = self.unit_db.get_item_effects(item_ids=item_ids)

                    for item in unit["items"]:
                        """
                        If the item id is in the lookup, then this item has some
                        effects
                        """
                        if item["id"] in item_effects_lookup:
                            item_effects = item_effects_lookup[unit_id]

                            """
                            You can use an item to gain its effect, but
                            some items can trigger an effect on possession!
                            """
                            for item_effect in item_effects:
                                if item_effect["effect_on_possession"] == 1:
                                    unit["effects"].append(dict(item_effect))
            else:
                unit["items"] = []
            
            """ Unit dialogue """
            if unit_id in dialogues_lookup:
                unit["dialogue"] = dialogues_lookup[unit_id]
            else:
                unit["dialogue"] = []

            """ Unit effects """
            if unit_id in unit_effects_lookup:
                unit["effects"] = unit_effects_lookup[unit_id]
            else:
                unit["effects"] = []

            units.append(unit)

        """ Build each unit based on the above """
        if len(units) > 0:
            for final_unit in units:
                unit_user_id = final_unit["user_id"]
                unit_nick = ""

                """
                Check if this user id is in the nick lookup
                """
                if unit_user_id in look_up_user_ids:
                    unit_nick = look_up_user_ids[unit_user_id]

                objectified_unit = SpiffyUnit(unit=final_unit,
                                              db=self.db,
                                              user_id=unit_user_id,
                                              nick=unit_nick,
                                              irc=self.irc,
                                              min_level=self.min_level,
                                              max_level=self.max_level,
                                              base_items_lookup=base_items_lookup)

                self.add_unit(objectified_unit)
        else:
            log.info("SpiffyRPG: couldn't find any monsters to populate dungeon")

    def get_user_lookup_from_channel(self):
        """ 
        Add players to the dungeon by iterating the nick list
        and checking for user ids.
        """
        nicks = self._irc.state.channels[GAME_CHANNEL].users
        ignoreMe = self.ignore_nicks
        look_up_user_ids = {}
        look_up_nicks = {}
        player_user_id_list = []

        for nick in nicks:
            if not nick:
                continue

            """ Skip ignored nicks """
            if nick in ignoreMe:
                continue

            hostmask = self._irc.state.nickToHostmask(nick)
            user_id = None

            if hostmask is None:
                continue

            try:
                user_id = ircdb.users.getUserId(hostmask)
            except KeyError:
                log.info("SpiffyRPG: error getting hostmask for %s" % nick)
            
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
                    (unit.level, unit.name, unit.get_title(), unit.get_hp(), self.name))
            else:
                log.info("SpiffyRPG: spawning a level %s NPC: %s (%s) with %s HP in %s" % \
                    (unit.level, unit.name, unit.get_title(), unit.get_hp(), self.name))
            
            self.units.append(unit)
        else:
            log.info("SpiffyRPG: not adding duplicate unit %s" % (unit.get_title()))

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
            #if unit.name.lower() == lower_name or unit.nick.lower() == lower_name:
            if unit.name.lower() == lower_name:
                return unit

    def get_player_by_player_id(self, player_id):
        for unit in self.units:
            if unit.id == player_id:
                return unit

    def get_living_unit_by_name(self, name):
        for unit in self.units:
            if unit.get_hp() > 0 and unit.name.lower() == name.lower():
                return unit

    def get_dead_unit_by_name(self, name):
        for unit in self.units:
            if unit.get_hp() <= 0 and unit.name.lower() == name.lower():
                return unit

    def get_living_players(self):
        players = []

        for unit in self.units:
            if unit.is_player and unit.is_alive():
                players.append(unit)

        return players

    def get_living_hostiles_at_stage(self, **kwargs):
        stage = kwargs["stage"]
        hostiles = []

        for unit in self.units:
            is_hostile = not unit.is_player and unit.is_hostile
            alive = unit.is_alive()
            same_stage = unit.get_stage_by_level(level=unit.level) == stage

            if is_hostile and alive and same_stage:
                hostiles.append(unit)

        return hostiles

    def get_living_hostiles_near_level(self, **kwargs):
        hostiles = []
        near = 5
        player_level = kwargs["level"]
        
        for unit in self.units:
            is_hostile = not unit.is_player and unit.is_hostile
            alive = unit.is_alive()
            near_level = unit.level <= (player_level+near)

            if is_hostile and alive and near_level:
                hostiles.append(unit)

        return hostiles

    def get_dead_players(self):
        players = []

        for unit in self.units:
            if unit.is_player and not unit.is_alive():
                players.append(unit)

        return players

    def get_wounded_players(self):
        players = []

        for unit in self.units:
            if unit.is_player and unit.is_below_max_hp():
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
        dead = []

        for unit in self.units:
            if not unit.is_alive():
                dead.append(unit)

        if len(dead) > 0:
            dead = sorted(dead, key=lambda x: x.level, reverse=True)

        return dead

    def get_living_units(self):
        alive = []

        for unit in self.units:
            if unit.is_alive():
                alive.append(unit)

        if len(alive) > 0:
            alive = sorted(alive, key=lambda x: x.level, reverse=True)

        return alive

    def search_living_units_by_name(self, name):
        alive = []

        for unit in self.units:
            unit_name = unit.get_title().lower()
            lower_search_input = name.lower()

            if unit.is_alive() and unit_name in lower_search_input:
                alive.append(unit)

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
                if unit.is_hostile:
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

class SpiffyUnitDB:
    """
    Unit DB operations
    """
    unit_turkey = 32

    def __init__(self, **kwargs):
        self.db = kwargs["db"]

    def register_new_player(self, user_id, char_name, unit_type_id):
        cursor = self.db.cursor()
        created_at = time.time()
        params = (user_id, char_name, unit_type_id, created_at)
        cursor.execute("""INSERT INTO spiffyrpg_units(
                          limnoria_user_id,
                          name, 
                          unit_type_id,
                          created_at)
                          VALUES (?, ?, ?, ?)""", params)
        db.commit()
        cursor.close()

    def get_top_players_by_xp(self):
        cursor = self.db.cursor()

        cursor.execute("""SELECT p.id,
                          ut.id AS unit_type_id,
                          ut.name AS unit_type_name,
                          u.name,
                          u.created_at,
                          u.limnoria_user_id AS user_id,
                          u.experience_gained
                          FROM spiffyrpg_units u
                          JOIN spiffyrpg_unit_types ut ON ut.id = u.unit_type_id
                          ORDER BY p.experience_gained DESC
                          LIMIT 3""")

        top_players = cursor.fetchall()

        cursor.close

        return top_players

    def update_player_role(self, player_id, unit_type_id):
        cursor = self.db.cursor()

        params = (unit_type_id, player_id)

        cursor.execute("""UPDATE spiffyrpg_units
                          SET unit_type_id = ?
                          WHERE id = ?""", 
                       params)

        db.commit()
        cursor.close()

    def get_max_player_level(self):
        cursor = self.db.cursor()

        cursor.execute("""SELECT MAX(experience) AS xp_max
                          FROM spiffyrpg_units
                          WHERE 1=1
                          AND limnoria_user_id != 0""")

        player = cursor.fetchone()

        if player is not None:
            return player["xp_max"]

        cursor.close()

    def get_effect_by_name(self, effect_name):
        cursor = self.db.cursor()
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
        cursor.close()

        if effect is not None:
            return dict(effect)

    def get_item_by_name(self, **kwargs):
        item_name = kwargs["item_name"]
        cursor = self.db.cursor()
        wildcard_item_name = "%%%s%%" % item_name

        cursor.execute("""SELECT
                          i.id,
                          i.name,
                          i.description,
                          i.min_level,
                          i.max_level,
                          i.item_type,
                          i.rarity,
                          i.equipment_slot,
                          i.is_permanent,
                          i.unit_type_id,
                          i.created_at
                          FROM spiffyrpg_items i
                          WHERE 1=1
                          AND i.name LIKE ?
                          ORDER BY i.name
                          LIMIT 1""", (wildcard_item_name,))

        item = cursor.fetchone()
        cursor.close()

        if item is not None:
            return dict(item)

    def get_realm_king_player_id(self):
        cursor = self.db.cursor()

        cursor.execute("""SELECT p.id
                          FROM spiffyrpg_units u
                          WHERE 1=1
                          AND limnoria_user_id != 0
                          ORDER BY experience DESC
                          LIMIT 1""")

        realm_king = cursor.fetchone()
        cursor.close()

        if realm_king is not None:
            return dict(realm_king)["id"]

    def remove_realm_king_effect(self):
        log.info("SpiffyRPG: removing realm kings")

        cursor = self.db.cursor()

        cursor.execute("""DELETE FROM spiffyrpg_item_effects
                          WHERE id = 3""", params)

        cursor.close()

    def get_battle_event(self):
        cursor = self.db.cursor()

        cursor.execute("""SELECT name,
                          description
                          FROM spiffyrpg_battle_events
                          WHERE 1=1
                          ORDER BY RANDOM()
                          LIMIT 1""")

        event = cursor.fetchone()
        cursor.close()

        if event is not None:
            return dict(event)

    def add_battle(self, battle):
        cursor = self.db.cursor()

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

        self.db.commit()
        battle_id = cursor.lastrowid
        cursor.close()

        return battle_id

    def get_turkey_ids(self, **kwargs):
        return self.get_units_by_type(unit_id=self.unit_turkey,
                                      limit=kwargs["limit"])

    def get_unit_types(self):
        cursor = self.db.cursor()

        cursor.execute("""SELECT id, name
                          FROM spiffyrpg_unit_types""")

        unit_types =cursor.fetchall()

        cursor.close()

        return unit_types

    def get_units_by_type(self, **kwargs):
        id_list = []
        cursor = self.db.cursor()
        limit = int(kwargs["limit"])
        query = """SELECT id
                   FROM spiffyrpg_units
                   WHERE 1=1
                   AND id = ?
                   AND limnoria_user_id = 0
                   ORDER BY RANDOM()
                   LIMIT %s""" % (limit)

        cursor.execute(query, (kwargs["unit_id"],))
        ids = cursor.fetchall()
        cursor.close()

        if ids is not None:
            for i in ids:
                id_list.append(str(dict(i)["id"]))

        return id_list

    def get_unit_ids(self, **kwargs):
        """
        Fetches random units with a limit
        """
        id_list = []
        cursor = self.db.cursor()
        limit = int(kwargs["limit"])

        query = """SELECT id
                   FROM spiffyrpg_units
                   WHERE 1=1
                   AND limnoria_user_id = 0
                   ORDER BY RANDOM()
                   LIMIT %s""" % (limit,)

        cursor.execute(query)
        ids = cursor.fetchall()
        cursor.close()

        if ids is not None:
            for i in ids:
                id_list.append(str(dict(i)["id"]))

        return id_list

    def get_units(self, **kwargs):
        """
        This query grabs the unit, its type, and its
        title.
        """
        cursor = self.db.cursor()
        
        """
        The main difference between players and NPCs is that
        only players have a Limnoria user id.
        """
        where = ""

        if "unit_ids" in kwargs:
            comma_separated_string = ",".join(kwargs["unit_ids"])
            where = "AND u.id IN (%s)" % comma_separated_string
        
        if "user_ids" in kwargs:
            comma_separated_string = ",".join(kwargs["user_ids"])
            where = "AND u.limnoria_user_id IN (%s)" % comma_separated_string

        query = """SELECT
                   u.id,
                   u.unit_type_id,
                   u.name AS unit_name,
                   utypes.name AS unit_type_name,
                   u.experience,
                   u.limnoria_user_id AS user_id
                   FROM spiffyrpg_units u
                   JOIN spiffyrpg_unit_types utypes ON utypes.id = u.unit_type_id
                   WHERE 1=1
                   %s
                   GROUP BY u.id
                   ORDER BY u.experience""" % where

        cursor.execute(query)

        units = cursor.fetchall()
        
        cursor.close()

        return units

    def get_unit_effects(self, **kwargs):
        """
        Fetches effects for one or many units
        """
        cursor = self.db.cursor()
        
        comma_separated_string = ",".join(kwargs["unit_ids"])
        params = (comma_separated_string,)

        cursor.execute("""SELECT
                          e.id,
                          e.name,
                          e.description,
                          e.operator,
                          e.hp_adjustment,
                          e.incoming_damage_adjustment,
                          e.outgoing_damage_adjustment,
                          e.interval_seconds,
                          e.stacks,
                          e.created_at
                          FROM spiffyrpg_effects e
                          JOIN spiffyrpg_unit_effects ue ON ue.effect_id = e.id
                          JOIN spiffyrpg_units u ON u.id = ue.unit_id
                          WHERE 1=1
                          AND u.id IN (%s)""" % params)

        effects = cursor.fetchall()
        
        cursor.close()

        lookup = {}

        if len(effects) > 0:
            for effect in effects:
                e = dict(effect)
                effect_id = e["id"]

                if not effect_id in lookup:
                    lookup[effect_id] = []

                lookup[effect_id].append(effect)

        return lookup

    def get_unit_type_titles_lookup(self, **kwargs):
        cursor = self.db.cursor()
        
        cursor.execute("""SELECT
                          t.unit_type_id,
                          t.required_level,
                          t.title
                          FROM spiffyrpg_unit_type_titles t
                          ORDER BY t.required_level ASC""")

        titles = cursor.fetchall()
        cursor.close()
        titles_lookup = {}

        if len(titles) > 0:
            for t in titles:
                title = dict(t)
                unit_type_id = title["unit_type_id"]

                if not unit_type_id in titles_lookup:
                    titles_lookup[unit_type_id] = []

                titles_lookup[unit_type_id].append(title)

        return titles_lookup

    def get_base_items_lookup(self):
        cursor = self.db.cursor()
        
        cursor.execute("""SELECT
                          i.id,
                          i.name,
                          i.description,
                          i.min_level,
                          i.max_level,
                          i.item_type,
                          i.rarity,
                          i.equipment_slot,
                          i.is_permanent,
                          i.unit_type_id,
                          i.created_at
                          FROM spiffyrpg_items i
                          WHERE 1=1
                          AND
                          i.is_permanent = 1
                          ORDER BY i.min_level ASC""")

        items = cursor.fetchall()
        cursor.close()
        items_lookup = {}

        if len(items) > 0:
            for item in items:
                unit_type_id = item["unit_type_id"]

                if not unit_type_id in items_lookup:
                    items_lookup[unit_type_id] = []

                items_lookup[unit_type_id].append(item)

        return items_lookup

    def get_unit_items(self, **kwargs):
        """
        Fetches items for one or many units
        """
        cursor = self.db.cursor()
        
        comma_separated_string = ",".join(kwargs["unit_ids"])
        params = (comma_separated_string,)

        cursor.execute("""SELECT
                          i.id,
                          i.name,
                          i.description,
                          i.min_level,
                          i.max_level,
                          i.item_type,
                          i.rarity,
                          i.equipment_slot,
                          i.is_permanent,
                          i.unit_type_id,
                          i.created_at,
                          ui.unit_id
                          FROM spiffyrpg_items i
                          JOIN spiffyrpg_unit_items ui ON ui.item_id = i.id
                          WHERE 1=1
                          AND ui.unit_id IN (%s)""" % params)

        items = cursor.fetchall()
        
        cursor.close()

        lookup = {}

        if len(items) > 0:
            for item in items:
                i = dict(item)
                item_id = i["id"]
                unit_id = i["unit_id"]

                if not item_id in lookup:
                    lookup[unit_id] = []

                lookup[unit_id].append(i)

        return lookup

    def get_item_effects(self, **kwargs):
        """
        Fetches item effects for one or items
        """
        cursor = self.db.cursor()
        
        comma_separated_string = ",".join(kwargs["item_ids"])
        params = (comma_separated_string,)

        cursor.execute("""SELECT
                          i.id,
                          e.effect_on_possession,
                          e.duration_in_seconds,
                          e.created_at
                          FROM spiffyrpg_item_effects e
                          JOIN spiffyrpg_items i ON i.id = e.item_id                        
                          WHERE 1=1
                          AND i.id IN (%s)""" % params)

        effects = cursor.fetchall()
        
        cursor.close()

        lookup = {}

        if len(effects) > 0:
            for effect in effects:
                e = dict(effect)
                effect_id = e["id"]
                item_id = e["item_id"]

                if not effect_id in lookup:
                    lookup[item_id] = []

                lookup[item_id].append(effect)

        return lookup

    def get_unit_dialogue(self, **kwargs):
        """
        Fetches dialogue for one or many units
        """
        cursor = self.db.cursor()
        
        comma_separated_string = ",".join(kwargs["unit_ids"])
        params = (comma_separated_string,)

        cursor.execute("""SELECT
                          ud.id,
                          ud.name,
                          ud.context,
                          u.id AS unit_id
                          FROM spiffyrpg_dialogue ud
                          JOIN spiffyrpg_units u ON u.id = ud.unit_id
                          WHERE 1=1
                          AND u.id IN (%s)""" % params)

        dialogues = cursor.fetchall()
        
        cursor.close()

        lookup = {}

        if len(dialogues) > 0:
            for dialogue in dialogues:
                d = dict(dialogue)
                dialogue_id = d["id"]
                unit_id = d["unit_id"]

                if not unit_id in lookup:
                    lookup[unit_id] = []

                lookup[unit_id].append(dialogue)

        return lookup

class SpiffyUnit:
    """
    A unit can be a player, or NPC. NPCs can be friendly/hostile
    """
    UNIT_TYPE_ZEN_MASTER = 1
    UNIT_TYPE_HACKER = 2
    UNIT_TYPE_TROLL = 3

    def __init__(self, **kwargs):
        self.db = kwargs["db"]

        """
        min/max level are only used for NPCs
        """
        min_level = 1
        max_level = 5

        if "min_level" in kwargs:
            min_level = kwargs["min_level"]

        if "max_level" in kwargs:
            max_level = kwargs["max_level"]

        """
        Start by initializing the unit as if it is an NPC,
        since for the most part, a player is identical to a NPC.
        """
        self.slain_foes = []
        self.battles = []
        self.unit_level = SpiffyUnitLevel()
        self.id = kwargs["unit"]["id"]
        self.user_id = kwargs["user_id"]
        self.created_at = time.time()
        self.unit_type_name = kwargs["unit"]["unit_type_name"]
        self.unit_type_id = kwargs["unit"]["unit_type_id"]
        self.effects = kwargs["unit"]["effects"]
        self.items = kwargs["unit"]["items"]
        self.level = random.randrange(min_level, max_level)
        self.experience = self.unit_level.get_xp_for_level(self.level)
        self.is_hostile = True
        self.name = kwargs["unit"]["unit_name"]
        self.nick = self.name

        """ When unit is an NPC then use the unit name """
        self.name = kwargs["unit"]["unit_name"]

        """
        If the unit has a non-zero user_id, then they are a player. 
        When the unit is a NPC then their level depends
        on the dungeon min/max.
        """
        self.is_player = self.user_id > 0

        if self.is_player:
            """
            When the unit is a player, recalculate experience
            """
            self.experience = kwargs["unit"]["experience"]
            self.level = self.unit_level.get_level_by_xp(self.experience)
            self.is_hostile = False
            self.is_player = True
            self.nick = kwargs["nick"]

            self.announcer = SpiffyPlayerAnnouncer(irc=kwargs["irc"],
                                                   destination=self.nick)

        """
        A unit's title is customized based on the unit type
        and current level.
        """
        self.title = self.get_unit_title_from_lookup(kwargs["unit"]["titles"])

        """
        Each unit should get some base items for their level.
        """
        base_items = self.get_base_items_from_lookup(kwargs["base_items_lookup"])
        self.populate_inventory_with_base_items(base_items)

        """
        The above line ensures that the unit always has at least the
        base weapons.
        """
        self.equip_random_weapon()

        """
        HP is a function of the unit's level, so
        the level must be determined prior.
        """
        self.hp = self.calculate_hp()

    def can_battle_unit(self, **kwargs):
        """
        As a balancing measure, units in certain stages
        cannot battle each other.
        """
        unit = kwargs["unit"]
        this_unit_stage = self.get_stage_by_level(level=self.level)
        target_unit_stage = self.get_stage_by_level(level=unit.level)
        can_battle = False
        reason = "You are in the same stage"

        if target_unit_stage == this_unit_stage:
            can_battle = True
        elif target_unit_stage > this_unit_stage:
            reason = "You have no weapons that can damage that target"
        elif target_unit_stage < this_unit_stage:
            reason = "That target is not worth your time"

        return {
            "reason": reason,
            "can_battle": can_battle
        }

    def regenerate_hp(self, regen_hp):
        current_hp = self.get_hp()
        max_hp = self.calculate_hp()

        if self.is_below_max_hp():
            self.hp += regen_hp

            log.info("SpiffyRPG: unit %s gains %sHP for winning" % (self.name, regen_hp))
        else:
            log.info("SpiffyRPG: unit %s is at max HP (%s/%s)" % (self.name, current_hp, max_hp))

    def is_below_max_hp(self):
        current_hp = self.get_hp()
        max_hp = self.calculate_hp()

        return current_hp < max_hp

    def add_victory_hp_bonus(self):
        current_hp = self.get_hp()
        max_hp = self.calculate_hp()
        hp_bonus = int(max_hp * .25)

        if self.is_below_max_hp():
            self.hp += hp_bonus

            log.info("SpiffyRPG: unit %s gains %sHP for winning" % (self.name, hp_bonus))
        else:
            log.info("SpiffyRPG: unit %s is at max HP (%s/%s)" % (self.name, current_hp, max_hp))

        return hp_bonus

    def populate_inventory_with_base_items(self, base_items):
        """
        The base items contain all of the items available
        for this unit type
        """
        for item in base_items:
            if item not in self.items:
                self.items.append(item)

    def get_unit_title_from_lookup(self, lookup):
        """
        Find the appropriate title based on the
        unit level. The lookup is already filtered
        by the unit type ID.
        """
        unit_title = self.unit_type_name

        #log.info("SpiffyRPG: lookup=%s" % lookup)

        """
        The unit's title is the one with the highest
        required level that is <= unit level.
        """
        for title in lookup:
            if self.level >= title["required_level"]:
                unit_title = title["title"]

        return unit_title

    def get_base_items_from_lookup(self, lookup):
        items = []

        if self.unit_type_id in lookup:
            tmp_items = lookup[self.unit_type_id]

            for item in tmp_items:
                if self.level >= item["min_level"]:
                    items.append(dict(item))

        return items

    def get_stage_by_level(self, **kwargs):
        stage = 1
        stage_two_min_level = 3
        stage_three_min_level = 10

        level = kwargs["level"]

        if level >= stage_two_min_level:
            stage = 2

        if level >= stage_three_min_level:
            stage = 3

        return stage

    def is_stage_one(self):
        return self.get_stage_by_level(level=self.level) == 1

    def is_stage_two(self):
        return self.get_stage_by_level(level=self.level) == 2

    def is_stage_three(self):
        return self.get_stage_by_level(level=self.level) == 3

    def equip_item(self, **kwargs):
        self.equipped_weapon = kwargs["item"]

    def equip_random_inventory_item_by_type(self, **kwargs):
        item_name = kwargs["item_type_name"]
        inventory_item = self.get_item_from_inventory_by_type(item_type_name=item_name)

        if inventory_item is not None:
            self.equip_item(item=inventory_item)

            self.announcer.item_equip(player=self,
                                      item=inventory_item)
        else:
            self.announcer.item_equip_failed(player=self,
                                             item_name=item_name)

    def equip_item_by_name(self, **kwargs):
        item_name = kwargs["item_name"]
        inventory_item = self.get_item_from_inventory_by_name(item_name=item_name)
        
        if inventory_item is not None:
            self.equip_item(item=inventory_item)

            self.announcer.item_equip(player=self,
                                      item=inventory_item)
        else:
            self.announcer.item_equip_failed(player=self,
                                             item_name=item_name)

    def get_item_type_from_user_input(self, **kwargs):
        item_type = kwargs["item_type"].lower()

        if item_type == "rock" or item_type[0] == "r":
            item_type = "rock"

        if item_type == "paper" or item_type[0] == "p":
            item_type = "paper"

        if item_type == "scissors" or item_type[0] == "s":
            item_type = "scissors"

        if item_type == "lizard" or item_type[0] == "l":
            item_type = "lizard"

        if item_type == "spock" or item_type[0] == "v":
            item_type = "spock"

        return item_type

    def equip_item_by_type(self, **kwargs):
        item_type = self.get_item_type_from_user_input(item_type=kwargs["item_type"])
        inventory_item = self.get_item_from_inventory_by_type(item_type_name=item_type)
        equip_ok = False

        if inventory_item is not None:
            self.equip_item(item=inventory_item)
            equip_ok = True
        else:
            self.announcer.item_equip_failed(player=self)
            equip_ok = False

        return equip_ok

    def get_equipped_weapon(self):
        """
        If the player only has one weapon, then they're 
        always going to equip that.
        """
        return self.equipped_weapon

    def get_rock_weapon(self):
        return self.get_item_from_inventory_by_type(item_type_name="rock")

    def get_paper_weapon(self):
        return self.get_item_from_inventory_by_type(item_type_name="paper")

    def get_scissors_weapon(self):
        return self.get_item_from_inventory_by_type(item_type_name="scissors")

    def get_lizard_weapon(self):
        return self.get_item_from_inventory_by_type(item_type_name="lizard")

    def get_spock_weapon(self):
        return self.get_item_from_inventory_by_type(item_type_name="spock")

    def get_item_from_inventory_by_type(self, **kwargs):
        item_type_name = kwargs["item_type_name"]
        items = []
        inventory_item_to_equip = None

        log.info("SpiffyRPG: trying to find items of type %s" % item_type_name)

        """
        Find a random item of $type in inventory
        """
        for item in self.items:
            if item["item_type"] == item_type_name:
                items.append(item)

        if len(items) > 0:
            inventory_item_to_equip = random.choice(items)

        return inventory_item_to_equip

    def get_item_from_inventory_by_id(self, **kwargs):
        items = self.items

        if len(items) > 0:
            for item in items:
                if kwargs["item_id"] == item["id"]:
                    return item
        else:
            log.info("SpiffyRPG: trying to get items but inventory is empty!")

    def get_item_from_inventory_by_name(self, **kwargs):
        item_name = kwargs["item_name"].lower()
        items = self.items

        for item in items:
            if item_name in item["name"].lower():
                return item

    def equip_random_weapon(self):
        items = self.items

        if len(items) > 0:
            random_item = random.choice(items)
            
            self.equipped_weapon = random_item
        else:
            log.error("SpiffyRPG: no items to equip!")

    def set_title(self, title):
        self.name = title

        log.info("Player %s sets title to %s" % (self.id, self.title))

        cursor = self.db.cursor()
        params = (title, self.id)

        cursor.execute("""UPDATE spiffyrpg_units
                          SET name = ?
                          WHERE id = ?""", 
                       params)

        self.db.commit()

        cursor.close()

    def get_dialogue_by_type(self, **kwargs):
        dialogue_type = kwargs["dialogue_type"]
        dialogues = []

        for dialogue in dialogues:
            if dialogue.type == dialogue_type:
                dialogues.append(dialogue)

        if len(dialogues) > 0:
            return random.choice(dialogue)

    def dialogue_intro(self):
        return self.get_dialogue_by_type(dialogue_type="intro")

    def dialogue_win(self):
        return self.get_dialogue_by_type(dialogue_type="intro")

    def dialogue_sup(self):
        return self.get_dialogue_by_type(dialogue_type="sup")

    def get_title(self):
        return self.title

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
        cursor = self.db.cursor()
        now = time.time()

        expires_at = now + duration
        params = (effect_id, player_id, expires_at, is_persistent, now)

        cursor.execute("""INSERT INTO spiffyrpg_item_effects(
                          effect_id,
                          player_id,
                          expires_at,
                          is_persistent,
                          created_at)
                          VALUES(?, ?, ?, ?)""", params)
    
    def get_xp_required_for_next_level(self):
        return self.unit_level.get_xp_for_next_level(self.level)

    def get_level(self):
        return self.unit_level.get_level_by_xp(self.experience)

    def add_experience(self, experience):
        if experience <= 0:
            return

        """ Non-player, don't add xp """
        if self.user_id == 0:
            log.info("SpiffyRPG: not adding xp to %s" % self.name)
            return

        log.info("Player %s adding %s xp" % (self.name, experience))

        cursor = self.db.cursor()
        params = (experience, self.id)

        cursor.execute("""UPDATE spiffyrpg_units
                          SET experience = experience + ?
                          WHERE id = ?""", 
                       params)

        self.db.commit()
        cursor.close()

    def calculate_hp(self):
        base_hp = self.level * 20
        
        return base_hp

    def get_effects(self):
        """ TODO: Check duration here """
        return self.effects

    def get_hp(self):
        hp = self.hp

        return int(hp)

    def apply_effect(self, effect):
        if effect not in self.effects:
            self.effects.append(effect)

    def get_attack_damage(self):
        return random.randrange(1, 5) * self.level

    def is_counterpart(self, **kwargs):
        target_unit = kwargs["target_unit"]
        is_counterpart = False

        """ Opponent """
        target_unit_type = target_unit.unit_type_id
        target_is_zm = target_unit_type == UNIT_TYPE_ZEN_MASTER
        target_is_hacker = target_unit_type == UNIT_TYPE_HACKER
        target_is_troll = target_unit_type == UNIT_TYPE_TROLL

        """ Attacker """
        attacker_is_zm = self.unit_type_id = UNIT_TYPE_ZEN_MASTER
        attacker_is_hacker = self.unit_type_id == UNIT_TYPE_HACKER
        attacker_is_troll = self.unit_type_id == UNIT_TYPE_TROLL

        """ TODO: make this work """

        return is_counterpart

    def get_attack(self, **kwargs):
        damage = self.get_attack_damage()
        item = self.get_equipped_weapon()

        attack_info = {
            "damage": damage,
            "item": item
        }

        return attack_info

    def apply_damage(self, hp):
        self.hp = int(self.hp - hp)

        log.info("SpiffyRPG: %s takes %s damage; now has %sHP" % \
        (self.name, hp, self.get_hp()))

    def remove_effect_by_id(self, id):
        effects = []

        for e in effects:
            if e["id"] != id:
                effects.append(e)

        self.effects = effects

    def is_alive(self):
        return self.get_hp() > 0

    def is_undead(self):
        return False

class SpiffyPlayerAnnouncer(SpiffyAnnouncer):
    """
    Announcements sent to a player - their IRC nick
    """
    def __init__(self, **kwargs):
        announcer_parent = super(SpiffyPlayerAnnouncer, self)
        announcer_parent.__init__(irc=kwargs["irc"],
                                  destination=kwargs["destination"],
                                  public=False)

    def victory_hp_bonus(self, **kwargs):
        hp = kwargs["hp"]
        pink_heart = self._c(u"♥", "pink")
        hp_with_heart = self._b("%s %s" % (hp, pink_heart))
        you_gain = "You gain %s" % hp_with_heart
        hp_providers = (
        "%s from looking at cute puppies" % you_gain,
        "You find some leftovers and eat them. %s" % you_gain,
        "%s from a victorious battle!" % you_gain,
        "The thrill of victory grants you %s" % hp_with_heart,
        "%s from being awesome" % you_gain
        )
        hp_gain_from = random.choice(hp_providers)

        announcement_msg = hp_gain_from

        self.announce(announcement_msg)

    def inventory(self, **kwargs):
        player = kwargs["player"]
        items = player.items

        if len(items) > 0:
            item_name_list = []
            equipped_item = player.get_equipped_weapon()

            for item in player.items:
                item_type = self._get_item_type_indicator(item["item_type"])
                item_name = "%s [%s]" % (self._b(item["name"]), item_type)
                is_equipped = item["id"] == equipped_item["id"]                

                if is_equipped:
                    item_name += " [E]"

                item_name_list.append(item_name)

            announcement_msg = ", ".join(item_name_list)
        else:
            announcement_msg = "Your bags seem empty."

        self.announce(announcement_msg)

    def item_equip(self, **kwargs):
        item = kwargs["item"]
        item_name = self._b(item["name"])
        
        announcement_msg = "You have equipped %s" % item_name

        self.announce(announcement_msg)

    def item_equip_failed(self, **kwargs):
        deaths = ("you suddenly burst into flames", 
        "a wild boar emerges from the jungle and charges at you",
        "a naked molerat eats you alive", "Candlejack kidnaps you",
        "Richard Stallman begins devouring you",
        "your bags suddenly burst into flames",
        "lava begins pouring out of your bags",
        "spiders begin pouring out of your bags")

        bold_death = self._b(random.choice(deaths))

        announcement_msg = "You attempt to equip that item, but %s" % bold_death

        self.announce(announcement_msg)

class SpiffyUnitLevel:
    """
    Functionality related to how much xp a unit has
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
                (35, 69000),
                (36, 70000),
                (37, 73000),
                (38, 76000),
                (39, 79000),
                (40, 76000),
                (41, 82000),
                (42, 85000),
                (43, 88000),
                (44, 92000),
                (45, 95000),
                (46, 98000),
                (47, 101000),
                (48, 104000),
                (49, 107000),
                (50, 110000)
      ]

class SpiffyRPG(callbacks.Plugin):
    """A gluten-free IRC RPG"""
    threaded = True
    welcome_messages = {}
    welcome_message_cooldown_in_seconds = 600

    def __init__(self, irc):        
        self.__parent = super(SpiffyRPG, self)
        self.__parent.__init__(irc)
        self.irc = irc

        db_lib = SpiffyRPGDB()
        self.db = db_lib._get_db()
        self.unit_level = SpiffyUnitLevel()
        
        self.unit_db = SpiffyUnitDB(db=self.db)
        self.classes = self.unit_db.get_unit_types()

        self.SpiffyWorld = SpiffyWorld(irc=irc,
                                       unit_db=self.unit_db,
                                       ignore_nicks=self.registryValue("ignoreNicks"))
        
        self._init_world()

    def _get_user_id(self, irc, prefix):
        try:
            return ircdb.users.getUserId(prefix)
        except KeyError:
            pass
            #irc.errorNotRegistered(Raise=True)

        return False

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
        max_xp = self.unit_db.get_max_player_level()
        max_level = self.unit_level.get_level_by_xp(max_xp)
        max_units = random.randrange(5, 20)

        dungeon = SpiffyDungeon(db=self.db,
                                irc=self.irc,
                                unit_db=self.unit_db,
                                unit_quantity=max_units,
                                max_level=max_level,
                                destination=GAME_CHANNEL)
        
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
                dungeon = self.SpiffyWorld.get_dungeon_by_channel(channel)

                if dungeon is not None:
                    player = dungeon.get_unit_by_user_id(user_id)

                    dungeon.announcer.inspect_target(dungeon=dungeon,
                                                     target=target,
                                                     player=player)
    inspect = wrap(inspect, ["user", "text"])

    def look(self, irc, msg, args, user):
        """
        Look around for anything of note nearby
        """
        channel = msg.args[0]
        
        if ircutils.isChannel(channel):
            user_id = self._get_user_id(irc, msg.prefix)

            if user_id:
                dungeon = self.SpiffyWorld.get_dungeon_by_channel(channel)

                if dungeon is not None:
                    player = dungeon.get_unit_by_user_id(user_id)

                    if player is not None:
                        stage = player.get_stage_by_level(level=player.level)
                        units = dungeon.get_living_hostiles_at_stage(stage=stage)
                        dungeon.announcer.look(dungeon=dungeon, 
                                               player=player,
                                               units=units,
                                               is_seance=False)
                    else:
                        log.info("SpiffyRPG: %s does not seem to be registered %s" % (msg.nick, user_id))
                else:
                    irc.error("The dungeon collapses!")
            else:
                log.info("SpiffyRPG: %s is not a user" % msg.prefix)
    
    look = wrap(look, ["user"])

    def find(self, irc, msg, args, user, name):
        """
        Searchs for a unit
        """
        channel = msg.args[0]
        
        if ircutils.isChannel(channel):
            user_id = self._get_user_id(irc, msg.prefix)

            if user_id:
                p = self.unit_db.get_units(unit_ids=[user_id])

                if p is not None:
                    dungeon = self.SpiffyWorld.get_dungeon_by_channel(channel)

                    if dungeon is not None:
                        player = dungeon.get_player_by_player_id(p["id"])
                        units = dungeon.search_living_units_by_name(name)
                        dungeon.announcer.look(dungeon=dungeon, 
                                               player=player,
                                               units=units,
                                               is_seance=False)
    find = wrap(find, ["user", "text"])

    def seance(self, irc, msg, args, user):
        """
        Attempt to communicate with the spirits of the dead
        """
        channel = msg.args[0]
        dungeon = self.SpiffyWorld.get_dungeon_by_channel(channel)
        fizzled = True
        user_id = self._get_user_id(irc, msg.prefix)

        if dungeon is not None:
            player = dungeon.get_unit_by_user_id(user_id)

            if player is not None:
                fizzled = False

                dead = dungeon.get_dead_units()

                if len(dead) > 0:
                    dungeon.announcer.look(dungeon=dungeon, 
                                           player=player,
                                           units=units,
                                           is_seance=False)
                else:
                    dungeon.announcer.seance_failed(dungeon=dungeon,
                                                    player=player)
        
        if fizzled:
            log.error("SpiffyRPG: seance attempt failed in %s" % channel)
            irc.error("Spell fizzled.")
    
    seance = wrap(seance, ["user"])

    def smap(self, irc, msg, args, user):
        """
        Examine your map to see where you are
        """
        channel = msg.args[0]
        
        if ircutils.isChannel(channel):
            user_id = self._get_user_id(irc, msg.prefix)

            dungeon = self.SpiffyWorld.get_dungeon_by_channel(channel)
            
            if dungeon is not None:
                player = dungeon.get_unit_by_user_id(user_id)

                if player is not None:
                    dungeon.announcer.open_map(dungeon=dungeon, 
                                               player=player)
                else:
                    irc.error("You are not in a dungeon.")
            else:
                irc.error("You seem to have misplaced your map.")
        else:
          irc.error("You are not in a dungeon.")
    
    smap = wrap(smap, ["user"])

    def title(self, irc, msg, args, user, title):
        """
        title <new title> - sets a new title for your character. Maximum 16 characters
        """
        is_channel = irc.isChannel(msg.args[0])

        if is_channel:
            user_id = self._get_user_id(irc, msg.prefix)
            dungeon = self.SpiffyWorld.get_dungeon_by_channel(msg.args[0])
            
            if dungeon is not None:
                player = dungeon.get_unit_by_user_id(user_id)

                player.set_title(title[0:16])

                dungeon.announcer.player_info(player=player)

    title = wrap(title, ["user", "text"])

    def attack(self, irc, msg, args, user, target_and_item_type):
        """
        attack <target> <rock|paper|scissors|lizard|spock>
        """
        is_channel = irc.isChannel(msg.args[0])

        if is_channel:
            user_id = self._get_user_id(irc, msg.prefix)          
            channel = msg.args[0]
            dungeon = self.SpiffyWorld.get_dungeon_by_channel(channel)

            if dungeon is not None:
                player = dungeon.get_unit_by_user_id(user_id)

                if player.is_alive():
                    """
                    The target name may contain spaces, so whatever
                    the last part is will be the item type.
                    """
                    target_parts = target_and_item_type.split(" ")
                    item_type = target_parts[-1]
                    
                    """ Remove item type """
                    target_parts.pop()

                    target = " ".join(target_parts)

                    unit = dungeon.get_living_unit_by_name(target)

                    if unit is not None and player is not None:
                        log.info("SpiffyRPG: found unit with name %s" % unit.name)

                        battle = SpiffyBattle(db=self.db,
                                              irc=irc,
                                              destination=msg.args[0])

                        """
                        In order to facilitate the player choosing
                        their attack, we equip the weapon by the 
                        type they choose.
                        """
                        equip_ok = player.equip_item_by_type(item_type=item_type)

                        """
                        If the player tries to equip an invalid weapon type,
                        they DIE. If all is well, the battle begins!
                        """
                        if equip_ok:
                            can_battle_info = player.can_battle_unit(unit=unit)

                            if can_battle_info["can_battle"]:
                                """
                                The target unit of the attack now equips a weapon!
                                """
                                unit.equip_random_weapon()

                                battle.add_party_member(player)
                                battle.add_party_member(unit)
                                battle.start()

                                dungeon.check_dungeon_cleared(player)
                            else:
                                reason = can_battle_info["reason"]
                                irc.error("You can't attack that. %s" % reason)
                        else:
                            dungeon.announcer.unit_death(unit=player)
                    else:
                        irc.error("You try to attack %s, but realize nothing is there" % ircutils.bold(target))
                else:
                    irc.error("You are dead.")
            else:
                irc.error("The dungeon collapses!")
        else:
            """ TODO: allow attacking players in PM """
            irc.error("You must attack channels in the channel.")

    attack = wrap(attack, ["user", "text"])

    def sbattle(self, irc, msg, args, user, target_nick_and_weapon):
        """
        Battles another user: /msg SpiffyRPG b <nick> <rock|paper|scissors|lizard|spock>
        """
        is_channel = irc.isChannel(msg.args[0])

        if is_channel:
            irc.error("Start battles in PM: /msg %s b" % (irc.nick))
            return

        target_nick, weapon = target_nick_and_weapon.split(" ", 1)

        """ If they don't specify a nick, they're battling themselves """
        if not target_nick:
            target_nick = msg.nick
            weapon = target_nick_and_weapon

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

        """ TODO: fix this """
        dungeon = self.SpiffyWorld.get_dungeon_by_channel(GAME_CHANNEL)

        if dungeon is not None:
            player_1 = dungeon.get_unit_by_user_id(attacker_user_id)
            player_2 = dungeon.get_unit_by_user_id(target_user_id)
            
            if player_1 is not None and player_2 is not None:
                battle = SpiffyBattle(db=self.db,
                                      irc=irc,
                                      destination=msg.args[0])

                battle.add_party_member(player_1)
                battle.add_party_member(player_2)
                battle.start()
            else:
                irc.error("The dungeon collapses.")

    sbattle = wrap(sbattle, ["user", "something"])

    def srank(self, irc, msg, args):
        """
        Shows top 3 players by experience gained
        """
        channel = msg.args[0]
        tmp_players = self.db.get_top_players_by_xp()
        top_players = []
        dungeon = self.SpiffyWorld.get_dungeon_by_channel(channel)

        if dungeon is not None:
            if len(tmp_players) > 0:
                for p in tmp_players:
                    d_p = dict(p)
                    
                    player = dungeon.get_unit_by_user_id(d_p["user_id"])
                    top_players.append(player)

                self.announcer.top_players(top_players)
            else:
                irc.error("There are no players yet!")

    srank = wrap(srank)
    
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
                    
                    self.announcer.player_role_change(player, role, unit_type_id)
                else:
                    classes = self._get_unit_type_list()

                    irc.error("Please choose one of the following roles: %s" % classes)

    srole = wrap(srole, ["user", "text"])

    def item(self, irc, msg, args, user, item_name):
        """
        Searches for an item by its name
        """
        item = self.unit_db.get_item_by_name(item_name=item_name)

        if item is not None:
            dungeon = self.SpiffyWorld.get_dungeon_by_channel(GAME_CHANNEL)

            if dungeon is not None:
                dungeon.announcer.item_info(item=item)
        else:
            irc.error("The tomes hold no mention of this artifact.")

    item = wrap(item, ["user", "text"])

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
                irc.error("A hulking terror emerges from the darkness and consumes you.")
        else:
            irc.error("You attempt to equip that item, but suddenly burst into flames!")

    equip = wrap(equip, ["user", "text"])

    def inventory(self, irc, msg, args):
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
            announcer = SpiffyPlayerAnnouncer(irc=irc,
                                              destination=msg.nick)

            announcer.inventory(player=player)
        else:
            irc.error("Your bags explode, blanketing you in flames!")

    def sinfo(self, irc, msg, args, target_nick):
        """
        Shows information about a player
        """
        if not target_nick:
            target_nick = msg.nick

        if not self._is_nick_in_channel(irc, target_nick):
            irc.error("I don't see that nick here")
            return

        channel = msg.args[0]
        info_target = msg.nick
        user_id = None

        try:
            target_hostmask = irc.state.nickToHostmask(target_nick)
            user_id = self._get_user_id(irc, target_hostmask)
        except KeyError:
            pass

        if user_id is not None:
            dungeon = self.SpiffyWorld.get_dungeon_by_channel(channel)

            if dungeon is not None:
                log.info("SpiffyRPG: looking up nick %s with user_id %s" % (target_nick, user_id))
                player = dungeon.get_unit_by_user_id(user_id)

                if player is not None:
                    dungeon.announcer.player_info(player=player)
                else:
                    irc.error("You peer into the dungeon, but see no one by that name.")
            else:
                """ TODO: this could probably be done outside of a dungeon """
                irc.error("The dungeon collapses!")
        else:
            irc.error("I could not find anything on that user.")

    sinfo = wrap(sinfo, [optional("text")])

    def raisedead(self, irc, msg, args, user, target):
        """
        Attempts to raise your target from the dead
        """
        user_id = self._get_user_id(irc, msg.prefix)
        channel = msg.args[0]
        dungeon = self.SpiffyWorld.get_dungeon_by_channel(channel)

        if dungeon is not None:
            player = dungeon.get_unit_by_user_id(user_id)
            unit = dungeon.get_dead_unit_by_name(target)

            if unit is not None:
                undead_effect = self.db.get_effect_by_name("Undead")

                unit.apply_effect(undead_effect)

                self.announcer.effect_raise_dead(player=player,
                                                 unit=unit)

                self.announcer.unit_info(unit=unit,
                                         player=player, 
                                         dungeon=dungeon)

                player.add_raised_unit(unit)
            else:
                irc.error("You attempt to perform the ritual, but something seems amiss.")
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
                self.dungeon_announcer.effect_applied_to_player(player, effect, duration)
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
            channel = msg.args[0]
            player = self.db.get_unit_by_user_id(user_id)

            if player is not None:
                irc.error("You look familiar...")
            else:
                valid_registration = self._is_valid_char_class(character_class)

                if valid_registration:
                    unit_type_id = self._get_unit_type_id_by_name(character_class)

                    if unit_type_id is not None:
                        log.info("SpiffyRPG: %s -> register '%s' the '%s' with class id %s " % (msg.nick, char_name, character_class, unit_type_id))

                        self.db.register_new_player(user_id, char_name, unit_type_id)
                        self.dungeon_announcer.new_player(irc, char_name, character_class)
                        irc.queueMsg(ircmsgs.voice(GAME_CHANNEL, msg.nick))
                    else:
                        log.error("SpiffyRPG: error determining class id from '%s'" % character_class)

                else:
                    classes = self._get_unit_type_list()
                    irc.reply("Please choose one of the following classes: %s" % classes)

    sjoin = wrap(sjoin, ["user", "text"])

    """ Admin-only commands """

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

    def fdungeoninit(self, irc, msg, args, channel):
        """
        fdungeoninit - force a dungeon to reinitialize
        """
        if not channel:
            channel = msg.args[0]

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

    def doQuit(self, irc, msg):
        user_id = None
        nick = None
        
        try:
            hostmask = irc.state.nickToHostmask(msg.nick)
            user_id = ircdb.users.getUserId(hostmask)
        except KeyError:
            log.info("SpiffyRPG: error getting hostmask for %s" % nick)

        if user_id is not None:
            dungeon = self.SpiffyWorld.get_dungeon_by_channel(GAME_CHANNEL)
            
            if dungeon is not None:
                unit = dungeon.get_unit_by_user_id(user_id)

                if unit is not None:
                    log.info("SpiffyRPG: removing %s from dungeon" % unit.name)

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

                    log.info("SpiffyRPG: nick change: %s is now known as %s, updating unit %s" % \
                    (old_nick, new_nick, unit.name))

    def doJoin(self, irc, msg):
        """
        Announces players joining
        """
        is_bot_joining = msg.nick == irc.nick
        user_id = None

        if not is_bot_joining:
            try:
                user_id = self._get_user_id(irc, msg.prefix)
            except KeyError:
                pass

            """
            Need to refactor this so that I don't have to repeat
            all the stuff in dungeon->populate
            """
            return

            if user_id is not None:
                user_ids = [str(user_id)]
                units = self.unit_db.get_units(user_ids=user_ids)
                player = None

                if len(units) > 0:
                    player = units[0]

                if player is not None:
                    dungeon = self.SpiffyWorld.get_dungeon_by_channel(msg.args[0])
      
                    if dungeon is not None:
                        unit = SpiffyUnit(unit=player,
                                          db=self.db,
                                          irc=irc,
                                          user_id=user_id,
                                          nick=msg.nick)

                        """ Voice recognized users """
                        irc.queueMsg(ircmsgs.voice(GAME_CHANNEL, msg.nick))
                        
                        """ Add player to dungeon """
                        dungeon.add_unit(unit)

                        if player.id in self.welcome_messages:
                            last_welcome = time.time() - self.welcome_messages[player.id]
                        else:
                            last_welcome = time.time() - self.welcome_message_cooldown_in_seconds
                        
                        if last_welcome > self.welcome_message_cooldown_in_seconds:
                            dungeon.announcer.player_info(player=player)
                            self.welcome_messages[player.id] = time.time()
                        else:
                            log.info("SpiffyRPG: not welcoming %s because cooldown" % player.name)

Class = SpiffyRPG


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
