###
# Copyright (c) 2015, butterscotchstallion
# All rights reserved.
#
#
###

from supybot.test import *
import supybot.ircdb as ircdb
import unittest
import os
import shutil


#@unittest.skip("Skipping Limnoria tests (run with supybot-test)")
class SpiffyRPGTestCase(ChannelPluginTestCase):
    plugins = ("SpiffyRPG", "User")

    def setUp(self):
        ChannelPluginTestCase.setUp(self)

        """
        Almost all commands require a registered user
        """
        self.nick = "SpiffyTester"
        self.prefix = "SpiffyRPG!SpiffyRPG@example.com"
        self.test_channel = "#SpiffyRPG"
        self.channel = self.test_channel
        self.irc.feedMsg(ircmsgs.privmsg(self.irc.nick,
                                         "register foo bar",
                                         prefix=self.prefix))
        _ = self.irc.takeMsg()

        # copy test db
        filename = "SpiffyRPG.sqlite3.db"
        parent_dir = os.path.realpath("..")
        test_db_src = "%s/SpiffyRPG/test/functional/fixture/%s" % (parent_dir, filename)
        test_db_destination = "%s/test-data/%s" % (os.path.realpath("."), filename)

        shutil.copy(test_db_src, test_db_destination)
        #print "SpiffyRPG test database copy successful!"

        assert os.path.exists(test_db_destination)

        self._join_test_channel()

    def _join_test_channel(self):
        self.irc.feedMsg(ircmsgs.join(self.test_channel, prefix=self.prefix))

    def _send_channel_command(self, command):
        self.irc.feedMsg(ircmsgs.privmsg(self.test_channel,
                                         command,
                                         prefix=self.prefix))

    def test_inspect(self):
        self._send_channel_command("inspect")

    def test_topplayers(self):
        self._send_channel_command("top")

    def test_map(self):
        self._send_channel_command("map")

    def test_look(self):
        self._send_channel_command("look")
