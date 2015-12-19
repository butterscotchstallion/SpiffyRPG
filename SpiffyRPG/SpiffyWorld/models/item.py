# -*- coding: utf-8 -*-
import logging as log

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

    def get_item_effects(self, **kwargs):
        """
        Fetches item effects
        """
        cursor = self.db.cursor()
        
        cursor.execute("""SELECT
                          e.id,
                          e.name,
                          e.description,
                          e.operator,
                          e.hp_adjustment,
                          e.incoming_damage_adjustment,
                          e.outgoing_damage_adjustment,
                          e.interval_seconds,
                          e.stacks,
                          e.created_at,
                          ie.item_id,
                          ie.effect_id,
                          ie.effect_on_possession,
                          ie.duration_in_seconds,
                          ie.created_at
                          FROM spiffyrpg_item_effects ie
                          JOIN spiffyrpg_effects e ON e.id = ie.effect_id""")

        effects = cursor.fetchall()
        
        cursor.close()

        lookup = {}

        if len(effects) > 0:
            for e in effects:
                d_effect = dict(e)
                item_id = d_effect["item_id"]

                if item_id not in lookup:
                    lookup[item_id] = []

                lookup[item_id].append(d_effect)

        return lookup

    def get_unit_items_lookup(self):
        """
        Fetches items for one or many units
        """
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
                          i.created_at,
                          i.charges,
                          i.can_use,
                          ui.item_id,
                          ui.unit_id
                          FROM spiffyrpg_unit_items ui
                          JOIN spiffyrpg_items i ON ui.item_id = i.id""")

        items = cursor.fetchall()
        
        cursor.close()

        lookup = {}

        if len(items) > 0:
            for i in items:
                d_item = dict(i)
                item_id = d_item["item_id"]
                unit_id = d_item["unit_id"]

                if unit_id not in lookup:
                    lookup[unit_id] = []

                effects = []

                if item_id in self.item_effects:
                    effects = self.item_effects[item_id]

                d_item["effects"] = effects

                lookup[unit_id].append(d_item)

        return lookup
