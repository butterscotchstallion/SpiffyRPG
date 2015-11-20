"""
a caribou migration

name: players 
version: 20151119160512
"""

def upgrade(connection):
    connection.execute("""CREATE TABLE IF NOT EXISTS spiffyrpg_players(
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          character_class_id INTEGER,
                          character_name TEXT,
                          experience_gained INTEGER DEFAULT 0,
                          user_id INTEGER,
                          created_at TIMESTAMP)""")
    connection.commit()

def downgrade(connection):
    # add your downgrade step here
    pass
