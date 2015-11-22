"""
a caribou migration

name: create_monster_dialogue 
version: 20151122124853
"""

def upgrade(connection):
    connection.execute("""CREATE TABLE spiffyrpg_monster_dialogue(
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          monster_id INT,
                          dialogue TEXT,
                          dialogue_type TEXT,
                          created_at TIMESTAMP)""")
    connection.commit()

def downgrade(connection):
    # add your downgrade step here
    pass
