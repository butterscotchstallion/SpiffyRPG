#!/usr/bin/env python
# -*- coding: utf-8 -*-
from SpiffyWorld import Item


class ItemBuilder:

    """
    Builds an Item given a list of item models
    and ItemCollection to look up items and such
    """

    def build_items(self, **kwargs):
        item_effects_map = kwargs["item_effects_map"]
        item_models = kwargs["item_models"]
        effect_collection = kwargs["effect_collection"]
        items = []

        for item_model in item_models:
            item_effects = []

            item_id = item_model["id"]

            if item_id in item_effects_map:
                item_effects = item_effects_map[item_id]

            item_model["effects"] = effect_collection.get_effects_by_effect_id_list(item_effects)

            item = self.build_item(item_model=item_model)

            items.append(item)

        return items

    def build_item(self, **kwargs):
        item_model = kwargs["item_model"]

        return Item(item=item_model)
