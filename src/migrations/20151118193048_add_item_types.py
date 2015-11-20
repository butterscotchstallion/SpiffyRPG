"""
a caribou migration

name: add_item_types.py 
version: 20151118193048
"""
def upgrade(connection):
    import time

    connection.execute("""CREATE TABLE IF NOT EXISTS spiffyrpg_item_types(
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT,
                          created_at TIMESTAMP)""")

    params = ("Melee", time.time())

    query = """INSERT INTO spiffyrpg_item_types(name, created_at)
               VALUES(?, ?)"""
    connection.execute(query, params)
    connection.commit()

def downgrade(connection):
    query = """DELETE FROM spiffyrpg_item_types
               WHERE name = 'Melee'"""
    connection.execute(query)
    connection.commit()
