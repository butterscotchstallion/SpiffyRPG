"""
a caribou migration

name: add_monsters 
version: 20151120200011
"""

def upgrade(connection):
    import time
    
    open_source_contributor = 1
    internet_tough_guy = 2
    black_hat = 3

    # open_source_contributor
    params = ("Heisenbug", 
              "It exists and doesn't exist simultaneously...", 
              open_source_contributor, 
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monsters(
                          name,
                          description,
                          character_class_id,
                          created_at)
                          VALUES(?, ?, ?, ?)""", params)

    # black hat
    params = ("NSA Agent", 
              "They're onto you...", 
              black_hat, 
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monsters(
                          name,
                          description,
                          character_class_id,
                          created_at)
                          VALUES(?, ?, ?, ?)""", params)


def downgrade(connection):
    # add your downgrade step here
    pass
