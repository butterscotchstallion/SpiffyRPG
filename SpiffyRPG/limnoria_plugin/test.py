###
# Copyright (c) 2015, butterscotchstallion
# All rights reserved.
#
#
###

from supybot.test import *
import os
import shutil
import random


class SpiffyRPGTestCase(ChannelPluginTestCase):
    plugins = ("User",)
    channel = "#SpiffyRPG"

    def _assert_response_not_error(self, message):
        self.assertFalse(message.startswith("Error: "))

    def setUp(self):
        ChannelPluginTestCase.setUp(self)

        """
        Register tester nick
        """
        self.prefix = "SpiffyTester!SpiffyTester@example.com"

        self.feedMsg("register SpiffyTester SpiffyPW",
                     to=self.nick,
                     frm=self.prefix)
        # "The operation suceeded"
        _ = self.getMsg(' ')

        self.feedMsg("hostmask add *!*@example.com",
                     to=self.nick,
                     frm=self.prefix)
        # "The operation suceeded"
        _ = self.getMsg(' ')

        # copy test db
        filename = "SpiffyRPG.sqlite3.db"
        parent_dir = os.path.realpath("..")
        test_db_src = "%s/SpiffyRPG/test/functional/fixture/%s" % \
            (parent_dir, filename)
        test_db_destination = "%s/test-data/%s" % \
            (os.path.realpath("."), filename)

        shutil.copy(test_db_src, test_db_destination)

        assert os.path.exists(test_db_destination)

        self.assertNotError("load SpiffyRPG")
        # "The operation suceeded"
        _ = self.getMsg(' ')

        classes = ("hacker", "zen master", "troll")
        sclass = random.choice(classes)

        self.assertRegexp("sjoin %s" % sclass, "joined the game")

    def test_rock_strike(self):
        self.assertRegexp("rock john", "hits")
        _ = self.getMsg(' ')

    def test_paper_strike(self):
        self.assertRegexp("paper rabid", "hits")
        _ = self.getMsg(' ')

    def test_scissors_strike(self):
        self.assertRegexp("scissors rad", "hits")
        _ = self.getMsg(' ')

    def test_lizard_strike(self):
        self.assertRegexp("lizard tech", "hits")
        _ = self.getMsg(' ')

    def test_spock_strike(self):
        self.assertRegexp("spock really", "hits")
        _ = self.getMsg(' ')

    def test_help(self):
        self.assertRegexp("spiffyrpg help", "Basic commands")
        _ = self.getMsg(' ')

    def test_inspect(self):
        # self inspect
        self.assertRegexp("inspect", "THRILLHOUSE")
        _ = self.getMsg(' ')

        # should emit look failed message
        self.assertRegexp("inspect a wild coyote", "nothing")
        _ = self.getMsg(' ')

    def test_inspect_something(self):
        self.assertNotError("inspect john")
        _ = self.getMsg(' ')

    def test_topplayers(self):
        self.assertNotError("topplayers")
        _ = self.getMsg(' ')

    def test_map(self):
        self.assertRegexp("smap", "You have been in")
        _ = self.getMsg(' ')

    def test_look(self):
        self.assertNotError("look")
        _ = self.getMsg(' ')

    def test_seance(self):
        self.assertRegexp("seance", "does not sense")
        _ = self.getMsg(' ')

    def test_title(self):
        self.assertRegexp("title quux", "quux")
        _ = self.getMsg(' ')

    def test_rock(self):
        self.assertHelp("rock")
        _ = self.getMsg(' ')

    def test_paper(self):
        self.assertHelp("paper")
        _ = self.getMsg(' ')

    def test_scissors(self):
        self.assertHelp("scissors")
        _ = self.getMsg(' ')

    def test_lizard(self):
        self.assertHelp("lizard")
        _ = self.getMsg(' ')

    def test_spock(self):
        self.assertHelp("spock")
        _ = self.getMsg(' ')

    def test_equip(self):
        self.assertHelp("equip")
        _ = self.getMsg(' ')

    def test_inventory(self):
        self.assertNotError("inventory")
        _ = self.getMsg(' ')

    def test_effect(self):
        self.assertHelp("effect")
        _ = self.getMsg(' ')

    def test_raise(self):
        self.assertHelp("raisedead")
        _ = self.getMsg(' ')
