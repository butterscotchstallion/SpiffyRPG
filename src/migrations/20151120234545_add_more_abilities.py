"""
a caribou migration

name: add_more_abilities 
version: 20151120234545
"""

def upgrade(connection):
    import time
    open_source_contributor = 1
    internet_tough_guy = 2
    black_hat = 3

    # open_source_contributor
    params = ("Fork", "Not just for contributing anymore!", 1, open_source_contributor, time.time())

    connection.execute("""INSERT INTO spiffyrpg_class_abilities(
                          name,
                          description,
                          min_level,
                          character_class_id,
                          created_at)
                          VALUES(?, ?, ?, ?, ?)""", params)

    # internet_tough_guy
    params = ("DDoS", "phat packets comin", 1, internet_tough_guy, time.time())

    connection.execute("""INSERT INTO spiffyrpg_class_abilities(
                          name,
                          description,
                          min_level,
                          character_class_id,
                          created_at)
                          VALUES(?, ?, ?, ?, ?)""", params)

    # black_hat
    params = ("Botnet", "The Black Hat uses a botnet to overwhelm their target.", 1, black_hat, time.time())

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
