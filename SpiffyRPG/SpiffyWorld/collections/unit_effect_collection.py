#!/usr/bin/env python
# -*- coding: utf-8 -*-


class UnitEffectCollection:

    """
    Representation of persisted effects on a unit
    """

    def __init__(self, **kwargs):
        self.effects = []

    def add(self, effect):
        if effect not in self.effects:
            self.effects.append(effect)
