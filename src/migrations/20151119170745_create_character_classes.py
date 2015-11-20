"""
a caribou migration

name: create_character_classes 
version: 20151119170745
"""

def upgrade(connection):
    connection.execute("""CREATE TABLE IF NOT EXISTS spiffyrpg_character_classes(
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT,
                          created_at TIMESTAMP)""")
    connection.commit()

def downgrade(connection):
    connection.execute("""DROP TABLE spiffyrpg_character_classes""")
    connection.commit()
