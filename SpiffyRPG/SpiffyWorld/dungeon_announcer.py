#!/usr/bin/env python
# -*- coding: utf-8 -*-
from SpiffyWorld import Announcer
import time
import supybot.log as log
import random


class DungeonAnnouncer(Announcer):
    """
    Announcements specific to dungeon events
    """
    def __init__(self, **kwargs):
        announcer_parent = super(DungeonAnnouncer, self)
        announcer_parent.__init__(irc=kwargs["irc"],
                                  ircutils=kwargs["ircutils"],
                                  ircmsgs=kwargs["ircmsgs"],
                                  destination=kwargs["destination"],
                                  public=True)

    def necromancer_raised_dead(self, **kwargs):
        dead_unit = kwargs["dead_unit"]
        necro = kwargs["necro"]
        unit_name = self._get_unit_title(dead_unit)
        necro_name = self._get_unit_title(necro)

        announcement_msg = "%s raised %s from the dead!" % (necro_name, unit_name)

        self.announce(announcement_msg)

    def unit_spell_interrupted(self, **kwargs):
        unit = kwargs["unit"]
        attacker = kwargs["attacker"]
        unit_name = self._get_unit_title(unit)
        attacker_name = self._get_unit_title(attacker)

        announcement_msg = "%s interrupts %s's spell!" % (attacker_name, unit_name)

        self.announce(announcement_msg)

    def necro_raising_dead(self, **kwargs):
        necro = kwargs["necro"]
        dead_unit = kwargs["dead_unit"]
        necro_name = self._get_unit_title(necro)
        unit_name = self._get_unit_title(dead_unit)

        announcement_msg = "%s begins raising %s from the dead!" % (necro_name, unit_name)
        #announcement_msg += " Attack it to interrupt the spell!"

        self.announce(announcement_msg)

    def challenge_accepted(self, **kwargs):
        attacker = kwargs["attacker"]
        target = kwargs["target"]

        params = (self._get_unit_title(attacker), self._get_unit_title(target))

        announcement_msg = "It's on between %s and %s!" % params

        self.announce(announcement_msg)

    def unit_death(self, **kwargs):
        """
        This occurs when the player tries to do something
        silly, like attack with a weapon type that doesn't exist.
        """
        unit = kwargs["unit"]
        unit_name = self._get_unit_title(unit)

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
            log.error("SpiffyWorld: no dialogue for %s" % unit.get_name())
            return

        bold_title = self._get_unit_title(unit)
        orange_dialogue = self._c(dialogue, "orange")

        params = (bold_title, orange_dialogue)

        announcement_msg = "%s: %s" % params

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
        player = kwargs["player"]
        irc = kwargs["irc"]
        item_name = self._b(self._c(item.name, "light blue"))
        rarity_indicator = self.get_rarity_indicator(rarity=item.rarity)
        item_type_indicator = item.get_indicator()
        params = (rarity_indicator,
                  item_name,
                  item_type_indicator)

        announcement_msg = "%s %s [%s]" % params

        if item.description is not None:
            announcement_msg += " %s" % item.description

        if player is not None:
            if player.get_equipped_weapon().id == item.id:
                announcement_msg += ". This item is currently equipped."

        if item.is_permanent:
            announcement_msg += " :: No Drop"

        """
        Use/effect information. An item is only usable if it
        is explicitly defined as such and it has at least one
        effect.
        """
        if item.is_usable() and len(item.effects) > 0:
            announcement_msg += " :: %s causes " % self._b(".use")
            effect_names = ", ".join([self._c(effect.name, "light blue") for effect in item.effects])

            announcement_msg += effect_names

            charges_word = "charges"

            if item.charges == 1:
                charges_word = "charge"

            announcement_msg += " :: %s %s" % (self._b(item.charges), charges_word)

        irc.reply(announcement_msg, notice=True)

    def effect_info(self, **kwargs):
        effect = kwargs["effect"]
        effect_name = self._b(self._c(effect.name, "light blue"))
        params = (effect_name,
                  effect.description)

        announcement_msg = "%s :: %s" % params

        kwargs["irc"].reply(announcement_msg)

    def unit_attack(self, **kwargs):
        attack_word = "hits"
        player_1 = kwargs["player_1"]
        attack = kwargs["attack"]

        if attack["is_critical_strike"]:
            attack_word = \
                ircutils.mircColor("critically strikes", fg="red", bg="black")

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
        utitle = self._b(unit.get_name())

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

    def dialogue_intro(self, unit, intro):
        colored_intro = ircutils.mircColor(intro, fg="orange")
        bold_title = ircutils.bold(unit.title)
        params = (bold_title, colored_intro)
        announcement_msg = "%s: %s" % params

        self._send_channel_notice(announcement_msg)

    def unit_info(self, **kwargs):
        """
        Shows information about a dungeon unit
        """
        irc = kwargs["irc"]
        unit = kwargs["unit"]
        dungeon = kwargs["dungeon"]

        """
        Units start alive
        """
        seconds_alive = int(time.time() - unit.created_at)
        alive_duration = self._get_duration(seconds_alive)

        """
        Also track how long the unit has been dead
        """
        seconds_dead = 0
        dead_duration = 0

        if not unit.is_alive() and unit.slain_at is not None:
            seconds_dead = int(time.time() - unit.slain_at)
            dead_duration = self._get_duration(seconds_dead)

        pink_heart = self._c(u"♥", "pink")
        unit_title = self._get_unit_title(unit)
        level = unit.level

        """
        Color level according to hostility
        combat_status = self._c(unit.combat_status, "yellow")
        """
        if unit.combat_status == "hostile":
            level = self._c(level, "red")

        if unit.combat_status == "friendly":
            level = self._c(level, "green")

        """
        Color HP accordingly
        """
        hp = "{:,}".format(unit.get_hp())

        if not unit.is_alive():
            hp = self._c(hp, "red")

        body_count = "{:,}".format(len(unit.get_slain_units()))
        unit_slain_count = self._c(body_count, "red")
        stage = unit.get_stage_by_level(level=unit.level)
        cname = self._c(unit.get_title(), "light green")
        percent_xp = self._get_level_xp_percentage(unit=unit)

        msg = "[%s] %s%% %s %s [%s] %s %s" % \
            (level, percent_xp, unit_title, cname, stage, pink_heart, hp)

        if unit.is_alive():
            msg += " :: %s %s" % (self._c("Alive", "green"), alive_duration)
        else:
            msg += " :: %s %s" % (self._c("Dead", "red"), dead_duration)

        if body_count > 0:
            msg += " :: %s slain" % unit_slain_count

        if len(unit.effects) > 0:
            msg += " :: %s " % self._b("Effects")
            msg += self._c(unit.get_effects_list(), "light blue")

        hot_streak = unit.is_on_hot_streak()

        if hot_streak is not None:
            msg += " Hot Streak: %s" % self._b(hot_streak)

        if unit.is_boss:
            msg += " :: This is a %s" % self._b("boss")

        irc.reply(msg, notice=True)

    def _get_level_xp_percentage(self, **kwargs):
        unit = kwargs["unit"]
        unit_xp = unit.experience

        xp_req_for_this_level = unit.get_xp_required_for_next_level() + 1
        xp_req_for_previous_level = unit.get_xp_required_for_previous_level() + 1

        """ Unit is above max level """
        if unit_xp >= xp_req_for_this_level:
            xp_req_for_this_level = self.levels[-1][1]

        percent_xp = int(((float(unit_xp - xp_req_for_previous_level) / (float(xp_req_for_this_level - xp_req_for_previous_level))) * 100))

        if percent_xp <= 20:
            xp_color = "yellow"
        elif percent_xp > 20 and percent_xp < 75:
            xp_color = "white"
        elif percent_xp >= 75:
            xp_color = "green"
        elif percent_xp < 0:
            xp_color = "purple"
            percent_xp = "100"

        colored_xp = self._c(percent_xp, xp_color)

        return colored_xp

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
        attacker = kwargs["attacker"]

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
        irc = kwargs["irc"]
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
                unit_name = self._b(unit.get_name())

                if is_seance:
                    unit_name = self._c(unit_name, "red")

                if unit.is_undead():
                    unit_name = self._c(unit_name, "light blue")

                unit_level = self._c(unit.level, "green")
                unit_titles.append("%s (%s)" % (unit_name, unit_level))

            msg += ", ".join(unit_titles)
        else:
            msg = "%s %s %s but sees nothing of interest" % \
                (player_name, look_phrase, dungeon_name)

        irc.reply(msg, notice=True)

    def inspect_target(self, **kwargs):
        player = kwargs["player"]
        irc = kwargs["irc"]
        unit = kwargs["unit"]
        dungeon = kwargs["dungeon"]

        log.info("SpiffyRPG: inspecting %s" % unit.get_name())

        self.unit_info(unit=unit,
                       player=player,
                       dungeon=dungeon,
                       irc=irc)

    def look_failure(self, **kwargs):
        irc = kwargs["irc"]
        words = ["looks around", "inspects the surroundings",
                 "scans the area of"]
        look_phrase = random.choice(words)
        player_name = self._get_unit_title(kwargs["player"])
        dungeon_name = self._get_dungeon_title(kwargs["dungeon"])

        msg = "%s %s %s but sees nothing of import" % \
            (player_name, look_phrase, dungeon_name)

        irc.reply(msg, notice=True)

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
