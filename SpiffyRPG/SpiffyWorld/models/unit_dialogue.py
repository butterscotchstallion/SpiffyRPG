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
                          ud.id AS dialogue_id,
                          ud.unit_id,
                          ud.dialogue,
                          ud.context
                          FROM spiffyrpg_unit_dialogue ud
                          LEFT JOIN spiffyrpg_units u ON u.id = ud.unit_id""")

        tmp_dialogue = cursor.fetchall()
        cursor.close()
        dialogue = []

        if tmp_dialogue:
            for e in tmp_dialogue:
                dia = dict(e)
                dialogue.append(dia)

        return self._get_unit_dialogue_map(dialogue)
