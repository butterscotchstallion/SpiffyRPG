"""
a caribou migration

name: add_more_finishing_moves 
version: 20151121000544
"""

def upgrade(connection):
    import time

    open_source_contributor = 1
    internet_tough_guy = 2
    black_hat = 3

    # open_source_contributor level 3
    params = ("Resolved: Invalid", 
              "The Open Source Contributor marks their opponent 'Invalid'.", 
              3, 
              open_source_contributor, 
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_class_finishing_moves(
                          name,
                          description,
                          min_level,
                          character_class_id,
                          created_at)
                          VALUES(?, ?, ?, ?, ?)""", params)

    # black_hat 3
    params = ("Persistent Malware", 
              "Might as well flatten and reinstall...", 
              3, 
              black_hat, 
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_class_finishing_moves(
                          name,
                          description,
                          min_level,
                          character_class_id,
                          created_at)
                          VALUES(?, ?, ?, ?, ?)""", params)

    # internet 3
    params = ("Empty Threat", 
              "Scary if it was believable!", 
              3, 
              internet_tough_guy, 
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_class_finishing_moves(
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
