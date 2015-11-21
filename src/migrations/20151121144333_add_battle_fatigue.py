"""
a caribou migration

name: add_battle_fatigue 
version: 20151121144333
"""

def upgrade(connection):
    import time

    params = ("Battle Fatigue", 
              "You are weary from battle and must wait before battling again.", 
              "+",
              0,
              0,
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
