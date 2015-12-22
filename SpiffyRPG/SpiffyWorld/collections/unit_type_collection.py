#!/usr/bin/env python
# -*- coding: utf-8 -*-
from SpiffyWorld import UnitType


class UnitTypeCollection:

    """
    A whole mess of unit types
    """

    def __init__(self, **kwargs):
        self.unit_types = []

    def add(self, unit_type):
        if not isinstance(unit_type, UnitType):
            raise ValueError("unit_type must be an instance of UnitType")

        if unit_type not in self.unit_types:
            self.unit_types.append(unit_type)

    def get_unit_type_by_name(self, unit_type_name):
        for unit_type in self.unit_types:
            if unit_type.name.lower().startswith(unit_type_name.lower()):
                return unit_type

    def get_unit_type_name_list(self):
        unit_type_name_list = [unit_type.name for unit_type in self.unit_types]

        if unit_type_name_list:
            unit_type_name_list = sorted(unit_type_name_list, key=lambda x: x)

        return ", ".join(unit_type_name_list)
