"""
a caribou migration

name: add_more_dialogue 
version: 20151121214233
"""

def upgrade(connection):
    import time

    open_source_contributor = 1
    internet_tough_guy = 2
    black_hat = 3

    # open_source_contributor
    params = ("I will *not* be merging any code from %s into the kernel until this constant pattern is fixed.", 
              "intro",
              open_source_contributor,
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_character_dialogue(dialogue, 
                          dialogue_type, character_class_id, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    # internet_tough_guy
    params = ("You are nothing to me but just another target.", 
              "intro",
              internet_tough_guy,
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_character_dialogue(dialogue, 
                          dialogue_type, character_class_id, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    # black_hat
    params = ("Your BLT drive is about to go AWOL", 
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
