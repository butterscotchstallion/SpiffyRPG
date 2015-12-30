#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from SpiffyWorld import PlayerAnnouncer


class TestPlayerAnnouncer(unittest.TestCase):

    """
    PlayerAnnouncer tests
    """
    def test_stuff(self):
        announcer = PlayerAnnouncer(irc="quux",
                                    ircmsgs="quux",
                                    ircutils="quux",
                                    destination="quux")

        self.assertIsInstance(announcer, PlayerAnnouncer)

if __name__ == '__main__':
    unittest.main()
