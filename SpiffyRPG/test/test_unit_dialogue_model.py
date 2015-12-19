# -*- coding: utf-8 -*-
import unittest
from SpiffyWorld.models import UnitDialogue

class TestUnitDialogueModel(unittest.TestCase):
    def test_get_unit_dialogue_map(self):
        """
        This method should return a dictionary with
        the unit_id as the key, and the a list of dialogue_ids
        as the value
        """
        unit_dialogue = [{"unit_id": 1, "dialogue_id": 1},
                        {"unit_id": 2, "dialogue_id": 1},
                        {"unit_id": 1, "dialogue_id": 99},
                        {"unit_id": 2, "dialogue_id": 101}]
        
        expected = {1: [1, 99], 2: [1, 101]}
        unit_dialogue_model = UnitDialogue(db="test")
        actual = unit_dialogue_model._get_unit_dialogue_map(unit_dialogue)

        self.assertEqual(expected, actual)
