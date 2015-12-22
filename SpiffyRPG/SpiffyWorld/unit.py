#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import re
import time
from datetime import datetime
import logging
from .unit_level import UnitLevel

log = logging.getLogger("SpiffyRPG.Unit")
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)

class Unit:
    """
    Basis for units in a dungeon
    """
    UNIT_TYPE_ZEN_MASTER = 1
    UNIT_TYPE_HACKER = 2
    UNIT_TYPE_TROLL = 3

    def __init__(self, **kwargs):
        """
        Start by initializing the unit as if it is an NPC,
        since for the most part, a player is identical to a NPC.
        """
        self.lower_damage_coefficient = 5
        self.upper_damage_coefficient = 10
        self.critical_strike_chance = 5
        self.slain_units = []
        self.winning_streak = []
        self.raised_units = []
        self.battles = []
        self.units_that_have_struck_me = []

        """
        Build unit from db info
        """
        unit = kwargs["unit"]

        self.id = unit["id"]
        self.is_boss = unit["is_boss"] == 1 or unit["is_boss"]
        self.user_id = unit["user_id"]
        self.created_at = time.time()
        self.slain_at = None
        self.unit_type_name = unit["unit_type_name"]
        self.unit_type_id = unit["unit_type_id"]
        self.effects = unit["effects"]
        self.items = unit["items"]
        self.lootable_items = [item for item in self.items if item.is_permanent]
        self.base_items = [item for item in self.items if item.is_permanent]
        self.dialogue = unit["dialogue"]
        self.experience = unit["experience"]

        unit_level = UnitLevel()

        self.level = unit_level.get_level_by_xp(self.experience)
        self.combat_status = unit["combat_status"]
        self.is_casting_spell = False
        self.spell_interrupted_callback = None

        """ When unit is an NPC then use the unit name """
        self.name = unit["unit_name"]
        self.nick = self.name
        self.title = self.unit_type_name

        """
        If the unit has a non-zero user_id, then they are a player.
        When the unit is a NPC then their level depends
        on the dungeon min/max.
        """
        self.is_player = self.user_id > 0
        self.is_npc = self.user_id <= 0

        if self.is_player:
            #user_id_lookup = kwargs["user_lookup"]["look_up_user_ids"]

            #if self.user_id in user_id_lookup:
            if "nick" in kwargs:
                #self.nick = user_id_lookup[self.user_id]
                self.nick = kwargs["nick"]

                """
                self.announcer = PlayerAnnouncer(irc=collections["irc"],
                                                 destination=self.nick)
                """

        """
        Each unit should get some base items for their level.
        """
        self.populate_inventory_with_base_items()

        """
        The above line ensures that the unit always has at least the
        base weapons.
        """
        self.equip_random_weapon()

        """
        HP is a function of the unit's level, so
        the level must be determined prior.
        """
        self.hp = self.calculate_hp()

        """
        Apply unit effects
        """
        self.apply_unit_effects()

        """
        Some items have an effect on possession!
        """
        self.apply_item_effects()

    def __str__(self):
        return self.name

    def __eq__(self, other):
        """
        Compares this unit against another one, checking
        unit id and inventory contents
        """
        id_match = self.id == other.id

        if not id_match:
            return False

        #if not self.name == other.name:
        #    return False

        """
        Test inventory contents
        """
        item_length_match = len(self.items) == len(other.items)

        if not item_length_match:
            return False

        self_item_ids = [item.id for item in self.items]
        other_item_ids = [item.id for item in other.items]
        items_match = self_item_ids == other_item_ids

        if not items_match:
            return False

        """
        Test effects
        """
        effect_length_match = len(self.effects) == len(other.effects)

        if not effect_length_match:
            return False

        self_effect_ids = [effect.id for effect in self.effects]
        other_effect_ids = [effect.id for effect in other.effects]
        effects_match = self_effect_ids == other_effect_ids

        if not effects_match:
            return False


    def apply_unit_effects(self):
        for effect in self.effects:
            self.apply_effect(effect)

    def add_charge_to_random_potion(self):
        potion = self.get_random_potion_without_charges()

        if potion is not None:
            self.add_charge_to_item(item=potion)

    def get_random_potion_without_charges(self):
        potions = []

        for item in self.items:
            is_potion = item.is_potion()
            has_charges = item.charges > 0

            if item.is_usable() and is_potion and not has_charges:
                potions.append(item)

        if len(potions) > 0:
            return random.choice(potions)

    def add_charge_to_item(self, **kwargs):
        item = kwargs["item"]

        if item.is_usable():
            item.charges += 1

            log.info("SpiffyRPG: added charge to %s" % item.name)
        else:
            log.error("SpiffyRPG: cannot add charges to %s because it is not usable" % item.name)

    def use_item(self, **kwargs):
        item = kwargs["item"]

        if item in self.items:
            if not item.can_use or item.charges == 0:
                return

            """
            Decrement charges each time an item is used
            """
            item.charges -= 1

            if len(item.effects) > 0:
                """
                Apply item effects
                """
                for effect in item.effects:
                    self.apply_effect(effect)

                return True
            else:
                log.info("SpiffyRPG: attempting to use item %s but it has no effects!" % item.name)
        else:
            log.error("SpiffyRPG: attempting to use %s but it is not in %s's bags" %
                      (item.name, self.name))

    def begin_casting_raise_dead(self):
        self.begin_casting_spell()

    def begin_casting_spell(self):
        self.combat_status = "hostile"
        self.is_casting_spell = True

    def set_spell_interrupted_callback(self, callback):
        self.spell_interrupted_callback = callback

    def on_unit_spell_interrupted(self, **kwargs):
        attacker = kwargs["attacker"]

        self.is_casting_spell = False

        """
        This callback typically announces the spell interruption
        """
        if self.spell_interrupted_callback is not None:
            self.spell_interrupted_callback(unit=self,
                                            attacker=attacker)

    def raise_dead(self, **kwargs):
        """
        Raise dead is a spell, so begin_casting_raise_dead is
        called before this to symbolize a spell being cast.
        If apply_damage is called before this method, then
        the spell is "interrupted". Returns True if the spell
        was cast successfully.
        """
        dead_unit = kwargs["unit"]

        if self.is_casting_spell:
            log.info("SpiffyRPG: %s raises %s from the dead!" %
                     (self.name, dead_unit.get_name()))

            """ Reset HP """
            dead_unit.hp = dead_unit.calculate_hp()

            """ Apply Undead effect """
            undead_effect = self.effects_collection.get_effect_by_name(name="Undead")
            dead_unit.apply_effect(undead_effect)

            """ Make this unit hostile """
            dead_unit.combat_status = "hostile"

            self.is_casting_spell = False

            return True

    def has_item(self, **kwargs):
        loot_item = kwargs["item"]
        item_ids = [item.id for item in self.items]

        return loot_item.id in item_ids

    def add_inventory_item(self, **kwargs):
        item = kwargs["item"]

        if not self.has_item(item=item):
            """
            Add to inventory
            """
            self.items.append(item)

            """
            Apply any effects this item may have
            """
            self.apply_item_effects()

            """
            Persist item to database
            """
            self.item_collection.add_unit_item(item_id=item.id,
                                               unit_id=self.id)

    def apply_item_effects(self):
        for item in self.items:
            if len(item.effects) > 0:
                for effect in item.effects:
                    if effect.effect_on_possession == "1":
                        params = (effect.name, self.name, item.name)
                        log.info("SpiffyRPG: applying %s to %s due to item effect on %s" % params)

                        self.apply_effect(effect)

    def make_hostile(self):
        self.combat_status = "hostile"

    def get_random_lootable_item(self, **kwargs):
        """
        Find a random lootable item, and something the
        other unit does not already have.
        """
        already_has_items = kwargs["already_has"]
        already_has_item_ids = [item.id for item in already_has_items]
        lootable = [item for item in self.lootable_items
                    if item.id not in already_has_item_ids]

        if len(lootable):
            return random.choice(lootable)

    def add_struck_unit(self, unit):
        if unit not in self.units_that_have_struck_me:
            self.units_that_have_struck_me.append(unit)

    def reset_struck_units(self):
        self.units_that_have_struck_me = []

    def get_slain_units(self):
        return self.slain_units

    def add_slain_unit(self, unit):
        self.slain_units.append(unit)

    def get_effects_list(self):
        """
        Retrieves a list of effects on this unit
        """
        effect_names = []

        for effect in self.effects:
            effect_names.append(effect.name)

        return ", ".join(effect_names)

    def add_raised_unit(self, **kwargs):
        unit = kwargs["unit"]

        if unit not in self.raised_units:
            self.raised_units.append(unit)

    def add_winning_streak_unit(self, **kwargs):
        unit = kwargs["unit"]

        self.winning_streak.append(unit)

        streak_count = self.is_on_hot_streak()

        return streak_count

    def is_on_hot_streak(self):
        """
        Determines if unit is on a hot streak. A streak is
        at least three consecutive victories. Returns the
        streak count, if any.
        """
        streak_count = len(self.winning_streak)

        if streak_count >= 3:
            if streak_count == 3:
                log.info("SpiffyRPG: %s is on a streak of 3!" % self.name)
            elif streak_count == 4:
                log.info("SpiffyRPG: %s is on a streak of 4!" % self.name)

            return streak_count

    def reset_winning_streak(self):
        self.winning_streak = []

    def is_hostile(self):
        return self.combat_status == "hostile"

    def is_friendly(self):
        return self.combat_status == "friendly"

    def is_unit_same_stage(self, **kwargs):
        unit = kwargs["unit"]

        this_unit_stage = self.get_stage_by_level(level=self.level)
        target_unit_stage = self.get_stage_by_level(level=unit.level)

        return target_unit_stage == this_unit_stage

    def can_battle_unit(self, **kwargs):
        """
        Returns True if can battle, or a reason (string) if not
        """
        unit = kwargs["unit"]
        can_battle = False
        reason = "That target "

        """ Check if unit exists """
        if unit is None:
            reason += "does not appear to exist"
            return reason

        """ Check if we're trying to hit ourselves """
        if self.id == unit.id:
            reason = "is not as clever as they would have you believe"
            return reason

        """ Check if this unit is hostile """
        if not unit.is_hostile():
            reason += " is not hostile (%s)" % unit.combat_status
            return reason

        """
        Check if we're currently in battle with something other than
        this unit
        """
        self_battles = self.get_incomplete_battles()
        battles_with_others = [battle for battle in self_battles
                               if battle["combatant"].id != unit.id]

        if len(battles_with_others) > 0:
            battle_with_other = battles_with_others[0]
            combatant = battle_with_other["combatant"]
            current_round = len(battle_with_other["rounds"]) + 1
            total_rounds = battle_with_other["total_rounds"]
            params = (combatant.name, current_round, total_rounds)
            reason = "You're currently currently battling %s (round %s/%s)" % params
            return reason

        """ Check if the unit is in battle """
        target_battles = unit.get_incomplete_battles()
        target_battles_with_others = [battle for battle in target_battles
                                      if battle["combatant"].id != self.id]

        if len(target_battles_with_others) > 0:
            battle_with_other = target_battles_with_others[0]
            combatant = battle_with_other["combatant"]
            current_round = len(battle_with_other["rounds"])
            total_rounds = battle_with_other["total_rounds"]
            params = (combatant.name, current_round, total_rounds)
            reason += "is currently battling %s (round %s/%s)" % params
            return reason

        """ Check stage match """
        combatants_are_same_stage = self.is_unit_same_stage(unit=unit)
        this_unit_stage = self.get_stage_by_level(level=self.level)
        target_unit_stage = self.get_stage_by_level(level=unit.level)

        if target_unit_stage > this_unit_stage:
            reason += "is too powerful! Use .look to find monsters your level"
            return reason

        if target_unit_stage < this_unit_stage:
            reason = "is too weak. Use .look to find monsters your level"
            return reason

        """ It's all gravy """
        return True

    def regenerate_hp(self, regen_hp):
        current_hp = self.get_hp()
        max_hp = self.calculate_hp()

        if self.is_below_max_hp():
            self.hp += regen_hp

            #self.announcer.player_regenerates(regen_hp=regen_hp)

            log.info("SpiffyRPG: unit %s gains %sHP from Regneration" % (self.name, regen_hp))
        else:
            """
            If regeneration has brought this unit back to life,
            reset created_at
            """
            self.created_at = time.time()

            log.info("SpiffyRPG: unit %s is not rengerating because max HP (%s/%s)" % (self.name, current_hp, max_hp))

    def is_below_max_hp(self):
        current_hp = self.get_hp()
        max_hp = self.calculate_hp()

        return current_hp < max_hp

    def add_victory_hp_bonus(self, **kwargs):
        current_hp = self.get_hp()
        max_hp = self.calculate_hp()
        hp_bonus = 0

        if self.is_below_max_hp():
            hp_bonus = int(max_hp * .10)
            self.hp += hp_bonus

            log.info("SpiffyRPG: unit %s gains %sHP for winning" % (self.name, hp_bonus))
        else:
            log.info("SpiffyRPG: unit %s is at max HP (%s/%s)" % (self.name, current_hp, max_hp))

        return hp_bonus

    def populate_inventory_with_base_items(self):
        """
        The base items contain all of the items available
        for this unit type
        """
        base_items = self.base_items

        for item in base_items:
            is_in_bags = item in self.items
            is_unit_type = item.unit_type_id == self.unit_type_id
            is_level_appropriate = item.min_level <= self.level

            if not is_in_bags and is_unit_type and is_level_appropriate:
                if self.is_player:
                    """
                    Players start with a rock
                    """
                    if self.is_stage_one() and item.is_scissors():
                        continue
                else:
                    if self.is_stage_one() and item.is_rock():
                        continue

                self.items.append(item)

    def get_stage_by_level(self, **kwargs):
        stage = 1
        stage_two_min_level = 3
        stage_three_min_level = 10

        level = kwargs["level"]

        if level >= stage_two_min_level:
            stage = 2

        if level >= stage_three_min_level:
            stage = 3

        return stage

    def is_stage_one(self):
        return self.get_stage_by_level(level=self.level) == 1

    def is_stage_two(self):
        return self.get_stage_by_level(level=self.level) == 2

    def is_stage_three(self):
        return self.get_stage_by_level(level=self.level) == 3

    def equip_item(self, **kwargs):
        self.equipped_weapon = kwargs["item"]

    def equip_random_inventory_item_by_type(self, **kwargs):
        item_name = kwargs["item_type_name"]
        inventory_item = self.get_item_from_inventory_by_type(item_type_name=item_name)

        if inventory_item is not None:
            self.equip_item(item=inventory_item)

            self.announcer.item_equip(player=self,
                                      item=inventory_item)
        else:
            self.announcer.item_equip_failed(player=self,
                                             item_name=item_name)

    def equip_item_by_name(self, **kwargs):
        item_name = kwargs["item_name"]
        inventory_item = self.get_item_from_inventory_by_name(item_name=item_name)

        if inventory_item is not None:
            self.equip_item(item=inventory_item)

            self.announcer.item_equip(player=self,
                                      item=inventory_item)
        else:
            self.announcer.item_equip_failed(player=self,
                                             item_name=item_name)

    def get_item_type_from_user_input(self, **kwargs):
        item_type = kwargs["item_type"].lower()

        if item_type == "rock" or item_type[0] == "r":
            item_type = "rock"

        if item_type == "paper" or item_type[0] == "p":
            item_type = "paper"

        if item_type == "scissors" or (item_type[0] == "s" and item_type != "spock"):
            item_type = "scissors"

        if item_type == "lizard" or item_type[0] == "l":
            item_type = "lizard"

        if item_type == "spock" or item_type[0] == "v":
            item_type = "spock"

        return item_type

    def equip_rock_weapon(self):
        self.equip_item_by_type(item_type="rock")

    def equip_paper_weapon(self):
        self.equip_item_by_type(item_type="paper")

    def equip_scissors_weapon(self):
        self.equip_item_by_type(item_type="scissors")

    def equip_lizard_weapon(self):
        self.equip_item_by_type(item_type="lizard")

    def equip_spock_weapon(self):
        self.equip_item_by_type(item_type="spock")

    def equip_item_by_type(self, **kwargs):
        item_type = self.get_item_type_from_user_input(item_type=kwargs["item_type"])
        inventory_item = self.get_item_from_inventory_by_type(item_type_name=item_type)
        equip_ok = False

        if inventory_item is not None:
            if self.equipped_weapon.item_type != inventory_item.item_type:
                self.equip_item(item=inventory_item)

            equip_ok = True
        else:
            self.announcer.item_equip_failed(player=self)
            equip_ok = False

        return equip_ok

    def get_equipped_weapon(self):
        """
        If the player only has one weapon, then they're
        always going to equip that.
        """
        return self.equipped_weapon

    def get_rock_weapon(self):
        return self.get_item_from_inventory_by_type(item_type_name="rock")

    def get_paper_weapon(self):
        return self.get_item_from_inventory_by_type(item_type_name="paper")

    def get_scissors_weapon(self):
        return self.get_item_from_inventory_by_type(item_type_name="scissors")

    def get_lizard_weapon(self):
        return self.get_item_from_inventory_by_type(item_type_name="lizard")

    def get_spock_weapon(self):
        return self.get_item_from_inventory_by_type(item_type_name="spock")

    def get_item_from_inventory_by_type(self, **kwargs):
        item_type_name = kwargs["item_type_name"]
        items = []
        inventory_item_to_equip = None

        """
        Find a random item of $type in inventory
        """
        for item in self.items:
            if item.item_type == item_type_name:
                items.append(item)

        if len(items) > 0:
            inventory_item_to_equip = random.choice(items)

        return inventory_item_to_equip

    def get_item_from_inventory_by_id(self, **kwargs):
        items = self.items

        if len(items) > 0:
            for item in items:
                if kwargs["item_id"] == item.id:
                    return item
        else:
            log.info("SpiffyRPG: trying to get items but inventory is empty!")

    def get_item_from_inventory_by_name(self, **kwargs):
        item_name = kwargs["item_name"].lower()
        items = self.items

        for item in items:
            if item_name in item.name.lower():
                return item

    def get_equippable_items(self):
        items = []
        stage = self.get_stage_by_level(level=self.level)
        unit_type = "NPC"

        if self.is_player:
            unit_type = "PC"

        log.info("SpiffyRPG: %s is a stage %s %s" % (self.name, stage, unit_type))

        for item in self.items:
            equippable = False

            if self.is_stage_three():
                equippable = True
            else:
                """
                Stage one players start with a rock
                Stage one NPCs start with scissors
                """
                if self.is_stage_one():
                    if self.is_player:
                        if item.is_rock():
                            equippable = True
                    else:
                        if item.is_scissors():
                            equippable = True

                elif self.is_stage_two() and item.item_type in ("paper", "scissors", "rock"):
                    equippable = True

            if equippable:
                items.append(item)

        return items

    def equip_random_weapon(self, **kwargs):
        """
        Before each fight, NPCs equip a random weapon. However,
        this behavior can be modified through effects!
        """
        all_types = ("rock", "paper", "scissors", "lizard", "spock")
        weapon_types = all_types

        """
        This is used to avoid draws
        """
        if "avoid_weapon_type" in kwargs:
            weapon_types = [wtype for wtype in all_types if wtype != kwargs["avoid_weapon_type"]]

        items = [item for item in self.items if item.item_type in weapon_types]

        if len(items) > 0:
            """
            By default we fetch a random item as usual.
            """
            random_item = random.choice(items)
            equipped_item = random_item
            pref_chance = 70
            chance_to_equip_preferred = random.randrange(1, 100) < pref_chance

            """
            If the unit has one of the preferential weapon effects,
            then choose one of those appropriately.
            """
            if self.is_archeologist():
                if chance_to_equip_preferred:
                    log.info("SpiffyRPG: Archeologist %s is equipping rock!" % self.name)
                    equipped_item = self.get_rock_weapon()
            elif self.is_paper_enthusiast():
                if chance_to_equip_preferred:
                    log.info("SpiffyRPG: Paper Enthusiast %s is equipping paper!" % self.name)
                    equipped_item = self.get_paper_weapon()
            elif self.is_running_with_scissors():
                if chance_to_equip_preferred:
                    log.info("SpiffyRPG: Running With Scissors %s is equipping scissors!" % self.name)
                    equipped_item = self.get_scissors_weapon()
            elif self.is_blue_tongue():
                if chance_to_equip_preferred:
                    log.info("SpiffyRPG: Blue Tongue %s is equipping lizard!" % self.name)
                    equipped_item = self.get_lizard_weapon()
            elif self.is_vulcan_embraced():
                if chance_to_equip_preferred:
                    log.info("SpiffyRPG: Vulcan's Embrace %s is equipping spock!" % self.name)
                    equipped_item = self.get_spock_weapon()

            self.equipped_weapon = equipped_item

    def set_title(self, title):
        self.name = title

    def get_dialogue_by_type(self, **kwargs):
        dialogue_type = kwargs["dialogue_type"]
        dialogues = []

        for dialogue in self.dialogue:
            if dialogue["context"] == dialogue_type:
                dialogues.append(dialogue)

        if len(dialogues) > 0:
            dialogue = random.choice(dialogues)

            return dialogue["dialogue"]

    def dialogue_intro(self):
        return self.get_dialogue_by_type(dialogue_type="intro")

    def dialogue_win(self):
        return self.get_dialogue_by_type(dialogue_type="win")

    def dialogue_sup(self):
        return self.get_dialogue_by_type(dialogue_type="sup")

    def dialogue_zombie(self):
        return self.dialogue_collection.get_dialogue_by_context(context="zombie")

    def get_title(self):
        return self.title

    def get_xp_required_for_next_level(self):
        return self.unit_level.get_xp_for_next_level(self.level)

    def get_xp_required_for_previous_level(self):
        return self.unit_level.get_xp_for_next_level(self.level-1)

    def get_level(self):
        return self.unit_level.get_level_by_xp(self.experience)

    def get_unit_title(self):
        return self.unit_type_name

    def on_unit_level(self, **kwargs):
        self.title = self.get_unit_title()
        self.hp = self.calculate_hp()
        self.populate_inventory_with_base_items()

    def add_experience(self, experience):
        gained_level = False
        if experience <= 0:
            return

        current_level = self.level

        self.experience += experience
        self.level = self.get_level()

        if self.level != current_level:
            gained_level = True
            self.on_unit_level()

        log.info("Player %s adding %s xp" % (self.name, experience))

        self.unit_model.add_experience(self.id, self.experience)

        return gained_level

    def calculate_hp(self):
        base_factor = 15

        if self.is_player:
            base_factor += 5

        base_hp = self.level * base_factor

        return base_hp

    def get_effects(self):
        """ TODO: Check duration here """
        return self.effects

    def get_hp(self):
        hp = self.hp

        return hp

    def get_xp_remaining_until_next_level_percentage(self, total):
        current_xp = self.experience
        total_xp_for_current_level = total

        remaining_xp = float(current_xp) / float(total_xp_for_current_level) * 100

        return remaining_xp

    def get_hp_percentage(self):
        total_hp = self.calculate_hp()
        current_hp = self.get_hp()

        percentage = float(current_hp) / float(total_hp) * 100

        return int(percentage)

    def get_name(self):
        unit_name = self.name

        if self.is_undead():
            unit_name = "Undead %s" % unit_name

        return unit_name

    def has_full_hp(self):
        hp = self.get_hp()
        total_hp = self.calculate_hp()

        return hp == total_hp

    def adjust_hp(self, effect):
        total_hp = self.calculate_hp()
        adjustment = float(total_hp * (float(effect.hp_adjustment) / float(100)))

        if effect.operator == "+":
            self.hp += adjustment

            log.info("SpiffyRPG: added %s HP from %s" % (adjustment, effect.name))
        elif effect.operator == "-":
            self.hp -= adjustment

            log.info("SpiffyRPG: subtracted %s HP from %s" % (adjustment, effect.name))
        elif effect.operator == "*":
            self.hp *= adjustment

            log.info("SpiffyRPG: multiplying %s HP from %s" % (adjustment, effect.name))

    def apply_effect(self, effect):
        """
        hp_adjustment is an instant effect that
        adjusts HP based on a percentage of the unit's
        total HP
        """
        if effect not in self.effects:
            self.effects.append(effect)

        if effect.hp_adjustment is not None:
            self.adjust_hp(effect)

        if effect.name == "Undead":
            self.on_effect_undead_applied()

    def on_effect_undead_applied(self):
        """
        Revive unit
        """
        total_hp = self.calculate_hp()
        self.hp = total_hp

        """
        Reset created_at so show that the unit has just been
        raised from the dead
        """
        self.created_at = time.time()

        params = (self.name, total_hp)
        log.info("SpiffyRPG: %s has been turned! setting HP to %s" % params)

    def get_min_base_attack_damage(self):
        return float(self.level * self.lower_damage_coefficient)

    def get_max_base_attack_damage(self):
        return float(self.level * self.upper_damage_coefficient)

    def get_attack_damage(self):
        return random.randrange(self.get_min_base_attack_damage(),
                                self.get_max_base_attack_damage())

    def is_counterpart(self, **kwargs):
        target_unit = kwargs["target_unit"]
        is_counterpart = False

        """ Opponent """
        target_unit_type = target_unit.unit_type_id
        target_is_zm = target_unit_type == UNIT_TYPE_ZEN_MASTER
        target_is_hacker = target_unit_type == UNIT_TYPE_HACKER
        target_is_troll = target_unit_type == UNIT_TYPE_TROLL

        """ Attacker """
        attacker_is_zm = self.unit_type_id = UNIT_TYPE_ZEN_MASTER
        attacker_is_hacker = self.unit_type_id == UNIT_TYPE_HACKER
        attacker_is_troll = self.unit_type_id == UNIT_TYPE_TROLL

        """ TODO: make this work """

        return is_counterpart

    def attack(self, **kwargs):
        """
        Get attack info from attacker and
        target, then return all the details
        of the attack
        """
        attacker = self
        target = kwargs["target"]
        is_hit = False
        is_draw = False
        hit_word = "draw"

        """ Attacker weapon """
        attacker_weapon = attacker.get_equipped_weapon()
        attacker_weapon_type = attacker_weapon.item_type

        """ Target weapon """
        target_weapon = target.get_equipped_weapon()
        target_weapon_type = target_weapon.item_type

        """ Rock crushes Scissors """
        if attacker_weapon.is_rock() and \
        target_weapon.is_scissors():
            is_hit = True
            hit_word = "crushes"

        """ Scissors cuts Paper """
        if attacker_weapon.is_scissors() and \
        target_weapon.is_paper():
            is_hit = True
            hit_word = "cuts"

        """ Paper covers Rock """
        if attacker_weapon.is_paper() and \
        target_weapon.is_rock():
            is_hit = True
            hit_word = "covers"

        """ Lizard eats Paper """
        if attacker_weapon.is_lizard() and \
        target_weapon.is_paper():
            is_hit = True
            hit_word = "eats"

        """ Spock vaporizes Rock """
        if attacker_weapon.is_spock() and \
        target_weapon.is_rock():
            is_hit = True
            hit_word = "vaporizes"

        """ Lizard poisons Spock """
        if attacker_weapon.is_lizard() and \
        target_weapon.is_spock():
            is_hit = True
            hit_word = "poisons"

        """ Rock crushes Lizard """
        if attacker_weapon.is_rock() and \
        target_weapon.is_lizard():
            is_hit = True
            hit_word = "crushes"

        """ Spock smashes Scissors """
        if attacker_weapon.is_spock() and \
        target_weapon.is_scissors():
            is_hit = True
            hit_word = "smashes"

        """ Paper disproves Spock """
        if attacker_weapon.is_paper() and \
        target_weapon.is_spock():
            is_hit = True
            hit_word = "disproves"

        """ Scissors decapitate Lizard """
        if attacker_weapon.is_scissors() and \
        target_weapon.is_lizard():
            is_hit = True
            hit_word = "decapitates"

        """ Draw! """
        if attacker_weapon_type == target_weapon_type:
            is_draw = True

        damage = 0
        is_critical_strike = False

        if is_hit and not is_draw:
            attack = self.get_attack()
            is_critical_strike = attack["is_critical_strike"]
            damage = attack["damage"]

            """
            After determining that the hit landed, apply damage
            to to the target unit
            """
            target.apply_damage(damage=damage,
                                attacker=attacker)

        return {
            "is_hit": is_hit,
            "attacker_weapon": attacker_weapon,
            "target_weapon": target_weapon,
            "is_draw": is_draw,
            "hit_word": hit_word,
            "damage": damage,
            "is_critical_strike": is_critical_strike
        }

    def get_attack(self):
        damage = self.get_attack_damage()
        item = self.get_equipped_weapon()

        """ Critical Strikes """
        crit_chance = self.get_critical_strike_chance()
        is_critical_strike = random.randrange(1, 100) <= crit_chance

        if is_critical_strike:
            damage *= 2

        """ Undead bonus """
        log.info("SpiffyRPG: unit has effects %s" % self.effects)

        for effect in self.effects:
            if effect.operator == "+":
                outgoing_damage_adjustment = effect.outgoing_damage_adjustment

                if outgoing_damage_adjustment > 0:
                    decimal_adjustment = float(outgoing_damage_adjustment) / float(100)
                    damage_adjustment = (damage * decimal_adjustment)
                    damage += damage_adjustment

                    log.info("SpiffyRPG: adding %s damage because undead" % damage_adjustment)

        attack_info = {
            "damage": damage,
            "item": item,
            "is_critical_strike": is_critical_strike
        }

        return attack_info

    def is_undead(self):
        return self.has_effect_name(name="Undead")

    def is_necromancer(self):
        return self.has_effect_name(name="Necromancer")

    def is_archeologist(self):
        return self.has_effect_name(name="Archeologist")

    def is_paper_enthusiast(self):
        return self.has_effect_name(name="Paper Enthusiast")

    def is_running_with_scissors(self):
        return self.has_effect_name(name="Running With Scissors")

    def is_blue_tongue(self):
        return self.has_effect_name(name="Blue Tongue")

    def is_vulcan_embraced(self):
        return self.has_effect_name(name="Vulcan's Embrace")

    def has_effect_name(self, **kwargs):
        name = kwargs["name"]

        for effect in self.effects:
            if effect.name.lower() == name.lower():
                return True

    def get_critical_strike_chance(self):
        return self.critical_strike_chance

    def get_incoming_damage_adjustment(self, damage):
        """
        Effects can increase/decrease incoming damage,
        so find any effects this unit has and adjust the damage
        accordingly
        """
        adjusted_damage = damage

        if len(self.effects) > 0:
            for effect in self.effects:
                if effect.operator == "-":
                    inc_dmg_adjustment = int(effect.incoming_damage_adjustment)

                    if inc_dmg_adjustment > 0:
                        decimal_adjustment = float(inc_dmg_adjustment) / float(100)
                        damage_amount = float(damage * decimal_adjustment)
                        adjusted_damage -= damage_amount

        return adjusted_damage

    def apply_damage(self, **kwargs):
        damage = kwargs["damage"]
        attacker = kwargs["attacker"]

        self.add_struck_unit(attacker)

        adjusted_damage = self.get_incoming_damage_adjustment(damage)
        self.hp = int(self.hp - adjusted_damage)

        """ Interrupt spell casting on damage """
        self.on_unit_spell_interrupted(unit=self, attacker=attacker)

        if self.hp <= 0:
            """
            Ensure that HP is never negative so players
            don't have to wait a long time to regenerate.
            """
            self.hp = 0

            self.on_unit_death()

    def on_unit_death(self):
        if self.is_player:
            self.announcer.unit_death()

        """
        This is used in unit_info as an alternative
        to displaying the time the unit has been alive,
        since it's dead now.
        """
        self.slain_at = time.time()

    def remove_effect_by_id(self, id):
        effects = []

        for e in effects:
            if e["id"] != id:
                effects.append(e)

        self.effects = effects

    def is_alive(self):
        return self.get_hp() > 0

    def is_dead(self):
        return self.get_hp() <= 0

    def kill(self):
        self.hp = 0
