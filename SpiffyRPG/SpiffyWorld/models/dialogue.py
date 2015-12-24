#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Dialogue:

    """
    Stores a lookup of all dialogue each time the world
    loads
    """

    def __init__(self, **kwargs):
        self.db = kwargs["db"]

    def get_dialogue(self, **kwargs):
        """
        Fetches dialogue for one or many units
        """
        cursor = self.db.cursor()

        cursor.execute("""SELECT
                          ud.id,
                          ud.dialogue,
                          ud.context,
                          CASE WHEN u.id IS NULL
                          THEN 0
                          ELSE u.id
                          END AS unit_id
                          FROM spiffyrpg_unit_dialogue ud
                          LEFT JOIN spiffyrpg_units u ON u.id = ud.unit_id""")

        tmp_dialogues = cursor.fetchall()

        cursor.close()
        dialogue = []

        if tmp_dialogues:
            for d in tmp_dialogues:
                dia = dict(d)

                dialogue.append(dia)

        return dialogue
