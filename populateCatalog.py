from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Catagory, Item

engine = create_engine('postgresql://catalog:yourpassword@localhost/catalog')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

user1 = User(email="jono-@hotmail.com", name="Jonathan")


sport1 = Catagory(name="Swimming", user=user1)

session.add(sport1)
session.commit()

sportEquipment1 = Item(name="Goggles",
                       description=("Protect eyes from having"
                                    "contact with water"),
                       catagory=sport1, user=user1)

session.add(sportEquipment1)
session.commit()
