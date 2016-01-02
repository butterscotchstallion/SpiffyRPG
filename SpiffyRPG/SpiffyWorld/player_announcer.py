#!/usr/bin/env python
# -*- coding: utf-8 -*-
from SpiffyWorld import Announcer
import random


class PlayerAnnouncer(Announcer):
    """
    Announcements specific to players
    """
    def __init__(self, **kwargs):
        announcer_parent = super(PlayerAnnouncer, self)
        announcer_parent.__init__(irc=kwargs["irc"],
                                  ircutils=kwargs["ircutils"],
                                  ircmsgs=kwargs["ircmsgs"],
                                  destination=kwargs["destination"],
                                  public=False)
        self.public = False

    def use_item(self, **kwargs):
        item = kwargs["item"]
        irc = kwargs["irc"]
        item_name = self._b(item.name)

        announcement_msg = "%s glows intensely for a moment " % item_name
        announcement_msg += "and fades. You feel invigorated."

        irc.reply(announcement_msg, notice=True)

    def found_loot(self, **kwargs):
        item = kwargs["item"]
        item_name = self._b(item.name)

        announcement_msg = "%s has been added to your inventory" % item_name

        self.announce(announcement_msg)

    def unit_slain(self, **kwargs):
        unit = kwargs["unit"]

        announcement_msg = "You have slain %s!" % self._b(unit.get_name())

        self.announce(announcement_msg)

    def attack_miss(self, **kwargs):
        hit_info = kwargs["hit_info"]
        target = kwargs["target"]
        params = (hit_info["attacker_weapon"].name, target.name)

        announcement_msg = "Your %s misses %s!" % params

        self.announce(announcement_msg)

    def damage_dealt(self, **kwargs):
        attack_info = kwargs["attack_info"]
        target = kwargs["target"]
        attacker_item = attack_info["attacker_weapon"]
        params = (attacker_item.name, target.name, attack_info["damage"])

        announcement_msg = "Your %s hits %s for %s damage" % params

        self.announce(announcement_msg)

    def draw(self, **kwargs):
        item_name = kwargs["item_name"]
        target_name = kwargs["target_name"]

        params = (item_name, target_name)
        announcement_msg = "Your %s misses %s!" % params

        self.announce(announcement_msg)

    def damage_applied(self, **kwargs):
        attack_info = kwargs["attack_info"]
        attacker = kwargs["attacker"]
        item = attack_info["attacker_weapon"]

        params = (attack_info["damage"], attacker.name, item.name)

        announcement_msg = "You take %s damage from %s's %s" % params

        self.announce(announcement_msg)

    def battle_round(self, **kwargs):
        combatant = kwargs["combatant"]
        player = kwargs["player"]
        rounds_remaining = kwargs["rounds_remaining"]
        params = (player.name, combatant.name, rounds_remaining)

        announcement_msg = "%s vs. %s: %s rounds remaining" % params

        self.announce(announcement_msg)

    def challenge_sent(self, **kwargs):
        player_nick = self._b(kwargs["player_nick"])

        announcement_msg = "Challenge sent to %s" % player_nick

        self.announce(announcement_msg)

    def challenge_received(self, **kwargs):
        player_nick = self._b(kwargs["player_nick"])

        announcement_msg = "You have been challenged by %s. type \"accept %s\" to allow them to attack you!" % (player_nick, player_nick)

        self.announce(announcement_msg)

    def unit_death(self):
        died = self._c("died", "red")
        announcement_msg = "You have %s. Don't worry though, you'll regenerate HP automatically over time :)" % died

        self.announce(announcement_msg)

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
        irc = kwargs["irc"]
        items = player.items

        if len(items) > 0:
            item_name_list = []

            for item in player.items:
                item_type = item.get_indicator()
                item_name = self._b(item.name)

                """
                Display usable items differently
                """
                if item.can_use:
                    item_name = self._c(item_name, "light blue")

                item_name = "%s [%s]" % (item_name, item_type)
                item_name_list.append(item_name)

            announcement_msg = ", ".join(item_name_list)
        else:
            announcement_msg = "Your inventory appear empty."

        irc.reply(announcement_msg, notice=True)

    def item_equip(self, **kwargs):
        item = kwargs["item"]
        item_name = self._b(item.name)

        announcement_msg = "You have equipped %s" % item_name

        self.announce(announcement_msg)

    def player_regenerates(self, **kwargs):
        regen_hp = self._b(kwargs["regen_hp"])
        params = (regen_hp, self.get_pink_heart())

        announcement_msg = "You receive %s %s from Regeneration." % params

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
