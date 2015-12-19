# -*- coding: utf-8 -*-

class UnitType:
    """
    Representation of a unit type
    """
    def __init__(self, **kwargs):
        unit_type = kwargs["unit_type"]

        self.id = unit_type["id"]
        self.name = unit_type["name"]
        self.is_playable = False

        if "is_playable" in kwargs:
            self.is_playable = kwargs["is_playable"]

    def __eq__(self, other):
        return self.name.lower().startswith(other.name.lower())