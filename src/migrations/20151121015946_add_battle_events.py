"""
a caribou migration

name: add_battle_events 
version: 20151121015946
"""

def upgrade(connection):
    import time

    params = ("Giant Meteor",
              "A giant meteor falls from the sky and hits %s for %s damage", 
              10,
              20,
              0,
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_battle_events(
                          name,
                          description,
                          chance_to_occur,
                          percent_damage_of_target_hp,
                          percent_heal_of_target_hp,
                          created_at)
                          VALUES(?, ?, ?, ?, ?, ?)""", params)

    ########
    params = ("Mysterious Benefactor",
              "A %s emerges from the shadows and heals %s for %s", 
              50,
              0,
              20,
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_battle_events(
                          name,
                          description,
                          chance_to_occur,
                          percent_damage_of_target_hp,
                          percent_heal_of_target_hp,
                          created_at)
                          VALUES(?, ?, ?, ?, ?, ?)""", params)

    connection.commit()

def downgrade(connection):
    # add your downgrade step here
    pass
