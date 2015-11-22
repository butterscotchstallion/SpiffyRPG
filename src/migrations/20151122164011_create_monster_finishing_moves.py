"""
a caribou migration

name: create_monster_finishing_moves 
version: 20151122164011
"""

def upgrade(connection):
    connection.execute("""CREATE TABLE spiffyrpg_monster_finishing_moves(
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          monster_id INT,
                          name TEXT,
                          description TEXT,
                          created_at TIMESTAMP)""")

    connection.commit()

def downgrade(connection):
    # add your downgrade step here
    pass
