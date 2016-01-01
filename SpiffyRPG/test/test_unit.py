#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from uuid import uuid4
from random import randrange, choice
from SpiffyWorld import Unit, UnitLevel, Item, UnitBuilder, \
    UnitGenerator, EffectGenerator
from SpiffyWorld.collections import ItemCollection
from SpiffyWorld.models import UnitItems
import logging
from testfixtures import LogCapture
EFFECT_UNDEAD_BONUS = 25


class TestUnit(unittest.TestCase):

    def _get_item(self, **kwargs):
        item_id = uuid4()
        item_name = "Item%s" % item_id
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

    def _get_unit_model(self, **kwargs):
        unit_level = UnitLevel()
        is_player = False
        level = randrange(1, 100)
        xp = unit_level.get_xp_for_level(level)
        unit_id = uuid4()
        unit_name = "Unit%s" % unit_id
        unit_types = (1, 2, 3)
        unit_type_id = choice(unit_types)

        if "is_player" in kwargs:
            is_player = kwargs["is_player"]

        user_id = 0

        if is_player:
            user_id = randrange(1, 999)

        unit_model = {
            "id": unit_id,
            "unit_name": unit_name,
            "items": [],
            "effects": [],
            "dialogue": [],
            "experience": xp,
            "level": level,
            "user_id": user_id,
            "is_boss": 0,
            "unit_type_id": unit_type_id,
            "unit_type_name": "quux",
            "combat_status": "hostile",
            "base_items": []
        }

        return unit_model

    def _make_unit(self):
        unit_generator = UnitGenerator()

        return unit_generator.generate()

    def _make_undead_effect(self):
        effect_name = "Undead"
        ud_bonus = EFFECT_UNDEAD_BONUS
        return self._make_effect(effect_name=effect_name,
                                 outgoing_damage_adjustment=ud_bonus)

    def _make_effect(self, **kwargs):
        hp_adjustment = 0
        incoming_damage = 0
        outgoing_damage = 0
        stacks = 1
        operator = "+"
        eg = EffectGenerator()
        effect_name = None

        if "effect_name" in kwargs:
            effect_name = kwargs["effect_name"]

        if "operator" in kwargs:
            operator = kwargs["operator"]

        if "hp_adjustment" in kwargs:
            hp_adjustment = kwargs["hp_adjustment"]

        if "stacks" in kwargs:
            stacks = kwargs["stacks"]

        if "incoming_damage_adjustment" in kwargs:
            incoming_damage = kwargs["incoming_damage_adjustment"]

        if "outgoing_damage_adjustment" in kwargs:
            outgoing_damage = kwargs["outgoing_damage_adjustment"]

        effect = eg.generate(operator=operator,
                             hp_adjustment=hp_adjustment,
                             effect_name=effect_name,
                             stacks=stacks,
                             incoming_damage_adjustment=incoming_damage,
                             outgoing_damage_adjustment=outgoing_damage)
        return effect

    def test_get_xp_remaining_until_next_level_percentage(self):
        unit_generator = UnitGenerator()
        unit = unit_generator.generate()

        unit_level = UnitLevel()

        level_42_xp = unit_level.get_xp_for_level(42)
        ten_percent_of_total_xp = level_42_xp * .10
        unit.experience = level_42_xp - ten_percent_of_total_xp
        total_xp = level_42_xp

        # Test 90%
        expected_percentage = 90
        actual_percentage = unit.get_xp_remaining_until_next_level_percentage(
            total_xp)

        self.assertEqual(expected_percentage, actual_percentage)

        # Test 50%
        expected_fifty_percentage = 50
        fifty_percent_of_total_xp = level_42_xp * .50
        unit.experience = level_42_xp - fifty_percent_of_total_xp
        a_fifty = unit.get_xp_remaining_until_next_level_percentage(total_xp)

        self.assertEqual(expected_fifty_percentage, a_fifty)

        # Test xp over max level
        expected_one_twenty_percent = 120
        max_level_xp = unit_level.get_xp_for_max_level()
        twenty_percent_of_max = max_level_xp * .20
        unit.experience = max_level_xp + twenty_percent_of_max
        a_120 = unit.get_xp_remaining_until_next_level_percentage(max_level_xp)

        self.assertEqual(expected_one_twenty_percent, a_120)

    def test_get_hp_percentage(self):
        unit_generator = UnitGenerator()
        unit = unit_generator.generate()

        """ Full hp """
        expected = 100
        actual = unit.get_hp_percentage()

        self.assertEqual(expected, actual)

        """
        Adjust HP and re-test
        """
        hp_adjustment = 10
        operator = "-"
        adjust_hp_effect = self._make_effect(
            operator=operator, hp_adjustment=hp_adjustment)

        self.assertEqual(adjust_hp_effect.hp_adjustment, hp_adjustment)
        self.assertEqual(adjust_hp_effect.operator, operator)

        # Apply effect
        unit.apply_effect(adjust_hp_effect)

        expected_adjusted = 90
        actual_adjusted = unit.get_hp_percentage()

        self.assertEqual(expected_adjusted, actual_adjusted)

        """
        Reset HP and try another percentage
        """
        unit.hp = unit.calculate_hp()
        big_hp = 50
        operator = "-"
        big_adjust_hp_effect = self._make_effect(operator=operator,
                                                 hp_adjustment=big_hp)
        unit.apply_effect(big_adjust_hp_effect)

        expected_big_adjusted = 50
        actual_big_adjusted = unit.get_hp_percentage()

        self.assertEqual(expected_big_adjusted, actual_big_adjusted)

        """
        Reset HP to full
        """
        unit.hp = unit.calculate_hp()

        expected_full = 100
        actual_full = unit.get_hp_percentage()

        self.assertEqual(expected_full, actual_full)

    def test_create_player(self):
        unit_generator = UnitGenerator()
        unit = unit_generator.generate(is_player=True)

        self.assertEqual(unit.is_player, True)
        self.assertEqual(unit.is_npc, False)

    def test_create_npc(self):
        unit_generator = UnitGenerator()
        unit = unit_generator.generate()

        self.assertEqual(unit.is_player, False)
        self.assertEqual(unit.is_npc, True)

    def get_combatants(self):
        """
        Create units, with an item of each type
        """
        item_collection = ItemCollection()
        unit_models = []
        unit_items_list = []
        expected_units = []

        item_types = ("rock", "paper", "scissors", "lizard", "spock")
        for item_type in item_types:
            item = self._get_item(item_type=item_type)
            item_collection.add(item)

        for j in range(0, 2):
            unit_model = self._get_unit_model()
            unit_id = unit_model["id"]

            for c_item in item_collection.items:
                unit_items_list.append({"item_id": c_item.id,
                                        "unit_id": unit_id})
                unit_model["items"].append(c_item)

            with LogCapture():
                logger = logging.getLogger()
                unit = Unit(unit=unit_model, log=logger)

            expected_units.append(unit)
            unit_models.append(unit_model)

        """
        Although we added more items, the collection should
        never add duplicates
        """
        total_items = len(item_types)
        self.assertEqual(len(item_collection.items), total_items)

        """
        There two units with five items each, so unit_items_map
        should have ten items total
        """
        unit_items_list_length = len(unit_items_list)
        self.assertEqual(unit_items_list_length, 10)

        builder = UnitBuilder()
        unit_items_model = UnitItems(db="quux")
        unit_items_map = unit_items_model._get_unit_items_map(unit_items_list)

        with LogCapture():
            logger = logging.getLogger()
            actual_units = builder.build_units(unit_models=unit_models,
                                               unit_items_map=unit_items_map,
                                               item_collection=item_collection,
                                               effect_collection="quux",
                                               dialogue_collection="quux",
                                               unit_effects_map={},
                                               unit_dialogue_map={},
                                               log=logger)

        self.assertEqual(len(expected_units), len(actual_units))

        """
        Ensure that each unit has the expected item set
        """
        unit_items = [uitem for uitem in item_collection.items]

        for unit in actual_units:
            # Ensure that each of the new units have full HP
            self.assertEqual(unit.get_hp(), unit.calculate_hp())
            self.assertEqual(unit.items, unit_items)

        return actual_units

    def test_unit_attacks(self):
        unit_1, unit_2 = self.get_combatants()

        """
        Equip a specific item type for each so we
        can accurately predict the outcome for
        testing purposes
        """
        unit_1.equip_rock_weapon()
        unit_1_weapon = unit_1.get_equipped_weapon()

        self.assertTrue(unit_1_weapon.is_rock())

        unit_2.equip_scissors_weapon()
        unit_2_weapon = unit_2.get_equipped_weapon()

        self.assertTrue(unit_2_weapon.is_scissors())

        """
        Test hit info. Hit info is returned from attack()
        (the result of an attack)
        """
        unit_2_hp_before_attack = unit_2.get_hp()

        hit_info = unit_1.attack(target=unit_2)

        self.assertEqual(hit_info["hit_word"], "crushes")
        self.assertTrue(hit_info["is_hit"])
        self.assertFalse(hit_info["is_draw"])
        self.assertTrue(hit_info["damage"] > 0)

        """
        Make sure this unit is attacking with an item that
        they have
        """
        self.assertIn(hit_info["attacker_weapon"], unit_1.items)

        self.assertTrue(
            hit_info["damage"] >= unit_1.get_min_base_attack_damage())

        # Upper bound is multiplied by two because of critical strikes
        damage_upper_bound = unit_1.get_max_base_attack_damage() * 2

        self.assertTrue(hit_info["damage"] <= damage_upper_bound)

        """
        Since we equipped unit_1 with a rock and unit_2
        with scissors, we know that is_hit should be True
        """
        self.assertTrue(hit_info["is_hit"])
        self.assertEqual(
            hit_info["attacker_weapon"], unit_1.get_equipped_weapon())
        self.assertEqual(
            hit_info["target_weapon"], unit_2.get_equipped_weapon())
        self.assertEqual(hit_info["hit_word"], "crushes")

        unit_2_is_alive = unit_2.is_alive()
        unit_2_total_hp = unit_2.calculate_hp()

        if hit_info["damage"] >= unit_2_total_hp:
            self.assertFalse(unit_2_is_alive)
        else:
            self.assertTrue(unit_2_is_alive)

        """
        apply_damage will always prevent the unit's HP from
        going below zero
        """
        expected_hp = unit_2_hp_before_attack - hit_info["damage"]

        if expected_hp < 0:
            expected_hp = 0

        actual_hp = unit_2.get_hp()

        self.assertEqual(expected_hp, actual_hp)

    def test_undead_attack(self):
        unit_1, unit_2 = self.get_combatants()

        """
        Equip a specific item type for each so we
        can accurately predict the outcome for
        testing purposes
        """
        unit_1.equip_rock_weapon()
        unit_1_weapon = unit_1.get_equipped_weapon()

        self.assertTrue(unit_1_weapon.is_rock())

        unit_2.equip_scissors_weapon()
        unit_2_weapon = unit_2.get_equipped_weapon()

        self.assertTrue(unit_2_weapon.is_scissors())

        # Test undead damage bonus
        undead_effect = self._make_undead_effect()

        """
        1. Add undead effect to unit
        2. Get a new attack
        3. Make sure the damage bonus has been applied
        """
        unit_1.apply_effect(undead_effect)

        self.assertTrue(unit_1.is_undead())

        undead_attack = unit_1.attack(target=unit_2)

        undead_bonus_dec = float(EFFECT_UNDEAD_BONUS) / float(100)

        damage_lower_bound = unit_1.get_min_base_attack_damage()

        # Upper bound is multiplied by two because of critical strikes
        damage_upper_bound = unit_1.get_max_base_attack_damage() * 2

        bonus_dec_lower = damage_lower_bound * undead_bonus_dec
        bonus_dec_upper = damage_upper_bound * undead_bonus_dec
        undead_damage_lower_bound = damage_lower_bound + bonus_dec_lower
        undead_damage_upper_bound = damage_upper_bound + bonus_dec_upper

        self.assertTrue(undead_attack["damage"] >= undead_damage_lower_bound)
        self.assertTrue(undead_attack["damage"] <= undead_damage_upper_bound)

    def test_hit_applies_damage(self):
        unit_1, unit_2 = self.get_combatants()

        # Lizard should poison spock
        unit_1.equip_spock_weapon()
        unit_2.equip_lizard_weapon()

        unit_2_hp_before_attack = unit_2.get_hp()
        hit_info = unit_1.attack(target=unit_2)

        # unit_1 strikes because Lizard poisons Spock
        self.assertFalse(hit_info["is_hit"])

        expected_unit_2_hp = unit_2_hp_before_attack - hit_info["damage"]
        actual_unit_2_hp = unit_2.get_hp()

        self.assertEqual(expected_unit_2_hp, actual_unit_2_hp)

    def test_attack_is_draw(self):
        unit_1, unit_2 = self.get_combatants()

        unit_1.equip_lizard_weapon()
        unit_2.equip_lizard_weapon()

        hit_info = unit_1.attack(target=unit_2)

        """
        Make sure both units have not taken damage
        in the event of a draw
        """
        self.assertTrue(unit_1.has_full_hp())
        self.assertTrue(unit_2.has_full_hp())
        self.assertFalse(hit_info["is_hit"])
        self.assertTrue(hit_info["is_draw"])
        self.assertEqual(hit_info["damage"], 0)

if __name__ == '__main__':
    unittest.main()
