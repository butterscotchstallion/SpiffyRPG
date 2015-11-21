"""
a caribou migration

name: add_more_monsters 
version: 20151120211628
"""

def upgrade(connection):
    import time
    
    open_source_contributor = 1
    internet_tough_guy = 2
    black_hat = 3

    # open_source_contributor
    params = ("Reopened Issue", 
              "It still doesn't work!", 
              open_source_contributor, 
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monsters(
                          name,
                          description,
                          character_class_id,
                          created_at)
                          VALUES(?, ?, ?, ?)""", params)

    # black hat
    params = ("Script Kiddie", 
              "DDoS comin", 
              black_hat, 
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monsters(
                          name,
                          description,
                          character_class_id,
                          created_at)
                          VALUES(?, ?, ?, ?)""", params)

    # internet tough guy
    params = ("Parental Unit", 
              "Time to do chores!", 
              internet_tough_guy, 
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
