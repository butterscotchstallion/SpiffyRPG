"""
a caribou migration

name: update_monster_dialogue 
version: 20151121121708
"""

def upgrade(connection):
    import time

    open_source_contributor = 1
    internet_tough_guy = 2
    black_hat = 3

    # open_source_contributor
    params = ("This issue will be resolved momentarily.", 
              "intro",
              open_source_contributor,
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_character_dialogue(dialogue, 
                          dialogue_type, character_class_id, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    # internet_tough_guy
    params = ("What the fuck did you just fucking say about me, you little bitch?", 
              "intro",
              internet_tough_guy,
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_character_dialogue(dialogue, 
                          dialogue_type, character_class_id, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    # black_hat
    params = ("ACID BURN SEZ LEAVE B4 U R EXPUNGED", 
              "intro",
              black_hat,
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_character_dialogue(dialogue, 
                          dialogue_type, character_class_id, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    connection.commit()

def downgrade(connection):
    # add your downgrade step here
    pass
