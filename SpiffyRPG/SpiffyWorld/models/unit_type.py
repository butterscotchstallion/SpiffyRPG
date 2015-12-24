#!/usr/bin/env python
# -*- coding: utf-8 -*-


class UnitType:

    """
    Unit type model
    """

    def __init__(self, **kwargs):
        self.db = kwargs["db"]

    def get_unit_types(self):
        cursor = self.db.cursor()

        cursor.execute("""SELECT id, name
                          FROM spiffyrpg_unit_types""")

        unit_types = cursor.fetchall()

        cursor.close()

        return unit_types
