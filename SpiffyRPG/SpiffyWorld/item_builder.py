# -*- coding: utf-8 -*-
from SpiffyWorld import Item

class ItemBuilder:

    """
    Builds an Item given a list of item models
    and ItemCollection to look up items and such
    """
    def build_items(self, **kwargs):
        item_collection = kwargs["item_collection"]
        effect_collection = kwargs["effect_collection"]
        item_effects_map = kwargs["item_effects_map"]
        item_models = kwargs["item_models"]
        items = []

        for item_model in item_models:
            effects = []

            item_id = item_model["id"]

            if item_id in item_effects_map:
                effects = item_effects_map[item_id]

            item_model["effects"] = effects

            item = Item(item=item_model)

            items.append(item)

        return items