#!/usr/bin/env python
# -*- coding: utf-8 -*-


class UnitEffects:

    """
    Unit effects model
    """

    def __init__(self, **kwargs):
        self.db = kwargs["db"]
        self.effects = {}

    def _get_unit_effects_map(self, effects):
        unit_effects_map = {}

        for unit_effect in effects:
            unit_id = unit_effect["unit_id"]

            if unit_id not in unit_effects_map:
                unit_effects_map[unit_id] = []

            unit_effects_map[unit_id].append(unit_effect["effect_id"])

        return unit_effects_map

    def get_unit_effects(self):
        """
        Get unit effect IDs. Those will be queried
        against the effect collection to get the rest
        of the effect information
        """
        cursor = self.db.cursor()

        cursor.execute("""SELECT
                          e.id AS effect_id,
                          ue.unit_id
                          FROM spiffyrpg_effects e
                          JOIN spiffyrpg_unit_effects ue ON ue.effect_id = e.id
                          JOIN spiffyrpg_units u ON u.id = ue.unit_id""")

        tmp_effects = cursor.fetchall()
        cursor.close()
        effects = []

        if tmp_effects:
            for e in tmp_effects:
                effect = dict(e)
                effects.append(effect)

        return effects
