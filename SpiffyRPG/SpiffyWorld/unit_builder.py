#!/usr/bin/env python
# -*- coding: utf-8 -*-
from SpiffyWorld import Unit


class UnitBuilder:

    """
    Builds a Unit given a list of unit models
    and ItemCollection to look up items and such
    """

    def build_units(self, **kwargs):
        unit_models = kwargs["unit_models"]
        log = kwargs["log"]
        item_collection = kwargs["item_collection"]
        effect_collection = kwargs["effect_collection"]
        dialogue_collection = kwargs["dialogue_collection"]

        unit_items_map = kwargs["unit_items_map"]
        unit_effects_map = kwargs["unit_effects_map"]
        unit_dialogue_map = kwargs["unit_dialogue_map"]
        units = []

        """
        Prepare unit models by populating using
        maps
        """
        for unit_model in unit_models:
            unit_id = unit_model["id"]
            items = []
            effects = []
            dialogue = []

            """
            Add unit items from map
            """
            if unit_id in unit_items_map:
                unit_item_ids = unit_items_map[unit_id]
                unit_items = item_collection.get_items_by_item_id_list(
                    unit_item_ids)

                if unit_items:
                    for item in unit_items:
                        items.append(item)

            unit_model["items"] = items

            """
            Add effects from map
            """
            if unit_id in unit_effects_map:
                unit_effect_ids = unit_effects_map[unit_id]
                unit_effects = effect_collection.get_effects_by_effect_id_list(
                    unit_effect_ids)

                if unit_effects:
                    for effect in unit_effects:
                        effects.append(effect)

            unit_model["effects"] = effects

            """
            Add dialogue from map
            """
            if unit_id in unit_dialogue_map:
                unit_dialogue_ids = unit_dialogue_map[unit_id]
                unit_dialogue = dialogue_collection.get_dialogue_by_dialogue_id_list(
                    unit_dialogue_ids)

                if unit_dialogue:
                    for d in unit_dialogue:
                        dialogue.append(d)

            unit_model["dialogue"] = dialogue

            unit = Unit(unit=unit_model, log=log)

            units.append(unit)

        return units
