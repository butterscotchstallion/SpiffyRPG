"""
a caribou migration

name: fix_class_ability 
version: 20151120002253
"""

def upgrade(connection):
    connection.execute("UPDATE spiffyrpg_class_abilities SET character_class_id = 3 where id = 3")
    connection.commit()

def downgrade(connection):
    # add your downgrade step here
    pass
