"""
a caribou migration

name: add_effects 
version: 20151121104040
"""

def upgrade(connection):
    import time

    params = ("Carmack's Inspiration",
              "Carmack's Inspiration grants an additional 5% chance to critical strike",
              "+",
              0,
              5,
              0,
              0,
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_effects(
                          name,
                          description,
                          operator,
                          hp_percent_adjustment,
                          critical_strike_chance_adjustment,
                          damage_percent_adjustment,
                          chance_to_hit_adjustment,
                          created_at)
                          VALUES(?, ?, ?, ?, ?, ?, ?, ?)""", params)

    connection.commit()

def downgrade(connection):
    # add your downgrade step here
    pass
