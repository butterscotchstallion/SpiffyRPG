"""
a caribou migration

name: update_provoke_ability 
version: 20151120002645
"""

def upgrade(connection):
    connection.execute("UPDATE spiffyrpg_class_abilities SET name = 'Drama Bomb' where id = 3")
    connection.commit()

def downgrade(connection):
    # add your downgrade step here
    pass
