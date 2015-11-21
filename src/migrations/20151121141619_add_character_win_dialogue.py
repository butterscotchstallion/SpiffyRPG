"""
a caribou migration

name: add_character_win_dialogue 
version: 20151121141619
"""

def upgrade(connection):
    import time

    open_source_contributor = 1
    internet_tough_guy = 2
    black_hat = 3

    # open_source_contributor
    params = ("This issue will be resolved momentarily.", 
              "win",
              open_source_contributor,
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_character_dialogue(dialogue, 
                          dialogue_type, character_class_id, created_at)
                          VALUES(?, ?, ?, ?)""", params)
    
    # internet_tough_guy
    params = ("You're fucking dead, kiddo.", 
              "win",
              internet_tough_guy,
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_character_dialogue(dialogue, 
                          dialogue_type, character_class_id, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    # black_hat
    params = ("Mess with the best, die like the rest.", 
              "win",
              black_hat,
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_character_dialogue(dialogue, 
                          dialogue_type, character_class_id, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    connection.commit()

def downgrade(connection):
    # add your downgrade step here
    pass
