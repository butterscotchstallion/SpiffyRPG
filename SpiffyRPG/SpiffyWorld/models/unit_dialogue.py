#!/usr/bin/env python
# -*- coding: utf-8 -*-
class UnitDialogue:
    """
    Unit dialogue model
    """
    def __init__(self, **kwargs):
        self.db = kwargs["db"]
        self.dialogue = {}

    def _get_unit_dialogue_map(self, dialogue):
        unit_dialogue_map = {}

        for unit_dialogue in dialogue:
            unit_id = unit_dialogue["unit_id"]

            if unit_id not in unit_dialogue_map:
                unit_dialogue_map[unit_id] = []

            unit_dialogue_map[unit_id].append(unit_dialogue["dialogue_id"])

        return unit_dialogue_map

    def get_unit_dialogue(self):
        """
        Get unit dialogue IDs. Those will be queried
        against the dialogue collection to get the rest
        of the dialogue information
        """
        cursor = self.db.cursor()
        
        cursor.execute("""SELECT
                          d.id,
                          ue.unit_id
                          FROM spiffyrpg_dialogue d
                          JOIN spiffyrpg_unit_dialogue ue ON ue.dialogue_id = d.id
                          JOIN spiffyrpg_units u ON u.id = ue.unit_id""")

        tmp_dialogue = cursor.fetchall()
        cursor.close()
        dialogue = []

        if tmp_dialogue:
            for e in tmp_dialogue:
                dialogue = dict(e)
                dialogue.append(dialogue)

        return self._get_unit_dialogue_map(dialogue)