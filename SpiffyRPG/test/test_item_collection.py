#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from SpiffyWorld.collections import ItemCollection
from SpiffyWorld import Item
from uuid import uuid4
from random import choice


class TestItemCollection(unittest.TestCase):

    def _get_item(self, **kwargs):
        item_id = uuid4()
        item_name = "Item%s" % item_id
        item_types = ("rock", "paper", "scissors", "lizard", "spock")
        item_type = choice(item_types)
        is_permanent = 0

        if "is_permanent" in kwargs:
            is_permanent = kwargs["is_permanent"]

        item_model = {
            "id": item_id,
            "name": item_name,
            "description": "foo",
            "effects": [],
            "min_level": 1,
            "max_level": 0,
            "rarity": "dank",
            "equipment_slot": None,
            "is_permanent": is_permanent,
            "unit_type_id": 0,
            "can_use": 0,
            "charges": 0,
            "created_at": "1",
            "item_type": item_type
        }

        item = Item(item=item_model)

        return item

    def test_add_item(self):
        item = self._get_item()
        collection = ItemCollection()
        collection.add(item)

        expected = item
        actual = collection.get_item_by_item_name(item.name)

        self.assertEqual(len(collection.items), 1)
        self.assertEqual(expected, actual)

        # Test that we can't add duplicate items
        collection.add(item)
        self.assertEqual(len(collection.items), 1)

    def test_get_item_by_item_name(self):
        item = self._get_item()
        collection = ItemCollection()
        collection.add(item)

        expected = item

        # Typical use case
        actual = collection.get_item_by_item_name(item.name)

        self.assertEqual(len(collection.items), 1)
        self.assertEqual(expected, actual)

        # Test that we don't get the wrong thing
        expected = None
        actual = collection.get_item_by_item_name("hello world")
        self.assertEqual(expected, actual)

    def test_get_base_items(self):
        base_item = self._get_item(is_permanent=True)

        collection = ItemCollection()
        collection.add(base_item)

        # Typical use case
        actual = collection.get_base_items()

        self.assertEqual(len(actual), 1)

        # Add non-base item
        item = self._get_item()

        collection.add(item)

        actual = collection.get_base_items()

        # Make sure the item was added
        self.assertEqual(len(collection.items), 2)

        # Make sure the result is still correct
        self.assertEqual(len(actual), 1)
