"""
a caribou migration

name: update_black_hat_abilities 
version: 20151120150416
"""

def upgrade(connection):
    params = ("Righteous Hack", 
              "\"Look, you wanna be elite? You gotta do a righteous hack.\"",
              3)
    connection.execute("""UPDATE spiffyrpg_class_abilities
                          SET name = ?, description = ?
                          WHERE id = ?""", params)

    params = ("0day", 
              "The Black Hat's cache of undisclosed vulnerabilities are a formidable tool.",
              5)
    connection.execute("""UPDATE spiffyrpg_class_abilities
                          SET name = ?, description = ?
                          WHERE id = ?""", params)

    connection.commit()

def downgrade(connection):
    # add your downgrade step here
    pass
