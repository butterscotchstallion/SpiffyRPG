# -*- coding: utf-8 -*-
from uuid import uuid4
from random import randrange, choice
from SpiffyWorld import Item

class ItemGenerator:
    """
    Generates items dynamically.
    TODO: use ItemBuilder so this can make
    items with effects
    """
    def generate(self, **kwargs):
        item_id = uuid4()
        item_name = "TestItem-%s" % item_id
        item_types = ("rock", "scissors", "paper", "lizard", "spock")
        item_type = choice(item_types)
        is_permanent = 0
        charges = 0
        can_use = 0

        if "item_name" in kwargs:
            item_name = kwargs["item_name"]
        
        if "item_type" in kwargs:
            specified_item_type = kwargs["item_type"]

            if specified_item_type not in item_types:
                raise ValueError("Invalid item_type")

            item_type = specified_item_type

        if "is_permanent" in kwargs:
            is_permanent = kwargs["is_permanent"]

        if "charges" in kwargs:
            charges = kwargs["charges"]

        if "can_use" in kwargs:
            can_use = kwargs["can_use"]

        item_model = {
            "id": item_id,
            "name": item_name,
            "description": "foo",
            "effects": [],
            "min_level": 1,
            "max_level": 100,
            "rarity": "dank",
            "equipment_slot": "main hand",
            "is_permanent": is_permanent,
            "unit_type_id": 0,
            "can_use": charges,
            "charges": can_use,
            "created_at": "1",
            "item_type": item_type
        }

        item = Item(item=item_model)

        return item
