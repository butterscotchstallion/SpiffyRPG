# -*- coding: utf-8 -*-
import unittest
from SpiffyWorld.collections import DungeonUnitCollection
from SpiffyWorld import Dungeon
import logging

log = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)

class TestDungeonUnitCollection(unittest.TestCase):
    def test_something(self):
        pass