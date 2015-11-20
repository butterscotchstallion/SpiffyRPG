"""
a caribou migration

name: add_more_abilities 
version: 20151120092527
"""

def upgrade(connection):
    import time

    open_source_contributor = 1
    internet_tough_guy = 2
    attention_whore = 3
    required_level = 2

    # open_source_contributor level 2
    params = ("Blocker Issue", "A JIRA Blocker Issue, high priority!", required_level, open_source_contributor, time.time())

    connection.execute("""INSERT INTO spiffyrpg_class_abilities(
                          name,
                          description,
                          min_level,
                          character_class_id,
                          created_at)
                          VALUES(?, ?, ?, ?, ?)""", params)

    # attention whore level 2
    params = ("Unstable Emotions", "Your unstable emotions consume your target, engulfing them in darkness", required_level, attention_whore, time.time())

    connection.execute("""INSERT INTO spiffyrpg_class_abilities(
                          name,
                          description,
                          min_level,
                          character_class_id,
                          created_at)
                          VALUES(?, ?, ?, ?, ?)""", params)

    # internet tough guy level 2
    params = ("Backtrace", "Consequences will never be the same", required_level, internet_tough_guy, time.time())

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
