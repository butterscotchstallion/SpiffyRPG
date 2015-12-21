# -*- coding: utf-8 -*-
from uuid import uuid4
from random import randrange, choice
from SpiffyWorld import Effect
import time

class EffectGenerator:
    """
    Generates units dynamically.
    TODO: use UnitBuilder so this can make
    items with effects
    """
    def generate(self, **kwargs):
        effect_id = uuid4()
        operators = ("+", "-", "*", "/")
        operator = choice(operators)
        effect_name = "Effect%s" % (effect_id)

        if "operator" in kwargs:
            operator = kwargs["operator"]

        if "combat_status" in kwargs:
            combat_status = kwargs["combat_status"]
        
        if "effect_name" in kwargs and kwargs["effect_name"] is not None:
            effect_name = kwargs["effect_name"]
        
        effect_model = {
            "id": effect_id,
            "name": effect_name,
            "operator": operator,
            "description": "quux",
            "hp_adjustment": 0,
            "incoming_damage_adjustment": 0,
            "outgoing_damage_adjustment": 0,
            "interval_seconds": 0,
            "stacks": 0
        }

        effect = Effect(effect=effect_model)

        return effect
