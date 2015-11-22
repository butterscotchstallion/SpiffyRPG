"""
a caribou migration

name: create_monster_abilities 
version: 20151122163204
"""

def upgrade(connection):
    import time
    
    """
    CREATE TABLE spiffyrpg_monster_abilities(
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
              "Interdiction",
              "The agent plants malware on your device before it even reaches you!",
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_abilities(monster_id, name, 
                          description, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    params = (nsa_agent,
              "Malware Implant",
              "The agent plants malware on your device",
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_abilities(monster_id, name, 
                          description, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    params = (nsa_agent,
              "Stingray",
              "The agent's Stingray reads your text and predicts your next moves!'",
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_abilities(monster_id, name, 
                          description, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    # irc_operator
    params = (irc_operator,
              "Network Banishment",
              "You have violated terms of service.",
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_abilities(monster_id, name, 
                          description, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    params = (irc_operator,
              "NickServ Freeze",
              "Your account has been frozen.",
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_abilities(monster_id, name, 
                          description, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    params = (irc_operator,
              "Kill",
              "The IRC Operator forcefully closes the connection.",
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_abilities(monster_id, name, 
                          description, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    # script_kiddie
    params = (script_kiddie,
              "DNS Amplification",
              "The Script Kiddie uses DNS Amplification to DDoS your servers",
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_abilities(monster_id, name, 
                          description, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    params = (script_kiddie,
              "Smurf",
              "The Script Kiddie uses DNS Amplification to DDoS your servers",
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_abilities(monster_id, name, 
                          description, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    params = (script_kiddie,
              "Ping Flood",
              "ping -f",
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_abilities(monster_id, name, 
                          description, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    connection.commit()


def downgrade(connection):
    # add your downgrade step here
    pass
