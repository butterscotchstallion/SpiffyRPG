"""
a caribou migration

name: add_monster_abilities 
version: 20151122162939
"""

def upgrade(connection):
    connection.execute("""CREATE TABLE spiffyrpg_monster_abilities(
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          monster_id INT,
                          name TEXT,
                          description TEXT,
                          created_at TIMESTAMP)""")

    connection.commit()

def downgrade(connection):
    # add your downgrade step here
    pass
