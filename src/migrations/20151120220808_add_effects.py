"""
a caribou migration

name: add_effects 
version: 20151120220808
"""

def upgrade(connection):
    connection.execute("""CREATE TABLE spiffyrpg_effects(
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT,
                          description TEXT,
                          operator VARCHAR(1),
                          hp_percent_adjustment INT,
                          critical_strike_chance_adjustment INT,
                          damage_percent_adjustment INT,
                          chance_to_hit_adjustment INT,
                          created_at TIMESTAMP)""")
    connection.commit()

def downgrade(connection):
    # add your downgrade step here
    pass
