"""
a caribou migration

name: replace_attention_whore 
version: 20151120143852
"""

def upgrade(connection):
    connection.execute("""UPDATE spiffyrpg_character_classes
                          SET name = "Black Hat" 
                          where id = 3""")
    connection.commit()

def downgrade(connection):
    # add your downgrade step here
    pass
