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

        unit_types_tmp = cursor.fetchall()
        unit_types = []
        cursor.close()

        if unit_types_tmp:
            for u in unit_types_tmp:
                unit_type = dict(u)

                unit_types.append(unit_type)

        return unit_types
