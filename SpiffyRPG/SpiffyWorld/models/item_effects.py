#!/usr/bin/env python
# -*- coding: utf-8 -*-

class ItemEffects:
    """
    Item effects model
    """
    def __init__(self, **kwargs):
        self.db = kwargs["db"]

    def _get_item_effects_map(self, effects):
        item_effects_map = {}

        for item_effect in effects:
            item_id = item_effect["item_id"]

            if item_id not in item_effects_map:
                item_effects_map[item_id] = []

            item_effects_map[item_id].append(item_effect["effect_id"])

        return item_effects_map

    def get_item_effects(self):
        """
        Fetches effects for one or many items
        """
        cursor = self.db.cursor()
        
        cursor.execute("""SELECT
                          ie.item_id,
                          ie.effect_id
                          FROM spiffyrpg_item_effects ie
                          JOIN spiffyrpg_items i ON ie.item_id = i.id""")

        tmp_items = cursor.fetchall()
        cursor.close()
        items = []

        if tmp_items:
            for i in tmp_items:
                item = dict(i)
                items.append(item)

        return self._get_item_effects_map(items)