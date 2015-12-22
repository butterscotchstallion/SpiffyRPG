#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging as log
from SpiffyWorld import Effect

class EffectCollection:
    """
    Effects catalog
    """
    def __init__(self, **kwargs):
        self.effects = []

    def add(self, effect):
        if not isinstance(effect, Effect):
            raise ValueError("effect must be an instance of Effect")

        if effect not in self.effects:
            self.effects.append(effect)

    def get_effect_undead(self):
        return self.get_effect_by_effect_name(effect_name="Undead")

    def get_effect_by_effect_name(self, **kwargs):
        name = kwargs["effect_name"].lower()

        for effect in self.effects:
            if name in effect.name.lower():
                return effect

    def get_effects_by_effect_id_list(self, effect_id_list):
        return [effect for effect in self.effects if effect.id in effect_id_list]
