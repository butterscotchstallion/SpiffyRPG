#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time


class Item:

    """
    Item model - db interactions
    """

    def __init__(self, **kwargs):
        self.db = kwargs["db"]

    def add_unit_item(self, **kwargs):
        item_id = kwargs["item_id"]
        unit_id = kwargs["unit_id"]
        cursor = self.db.cursor()
        params = (unit_id, item_id, time.time())
        cursor.execute("""INSERT INTO spiffyrpg_unit_items(
                          unit_id,
                          item_id,
                          created_at)
                          VALUES(?, ?, ?)""", params)
        self.db.commit()
        cursor.close()

    def get_items(self, **kwargs):
        cursor = self.db.cursor()

        cursor.execute("""SELECT
                          i.id,
                          i.name,
                          i.description,
                          i.min_level,
                          i.max_level,
                          i.item_type,
                          i.rarity,
                          i.equipment_slot,
                          i.is_permanent,
                          i.unit_type_id,
                          i.can_use,
                          i.charges,
                          i.created_at
                          FROM spiffyrpg_items i""")

        all_items = cursor.fetchall()
        items = []

        cursor.close()

        if len(all_items) > 0:
            for i in all_items:
                item = dict(i)
                item["effects"] = []

                items.append(item)

        return items
