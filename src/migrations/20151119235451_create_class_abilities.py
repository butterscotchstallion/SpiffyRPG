"""
a caribou migration

name: create_class_abilities 
version: 20151119235451
"""

def upgrade(connection):
    connection.execute("""CREATE TABLE IF NOT EXISTS spiffyrpg_class_abilities(
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT,
                          description TEXT,
                          min_level INT,
                          character_class_id INT,
                          created_at TIMESTAMP)""")
    connection.commit()

def downgrade(connection):
    # add your downgrade step here
    pass
