"""
a caribou migration

name: create_monsters 
version: 20151120195630
"""

def upgrade(connection):
    connection.execute("""CREATE TABLE spiffyrpg_monsters(
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT,
                          description TEXT,
                          character_class_id INT,
                          created_at TIMESTAMP)""")
    connection.commit()

def downgrade(connection):
    # add your downgrade step here
    pass
