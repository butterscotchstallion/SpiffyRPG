"""
a caribou migration

name: add_character_classes.py 
version: 20151118195851
"""
import time

def upgrade(connection):
    # add your upgrade step here
    params = ("IRC Troll", time.time())
    connection.execute("""INSERT INTO spiffyrpg_character_classes(name, created_at)
                          VALUES(?, ?)""", params)

    params = ("Internet Tough Guy", time.time())
    connection.execute("""INSERT INTO spiffyrpg_character_classes(name, created_at)
                          VALUES(?, ?)""", params)

    params = ("Attention Whore", time.time())
    connection.execute("""INSERT INTO spiffyrpg_character_classes(name, created_at)
                          VALUES(?, ?)""", params)

    connection.commit()

def downgrade(connection):
    # add your downgrade step here
    pass
