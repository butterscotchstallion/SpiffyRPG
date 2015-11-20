"""
a caribou migration

name: add_class_abilities 
version: 20151120000221
"""

def upgrade(connection):
    import time

    open_source_contributor = 1
    internet_tough_guy = 2
    attention_whore = 3

    # open_source_contributor
    params = ("Force Push", "git push -f", 1, open_source_contributor, time.time())

    connection.execute("""INSERT INTO spiffyrpg_class_abilities(
                          name,
                          description,
                          min_level,
                          character_class_id,
                          created_at)
                          VALUES(?, ?, ?, ?, ?)""", params)

    # internet_tough_guy
    params = ("Navy Seals Copypasta", "He graduated at the top of his class", 1, internet_tough_guy, time.time())

    connection.execute("""INSERT INTO spiffyrpg_class_abilities(
                          name,
                          description,
                          min_level,
                          character_class_id,
                          created_at)
                          VALUES(?, ?, ?, ?, ?)""", params)

    # attention whore
    params = ("Provoke", "", 1, attention_whore, time.time())

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
