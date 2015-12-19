# -*- coding: utf-8 -*-

class Unit:
    """
    Unit model
    """
    def __init__(self, **kwargs):
        self.db = kwargs["db"]
    
    def add_experience(self, unit_id, experience):
        cursor = self.db.cursor()
        params = (experience, unit_id)

        cursor.execute("""UPDATE spiffyrpg_units
                          SET experience = ?
                          WHERE id = ?""", params)

        self.db.commit()
        cursor.close()

    def set_title(self, unit_id, title):
        log.info("SpiffyRPG: %s sets title to %s" % (old_name, self.name))

        cursor = self.db.cursor()
        params = (title, unit_id)

        cursor.execute("""UPDATE spiffyrpg_units
                          SET name = ?
                          WHERE id = ?""", params)

        self.db.commit()
        cursor.close()

    def get_units(self, **kwargs):
        cursor = self.db.cursor()
        
        query = """SELECT
                   u.id,
                   u.unit_type_id,
                   u.name AS unit_name,
                   utypes.name AS unit_type_name,
                   u.experience,
                   u.limnoria_user_id AS user_id,
                   u.combat_status,
                   CASE WHEN b.unit_id IS NULL
                   THEN 0
                   ELSE 1
                   END AS is_boss
                   FROM spiffyrpg_units u
                   JOIN spiffyrpg_unit_types utypes ON utypes.id = u.unit_type_id
                   LEFT JOIN spiffyrpg_dungeon_boss_units b ON b.unit_id = u.id
                   WHERE 1=1
                   GROUP BY u.id"""

        cursor.execute(query)

        units = cursor.fetchall()
        cursor.close()
        
        return units
