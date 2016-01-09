#!/usr/bin/env python
# -*- coding: utf-8 -*-
from SpiffyWorld import UnitLevel
GAME_CHANNEL = "#SpiffyRPG"


class Announcer(object):

    """
    There are two types of announcements:

    1. Dungeon (Public) - announcements made in the channel
       SpiffyDungeonAnnouncer fulfills this role.
    2. Player (Private) - announcements made directly to the
       player

    The destination of the announcement is set when the announcer
    is instantiated.
    """
    is_public = True

    def __init__(self, **kwargs):
        self._irc = kwargs["irc"]
        self.is_public = kwargs["public"]
        self.destination = kwargs["destination"]
        self.ircutils = kwargs["ircutils"]
        self.ircmsgs = kwargs["ircmsgs"]
        unit_levels = UnitLevel()
        self.levels = unit_levels.get_levels()
        self.log = None
        self.testing = False

        if "log" in kwargs:
            self.log = kwargs["log"]

        if "testing" in kwargs:
            self.testing = kwargs["testing"]

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

        bold_title = self._b(unit.get_name())
        indicator = self._get_unit_indicator(unit)

        if unit.is_player and unit.unit_type_id in role_colors:
            role_color = role_colors[unit.unit_type_id]
            bold_title = self._c(bold_title, role_color)

        if unit.is_undead():
            bold_title = self._c(bold_title, "light blue")

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
            indicator = self._c(indicator, "light green")

        return indicator

    def get_pink_heart(self):
        return self._c(u"♥", "pink")

    def announce(self, message):
        if self.is_public:
            self._send_channel_notice(message)
        else:
            self._send_player_notice(message)

    def _b(self, input):
        return self.ircutils.bold(input)

    def _c(self, input, text_color):
        return self.ircutils.mircColor(input, fg=text_color)

    def _get_effect_text(self, input):
        return self.ircutils.mircColor(input, fg="light blue")

    def _get_duration(self, seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        existed_timestamp = "%02d:%02d" % (m, s)

        if h > 0:
            existed_timestamp = "%d:%s" % (h, existed_timestamp)

        return existed_timestamp

    def _is_nick_in_channel(self, irc, nick):
        return nick in irc.state.channels[GAME_CHANNEL].users

    def _send_player_notice(self, message):
        nick_in_channel = self._is_nick_in_channel(self._irc, self.destination)

        if nick_in_channel:
            self._irc.queueMsg(self.ircmsgs.notice(self.destination, message))
        else:
            if self.log is not None:
                self.log.info("Suppressing player notice to non-existent player %s" %
                              self.destination)

    def _send_channel_notice(self, message):
        """
        All event communication should be sent as a channel notice
        """
        if not self.testing:
            self._irc.queueMsg(self.ircmsgs.notice(GAME_CHANNEL, message))
