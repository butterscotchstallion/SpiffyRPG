#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging as log


class UnitTitleCollection:

    """
    Stores unit type titles based on stage/level
    """

    def __init__(self, **kwargs):
        self.db = kwargs["db"]
        self.titles = []

    def populate(self):
        self.titles = self._get_titles_lookup()
        log.info("SpiffyRPG: fetching unit titles")

    def get_titles_by_unit_type_id(self, **kwargs):
        unit_type_id = kwargs["unit_type_id"]

        if unit_type_id in self.titles:
            return self.titles[unit_type_id]

    def _get_titles_lookup(self):
        cursor = self.db.cursor()

        cursor.execute("""SELECT
                          t.unit_type_id,
                          t.required_level,
                          t.title
                          FROM spiffyrpg_unit_type_titles t
                          ORDER BY t.required_level ASC""")

        titles = cursor.fetchall()
        cursor.close()
        titles_lookup = {}

        if len(titles) > 0:
            for t in titles:
                title = dict(t)
                unit_type_id = title["unit_type_id"]

                if unit_type_id not in titles_lookup:
                    titles_lookup[unit_type_id] = []

                titles_lookup[unit_type_id].append(title)

        return titles_lookup
