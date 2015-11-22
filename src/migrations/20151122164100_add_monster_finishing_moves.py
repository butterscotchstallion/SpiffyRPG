"""
a caribou migration

name: add_monster_finishing_moves 
version: 20151122164100
"""

def upgrade(connection):
    import time
    
    """
    CREATE TABLE spiffyrpg_monster_finishing_moves(
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          monster_id INT,
                          name TEXT,
                          description TEXT,
                          created_at TIMESTAMP)
    """
    nsa_agent = 2
    irc_operator = 3
    script_kiddie = 5

    # nsa_agent
    params = (nsa_agent,
              "Duqu",
              "You are now infected with Duqu.",
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_finishing_moves(monster_id, name, 
                          description, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    params = (nsa_agent,
              "Stuxnet",
              "You are now infected with Stuxnet.",
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_finishing_moves(monster_id, name, 
                          description, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    params = (nsa_agent,
              "Skywiper",
              "You are now infected with Skywiper.",
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_finishing_moves(monster_id, name, 
                          description, created_at)
                          VALUES(?, ?, ?, ?)""", params)


    ### irc_operator
    params = (irc_operator,
              "WALLOPS",
              "Sends a \"Message\" to all those with the umode +w.",
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_finishing_moves(monster_id, name, 
                          description, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    params = (irc_operator,
              "ZLINE",
              "Disables all access to the IRC server from a specified IP.",
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_finishing_moves(monster_id, name, 
                          description, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    params = (irc_operator,
              "SHUN",
              "Prevents a user from executing ANY command except ADMIN and respond to Server Pings. This effectively prevents them from doing anything on the server.",
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_finishing_moves(monster_id, name, 
                          description, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    ### script_kiddie
    params = (script_kiddie,
              "WinNuke",
              "Sends a \"Message\" to all those with the umode +w.",
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_finishing_moves(monster_id, name, 
                          description, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    params = (script_kiddie,
              "Low Orbit Ion Cannon",
              "Low Orbit Ion Cannon",
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_finishing_moves(monster_id, name, 
                          description, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    params = (script_kiddie,
              "BackOrifice",
              "BackOrifice ",
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_finishing_moves(monster_id, name, 
                          description, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    connection.commit()

def downgrade(connection):
    # add your downgrade step here
    pass
