# -*- coding: utf-8 -*-
from uuid import uuid4
from random import randrange, choice
from SpiffyWorld import Unit, UnitLevel

class UnitGenerator:
    """
    Generates units dynamically.
    TODO: use UnitBuilder so this can make
    items with effects
    """
    def generate(self, **kwargs):
        unit_level = UnitLevel()
        is_player = False
        level = randrange(1, 100)
        xp = unit_level.get_xp_for_level(level)
        unit_id = uuid4()
        combat_status = "passive"

        if "combat_status" in kwargs:
            combat_status = kwargs["combat_status"]
        
        if "unit_name" in kwargs:
            unit_name = kwargs["unit_name"]
        else:
            unit_name = "Level%sUnit%s" % (level, unit_id)

        unit_types = (1, 2, 3)
        unit_type_id = choice(unit_types)
        
        user_id = 0

        if "is_player" in kwargs:
            is_player = kwargs["is_player"]
            user_id = randrange(1, 999)

        if "user_id" in kwargs:
            user_id = kwargs["user_id"]

        unit_model = {
            "id": unit_id,
            "unit_name": unit_name,
            "items": [],
            "effects": [],
            "dialogue": [],
            "experience": xp,
            "level": level,
            "user_id": user_id,
            "is_boss": 0,
            "unit_type_id": unit_type_id,
            "unit_type_name": "quux",
            "combat_status": combat_status
        }

        unit = Unit(unit=unit_model)

        return unit
