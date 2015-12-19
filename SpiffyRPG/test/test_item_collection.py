# -*- coding: utf-8 -*-
import unittest
from SpiffyWorld.collections import ItemCollection
from SpiffyWorld import Item
import logging

log = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)

class TestItemCollection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def _get_item(self, **kwargs):
        item_name = kwargs["item_name"]
        item_id = 1
        item_type = kwargs["item_type"]
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
        item_name = "Test Item"
        item_type = "rock"
        item = self._get_item(item_name=item_name, item_type=item_type)
        
        collection = ItemCollection()
        collection.add(item)

        expected = item
        actual = collection.get_item_by_item_name(item_name)

        self.assertEqual(len(collection.items), 1)
        self.assertEqual(expected, actual)

        # Test that we can't add duplicate items
        collection.add(item)
        self.assertEqual(len(collection.items), 1)

    def test_get_item_by_item_name(self):
        item_name = "QA Engineer's Razor-sharp Shears"
        item_type = "scissors"
        item = self._get_item(item_name=item_name, item_type=item_type)
        
        collection = ItemCollection()
        collection.add(item)

        expected = item

        # Typical use case
        actual = collection.get_item_by_item_name(item_name)

        self.assertEqual(len(collection.items), 1)
        self.assertEqual(expected, actual)

        # Test that we don't get the wrong thing
        expected = None
        actual = collection.get_item_by_item_name("hello world")
        self.assertEqual(expected, actual)

    def test_get_base_items(self):
        base_item_name = "QA Engineer's Boulder"
        base_item_type = "rock"
        base_item = self._get_item(item_name=base_item_name, 
                                   item_type=base_item_type,
                                   is_permanent=True)
        
        collection = ItemCollection()
        collection.add(base_item)

        # Typical use case
        actual = collection.get_base_items()

        self.assertEqual(len(actual), 1)

        # Add non-base item
        item_name = "cat treat"
        item_type = "paper"
        item = self._get_item(item_name=item_name, item_type=item_type)

        collection.add(item)

        actual = collection.get_base_items()

        # Make sure the item was added
        self.assertEqual(len(collection.items), 2)

        # Make sure the result is still correct
        self.assertEqual(len(actual), 1)
        



