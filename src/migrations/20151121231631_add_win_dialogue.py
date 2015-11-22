"""
a caribou migration

name: add_win_dialogue 
version: 20151121231631
"""

def upgrade(connection):
    import time

    open_source_contributor = 1
    internet_tough_guy = 2
    black_hat = 3

    dialogue_type = "win"

    # open_source_contributor
    params = ("Pull Request denied.", 
              dialogue_type,
              open_source_contributor,
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_character_dialogue(dialogue, 
                          dialogue_type, character_class_id, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    # internet_tough_guy
    params = ("You think you can get away with saying that shit to me over the Internet? Think again, fucker.", 
              dialogue_type,
              internet_tough_guy,
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_character_dialogue(dialogue, 
                          dialogue_type, character_class_id, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    # black_hat
    params = ("This is the end, my friend. Thank you for calling.", 
              dialogue_type,
              black_hat,
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_character_dialogue(dialogue, 
                          dialogue_type, character_class_id, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    connection.commit()

def downgrade(connection):
    # add your downgrade step here
    pass
