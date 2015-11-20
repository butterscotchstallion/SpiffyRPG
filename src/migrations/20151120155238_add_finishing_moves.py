"""
a caribou migration

name: add_finishing_moves 
version: 20151120155238
"""

def upgrade(connection):
    import time

    open_source_contributor = 1
    internet_tough_guy = 2
    black_hat = 3

    connection.execute("""CREATE TABLE spiffyrpg_class_finishing_moves(
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT,
                          description TEXT,
                          min_level INT,
                          character_class_id INT,
                          created_at TIMESTAMP)""")

    # open_source_contributor level 1
    params = ("Resolved: Cannot reproduce", 
              "The Open Source Contributor removes their opponent's ability to reproduce", 
              1, 
              open_source_contributor, 
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_class_abilities(
                          name,
                          description,
                          min_level,
                          character_class_id,
                          created_at)
                          VALUES(?, ?, ?, ?, ?)""", params)

    # open_source_contributor level 2
    params = ("Torvald's Fury", 
              "The Open Source Contributor delivers a deadly vitriolic rant.", 
              2, 
              open_source_contributor, 
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_class_abilities(
                          name,
                          description,
                          min_level,
                          character_class_id,
                          created_at)
                          VALUES(?, ?, ?, ?, ?)""", params)

    # black_hat level 1
    params = ("kill -9", 
              "This kills the process.", 
              1, 
              black_hat, 
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_class_abilities(
                          name,
                          description,
                          min_level,
                          character_class_id,
                          created_at)
                          VALUES(?, ?, ?, ?, ?)""", params)

    # black_hat level 2
    params = ("Rootkit", 
              "ACID BURN SEZ LEAVE B4 U R EXPUNGED", 
              2, 
              black_hat, 
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_class_abilities(
                          name,
                          description,
                          min_level,
                          character_class_id,
                          created_at)
                          VALUES(?, ?, ?, ?, ?)""", params)

    # internet_tough_guy level 1
    params = ("360 NO-SCOPE", 
              "YEAAAAAAAAAH!!!!! I F**ING OWNED THAT BTCH!!!! gET 360 NOSCOPED AND #SHREKT!!!!", 
              1, 
              internet_tough_guy, 
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_class_abilities(
                          name,
                          description,
                          min_level,
                          character_class_id,
                          created_at)
                          VALUES(?, ?, ?, ?, ?)""", params)

    # internet_tough_guy level 2
    params = ("Five Point Palm Exploding Heart Technique", 
              "Quite simply, the deadliest blow in all of martial arts. He hits you with his fingertips at 5 different pressure points on your body, and then lets you walk away. But once you've taken five steps your heart explodes inside your body and you fall to the floor, dead.", 
              1, 
              internet_tough_guy, 
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_class_abilities(
                          name,
                          description,
                          min_level,
                          character_class_id,
                          created_at)
                          VALUES(?, ?, ?, ?, ?)""", params)

    connection.commit()

def downgrade(connection):
    # add your downgrade step here
    pass
