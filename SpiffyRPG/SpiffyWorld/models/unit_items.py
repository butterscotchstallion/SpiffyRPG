#!/usr/bin/env python
# -*- coding: utf-8 -*-

class UnitItems:
    """
    Unit items model
    """
    def __init__(self, **kwargs):
        self.db = kwargs["db"]

    def _get_unit_items_map(self, items):
        unit_items_map = {}

        for unit_item in items:
            unit_id = unit_item["unit_id"]

            if unit_id not in unit_items_map:
                unit_items_map[unit_id] = []

            unit_items_map[unit_id].append(unit_item["item_id"])

        return unit_items_map

    def get_unit_items(self):
        """
        Fetches items for one or many units
        """
        cursor = self.db.cursor()
        
        cursor.execute("""SELECT
                          ui.item_id,
                          ui.unit_id
                          FROM spiffyrpg_unit_items ui
                          JOIN spiffyrpg_items i ON ui.item_id = i.id""")

        tmp_items = cursor.fetchall()
        cursor.close()
        items = []

        if tmp_items:
            for i in tmp_items:
                item = dict(i)
                items.append(item)

        return self._get_unit_items_map(items)