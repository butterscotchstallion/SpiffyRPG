###
# Copyright (c) 2015, butterscotchstallion
# All rights reserved.
#
#
###

from supybot.test import *
import supybot.ircdb as ircdb


class SpiffyRPGTestCase(PluginTestCase):
    plugins = ("SpiffyRPG", "User")

    def setUp(self):
        PluginTestCase.setUp(self)

        """
        Almost all commands require a registered user
        """
        self.irc.nick = "SpiffyTester"
        self.irc.prefix = "SpiffyTester!SpiffyTester@example.com"
        self.channel = "#SpiffyRPG"
        self.irc.feedMsg(ircmsgs.privmsg(self.irc.nick,
                                         'register foo bar',
                                         prefix=self.irc.prefix))
        _ = self.irc.takeMsg()
        self.irc.feedMsg(ircmsgs.join(self.channel, prefix=self.irc.prefix))

    def test_inspect(self):
        # Inspect nothing (self)
        self.assertNotError("spiffyrpg inspect")
