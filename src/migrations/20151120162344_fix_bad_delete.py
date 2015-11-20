"""
a caribou migration

name: fix_bad_delete 
version: 20151120162344
"""

def upgrade(connection):
    # fix inserting stuff into wrong table
    connection.execute("""DELETE FROM spiffyrpg_class_abilities
                          WHERE id > 6""")

    connection.commit()

def downgrade(connection):
    # add your downgrade step here
    pass
