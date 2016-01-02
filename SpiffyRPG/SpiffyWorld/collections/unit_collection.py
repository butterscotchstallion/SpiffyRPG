#!/usr/bin/env python
# -*- coding: utf-8 -*-
from SpiffyWorld import Unit


class UnitCollection:

    """
    All the units!
    """

    def __init__(self):
        self.units = []

    def add(self, unit):
        if not isinstance(unit, Unit):
            raise ValueError("unit must be an instance of Unit")

        if unit not in self.units:
            self.units.append(unit)

    def get_players(self):
        return [unit for unit in self.units if unit.is_player]

    def get_player_by_user_id(self, user_id):
        players = self.get_players()

        for player in players:
            if player.user_id == user_id:
                return player

    def get_top_players_by_xp(self):
        players = self.get_players()

        if len(players) >= 1:
            # top 3 or all the players, whichever is less.
            limit = min(len(players), 3)

            top_players = sorted(
                players, key=lambda x: x.experience, reverse=True)

            return top_players[0:limit]

    def get_units_by_unit_id_list(self, unit_id_list):
        return [unit for unit in self.units if unit.id in unit_id_list]
