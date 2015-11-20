"""
a caribou migration

name: remove_dupe_moves 
version: 20151120162236
"""

def upgrade(connection):
        # fix inserting stuff into wrong table
    connection.execute("""DELETE FROM spiffyrpg_class_abilities
                          WHERE id > 6""")

    connection.commit()

def downgrade(connection):
    # add your downgrade step here
    pass
