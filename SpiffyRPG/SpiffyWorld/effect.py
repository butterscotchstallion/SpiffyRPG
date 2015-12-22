#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

class Effect:
    """
    Representation of an effect. Effects can alter the behavior
    or stats of a unit and can have a duration or be permanent
    """
    def __init__(self, **kwargs):
        effect = kwargs["effect"]
        self.id = effect["id"]
        self.name = effect["name"]
        self.description = effect["description"]
        self.operator = effect["operator"]
        self.hp_adjustment = effect["hp_adjustment"]
        self.incoming_damage_adjustment = effect["incoming_damage_adjustment"]
        self.outgoing_damage_adjustment = effect["outgoing_damage_adjustment"]
        self.interval_seconds = effect["interval_seconds"]
        self.stacks = int(effect["stacks"])
        self.effect_on_possession = False
        self.created_at = time.time()

        if "effect_on_possession" in effect:
            self.effect_on_possession = effect["effect_on_possession"]

    def get_hp_adjustment(self):
        return self.hp_adjustment * self.stacks

    def get_incoming_damage_adjustment(self):
        return self.incoming_damage_adjustment * self.stacks

    def get_outgoing_damage_adjustment(self):
        return self.outgoing_damage_adjustment * self.stacks
