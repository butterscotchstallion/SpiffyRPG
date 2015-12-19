# -*- coding: utf-8 -*-
import unittest
from SpiffyWorld.models import UnitEffects

class TestUnitEffectsModel(unittest.TestCase):
    def test_get_unit_effects_map(self):
        """
        This method should return a dictionary with
        the unit_id as the key, and the a list of effect_ids
        as the value
        """
        unit_effects = [{"unit_id": 1, "effect_id": 1},
                        {"unit_id": 2, "effect_id": 1},
                        {"unit_id": 1, "effect_id": 99},
                        {"unit_id": 2, "effect_id": 101}]
        
        expected = {1: [1, 99], 2: [1, 101]}
        unit_effects_model = UnitEffects(db="test")
        actual = unit_effects_model._get_unit_effects_map(unit_effects)

        self.assertEqual(expected, actual)
