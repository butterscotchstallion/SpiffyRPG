"""
a caribou migration

name: add_items.py 
version: 20151118202157
"""

def upgrade(connection):
    import time

    connection.execute("""CREATE TABLE IF NOT EXISTS spiffyrpg_items(
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT,
                          description TEXT,
                          min_level INTEGER DEFAULT 1,
                          max_level INTEGER DEFAULT 100,
                          item_type TEXT,
                          created_at TIMESTAMP)""")

    params = ("Frozen Hot Pocket", "A delicious delicacy, frozen solid", time.time())
    connection.execute("""INSERT INTO spiffyrpg_items(name, description, created_at)
                          VALUES(?, ?, ?)""", params)

    connection.commit()

def downgrade(connection):
    # add your downgrade step here
    pass
