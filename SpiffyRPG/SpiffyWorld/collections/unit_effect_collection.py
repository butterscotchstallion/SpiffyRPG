import logging as log
from SpiffyWorld import Effect

class UnitEffectCollection:
    """
    Representation of persisted effects on a unit
    """
    def __init__(self, **kwargs):
        self.effects = []

    def add(self, effect):
        if effect not in self.effects:
            self.effects.append(effect)

    def get_effects_by_unit_id(self, **kwargs):
        return [effect for effect in self.effects in effect]