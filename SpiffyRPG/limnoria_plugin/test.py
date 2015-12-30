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
        reg_response = self.getMsg(" ")

        self.feedMsg("hostmask add *!*@example.com",
                     to=self.nick,
                     frm=self.prefix)
        hostmask_response = self.getMsg(" ")

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

        classes = ("hacker", "zen master", "troll")
        sclass = random.choice(classes)
        self.assertNotError("sjoin %s" % sclass)

    def test_help(self):
        self.assertNotError("spiffyrpg help")

    def test_inspect(self):
        self.assertNotError("inspect")

    def test_inspect_something(self):
        self.assertNotError("inspect john")

    def test_topplayers(self):
        self.assertNotError("topplayers")

    def test_map(self):
        self.assertNotError("smap")

    def test_look(self):
        self.assertNotError("look")

    def test_seance(self):
        self.assertNotError("seance")

    def test_title(self):
        self.assertNotError("title THRILLHOUSE")

    def test_rock(self):
        self.assertNotError("rock")

    def test_paper(self):
        self.assertNotError("paper")

    def test_scissors(self):
        self.assertNotError("scissors")

    def test_lizard(self):
        self.assertNotError("lizard")

    def test_spock(self):
        self.assertNotError("spock")

    def test_equip(self):
        self.assertNotError("equip rock")

    def test_items(self):
        self.assertNotError("items")

    def test_effect(self):
        self.assertNotError("effect")

    def test_raise(self):
        self.assertNotError("raise")
