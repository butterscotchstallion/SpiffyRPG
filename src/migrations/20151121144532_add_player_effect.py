"""
a caribou migration

name: add_player_effect 
version: 20151121144532
"""

def upgrade(connection):
    connection.execute("""CREATE TABLE spiffyrpg_player_effects(
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          effect_id INT,
                          player_id INT,
                          created_at TIMESTAMP,
                          expires_at TIMESTAMP)""")

    connection.commit()

def downgrade(connection):
    # add your downgrade step here
    pass
