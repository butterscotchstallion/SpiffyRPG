"""
a caribou migration

name: item_qualities 
version: 20151119160641
"""

def upgrade(connection):
    connection.execute("""CREATE TABLE IF NOT EXISTS spiffyrpg_item_qualities(
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT,
                          created_at TIMESTAMP)""")
    connection.commit()

    # todo add item qualities

def downgrade(connection):
    # add your downgrade step here
    pass
