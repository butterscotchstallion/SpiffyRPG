"""
a caribou migration

name: fix_monsters 
version: 20151120202222
"""

def upgrade(connection):
    # internet tough guy
    params = ("IRC Operator", 
              "Banned!", 
              3)

    connection.execute("""UPDATE spiffyrpg_monsters
                          SET name = ?,
                          description = ?
                          WHERE id = ?""", params)

    connection.commit()

def downgrade(connection):
    # add your downgrade step here
    pass
