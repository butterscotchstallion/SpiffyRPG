"""
a caribou migration

name: add_battles 
version: 20151120163601
"""

def upgrade(connection):
    connection.execute("""CREATE TABLE spiffyrpg_class_battles(
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          attacker_player_id INT,
                          target_player_id INT,
                          winner_player_id INT,
                          loser_player_id INT,
                          created_at TIMESTAMP)""")
    connection.commit()

def downgrade(connection):
    # add your downgrade step here
    pass
