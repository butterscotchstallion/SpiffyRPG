#!/usr/bin/env python
# -*- coding: utf-8 -*-
from SpiffyWorld import Item


class ItemCollection:

    """
    Catalog of available items
    """

    def __init__(self, **kwargs):
        self.items = []

    def add(self, item):
        if not isinstance(item, Item):
            raise ValueError("item must be an instance of Item")

        if item not in self.items:
            self.items.append(item)

    def get_item_by_item_name(self, item_name):
        for item in self.items:
            if item.name.lower().startswith(item_name.lower()):
                return item

    def get_item_by_item_id(self, item_id):
        for item in self.items:
            if item.id == item_id:
                return item

    def get_base_items(self):
        return [item for item in self.items if item.is_permanent]

    def get_items_by_item_id_list(self, item_id_list):
        return [item for item in self.items if item.id in item_id_list]
