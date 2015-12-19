# -*- coding: utf-8 -*-

class Effect:
    """
    Representation of all effects
    """
    def __init__(self, **kwargs):
        self.db = kwargs["db"]
    
    def get_effects(self):
        """
        Fetches effects for one or many units
        """
        cursor = self.db.cursor()
        
        cursor.execute("""SELECT
                          e.id,
                          e.name,
                          e.description,
                          e.operator,
                          e.hp_adjustment,
                          e.incoming_damage_adjustment,
                          e.outgoing_damage_adjustment,
                          e.interval_seconds,
                          e.stacks,
                          e.created_at
                          FROM spiffyrpg_effects e""")

        tmp_effects = cursor.fetchall()
        effects = []

        cursor.close()

        if len(tmp_effects) > 0:
            for e in tmp_effects:
                effect = dict(e)
                effects.append(effect)

        return effects