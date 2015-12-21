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
        hp_adjustment = 0
        incoming_damage_adjustment = 0
        outgoing_damage_adjustment = 0
        interval_second = 0
        stacks = 1
        
        if "operator" in kwargs:
            operator = kwargs["operator"]

        if "combat_status" in kwargs:
            combat_status = kwargs["combat_status"]
        
        if "effect_name" in kwargs and kwargs["effect_name"] is not None:
            effect_name = kwargs["effect_name"]
        
        if "hp_adjustment" in kwargs:
            hp_adjustment = kwargs["hp_adjustment"]

        if "incoming_damage_adjustment" in kwargs:
            incoming_damage_adjustment = kwargs["incoming_damage_adjustment"]

        if "outgoing_damage_adjustment" in kwargs:
            outgoing_damage_adjustment = kwargs["outgoing_damage_adjustment"]

        if "stacks" in kwargs:
            stacks = kwargs["stacks"]

        effect_model = {
            "id": effect_id,
            "name": effect_name,
            "operator": operator,
            "description": "quux",
            "hp_adjustment": hp_adjustment,
            "incoming_damage_adjustment": incoming_damage_adjustment,
            "outgoing_damage_adjustment": outgoing_damage_adjustment,
            "interval_seconds": interval_second,
            "stacks": stacks
        }

        effect = Effect(effect=effect_model)

        return effect
