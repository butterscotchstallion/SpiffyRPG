#!/usr/bin/env python
# -*- coding: utf-8 -*-


class UnitDialogue:

    """
    Dialogue object for Units
    """

    def __init__(self, **kwargs):
        dialogue = kwargs["dialogue"]

        self.id = dialogue["id"]
        self.dialogue = dialogue["dialogue"]
        self.context = dialogue["context"]

        """
        unit_id can be zero in the case of dialogue
        that any unit can use, like zombie
        """
        self.unit_id = dialogue["unit_id"]
