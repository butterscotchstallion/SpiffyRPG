#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from SpiffyWorld import UnitDialogue
from uuid import uuid4


class TestUnitDialogue(unittest.TestCase):

    def _make_dialogue(self):
        dialogue_id = uuid4()
        dialogue_context = "sup"
        dialogue_text = "hello world"

        dialogue_model = {
            "id": dialogue_id,
            "context": dialogue_context,
            "dialogue": dialogue_text,
            "unit_id": uuid4()
        }

        dialogue = UnitDialogue(dialogue=dialogue_model)

        return dialogue

    def test_create_dialogue(self):
        dialogue = self._make_dialogue()

        self.assertIsInstance(dialogue, UnitDialogue)
        self.assertIsNotNone(dialogue.id)
        self.assertIsNotNone(dialogue.context)
        self.assertIsNotNone(dialogue.unit_id)

if __name__ == '__main__':
    unittest.main()
