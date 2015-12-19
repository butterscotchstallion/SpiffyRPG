# -*- coding: utf-8 -*-
class Item:
    """
    Representation of an item which a unit can possess
    """
    def __init__(self, **kwargs):
        item = kwargs["item"]

        self.id = item["id"]
        self.effects = item["effects"]
        self.name = item["name"]
        self.description = item["description"]
        self.min_level = item["min_level"]
        self.max_level = item["max_level"]
        self.rarity = item["rarity"]
        self.equipment_slot = item["equipment_slot"]
        self.item_type = item["item_type"].lower()
        self.is_permanent = item["is_permanent"] == "1" or item["is_permanent"]
        self.unit_type_id = item["unit_type_id"]
        self.created_at = item["created_at"]
        self.charges = int(item["charges"])
        self.can_use = item["can_use"] == 1

    def is_usable(self):
        return self.can_use

    def is_potion(self):
        return self.item_type == "potion"

    def get_indicator(self):
        indicator = self.item_type[0].upper()

        if self.item_type == "spock":
            indicator = "V"

        if self.is_potion():
            indicator = "i"

        return indicator

    def is_rock(self):
        return self.item_type == "rock"

    def is_paper(self):
        return self.item_type == "paper"

    def is_scissors(self):
        return self.item_type == "scissors"

    def is_lizard(self):
        return self.item_type == "lizard"

    def is_spock(self):
        return self.item_type == "spock"

    def is_usable_by_level(self, **kwargs):
        return self.min_level <= kwargs["level"] and \
        kwargs["level"] <= self.max_level
