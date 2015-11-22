"""
a caribou migration

name: add_monster_dialogue 
version: 20151122131046
"""

def upgrade(connection):
    """
    CREATE TABLE spiffyrpg_monster_dialogue(
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          monster_id INT,
                          dialogue TEXT,
                          dialogue_type TEXT,
                          created_at TIMESTAMP)
    """
    import time

    """
    2|NSA Agent
    3|IRC Operator
    5|Script Kiddie
    """
    
    nsa_agent = 2
    irc_operator = 3
    script_kiddie = 5

    # irc_operator
    params = (irc_operator,
              "Do you have a support question?",
              "intro",
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_dialogue(monster_id, dialogue, 
                          dialogue_type, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    ##
    params = (irc_operator,
              "Hello. How can I help?",
              "intro",
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_dialogue(monster_id, dialogue, 
                          dialogue_type, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    ## 
    params = (irc_operator,
              "Hey %s, what's up?",
              "intro",
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_dialogue(monster_id, dialogue, 
                          dialogue_type, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    #### win quips
    dialogue_type = "win"

    ## 
    params = (irc_operator,
              "Spam is off-topic on freenode.",
              dialogue_type,
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_dialogue(monster_id, dialogue, 
                          dialogue_type, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    ##
    params = (irc_operator,
              "You have violated network guidelines.",
              dialogue_type,
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_dialogue(monster_id, dialogue, 
                          dialogue_type, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    params = (irc_operator,
              "You should know better.",
              dialogue_type,
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_dialogue(monster_id, dialogue, 
                          dialogue_type, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    ##### nsa agent

    params = (nsa_agent,
              "I know what you did last summer.",
              "intro",
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_dialogue(monster_id, dialogue, 
                          dialogue_type, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    ##
    params = (nsa_agent,
              "Hey! That's classified!",
              "intro",
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_dialogue(monster_id, dialogue, 
                          dialogue_type, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    ## 
    params = (nsa_agent,
              "Our system has determined you are a credible threat to national security.",
              "intro",
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_dialogue(monster_id, dialogue, 
                          dialogue_type, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    #### win quips
    dialogue_type = "win"

    ## 
    params = (nsa_agent,
              "This was a matter of national security.",
              dialogue_type,
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_dialogue(monster_id, dialogue, 
                          dialogue_type, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    ## 
    params = (nsa_agent,
              "Our data indicates this conclusion was inevitable.",
              dialogue_type,
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_dialogue(monster_id, dialogue, 
                          dialogue_type, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    params = (nsa_agent,
              "You have nothing to fear if you have nothing to hide.",
              dialogue_type,
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_dialogue(monster_id, dialogue, 
                          dialogue_type, created_at)
                          VALUES(?, ?, ?, ?)""", params)


    ##### script_kiddie

    params = (script_kiddie,
              "ddos comin",
              "intro",
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_dialogue(monster_id, dialogue, 
                          dialogue_type, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    ##
    params = (script_kiddie,
              "u better wathc out b4 i hack ur server",
              "intro",
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_dialogue(monster_id, dialogue, 
                          dialogue_type, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    ## 
    params = (script_kiddie,
              "LOL U DONT EVEN KNOW WHAT IM CAPABLE OF NOOB",
              "intro",
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_dialogue(monster_id, dialogue, 
                          dialogue_type, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    #### win quips
    dialogue_type = "win"

    ## 
    params = (script_kiddie,
              "LMFAO 0wned u n00b",
              dialogue_type,
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_dialogue(monster_id, dialogue, 
                          dialogue_type, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    ## 
    params = (script_kiddie,
              "LOL rekt scrub",
              dialogue_type,
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_dialogue(monster_id, dialogue, 
                          dialogue_type, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    params = (script_kiddie,
              "lol pwn3d",
              dialogue_type,
              time.time())

    connection.execute("""INSERT INTO spiffyrpg_monster_dialogue(monster_id, dialogue, 
                          dialogue_type, created_at)
                          VALUES(?, ?, ?, ?)""", params)

    connection.commit()

def downgrade(connection):
    # add your downgrade step here
    pass
