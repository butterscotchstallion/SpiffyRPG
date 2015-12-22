#!/usr/bin/env python
# -*- coding: utf-8 -*-
from SpiffyWorld import Unit

class DungeonUnitCollection:
    """
    Stores persistant units in a dungeon by the dungeon ID
    """


    def __init__(self, **kwargs):
        self.units = []

    def add(self, unit):
        if not isinstance(unit, Unit):
            raise ValueError("unit must be an instance of Unit")

        if unit not in self.units:
            self.units.append(unit)
