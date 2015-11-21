"""
a caribou migration

name: add_new_abilities 
version: 20151121025025
"""

def upgrade(connection):
    import time
    open_source_contributor = 1
    internet_tough_guy = 2
    black_hat = 3

    # open_source_contributor
    params = ("Squash Commits", "Squash those merge commits!", 4, open_source_contributor, time.time())

    connection.execute("""INSERT INTO spiffyrpg_class_abilities(
                          name,
                          description,
                          min_level,
                          character_class_id,
                          created_at)
                          VALUES(?, ?, ?, ?, ?)""", params)

    # internet_tough_guy
    params = ("Delusions of Grandeur", "I'm the best and everyone should know it!", 4, internet_tough_guy, time.time())

    connection.execute("""INSERT INTO spiffyrpg_class_abilities(
                          name,
                          description,
                          min_level,
                          character_class_id,
                          created_at)
                          VALUES(?, ?, ?, ?, ?)""", params)
    # black_hat
    params = ("Social Engineering", "The Black Hat uses Social Engineering to discover their target's vulnerabilities.", 4, black_hat, time.time())

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
