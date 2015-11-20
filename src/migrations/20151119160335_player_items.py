"""
a caribou migration

name: player_items 
version: 20151119160335
"""

def upgrade(connection):
    connection.execute("""CREATE TABLE IF NOT EXISTS spiffyrpg_player_items(
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          item_id INTEGER,
                          player_id INTEGER,
                          created_at TIMESTAMP)""")
    connection.commit()

def downgrade(connection):
    # add your downgrade step here
    pass
