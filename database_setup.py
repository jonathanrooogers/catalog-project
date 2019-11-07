# Catalog project for Udacity
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    email = Column(String(200), unique = True)
    name =  Column(String(64))
    picture = Column(String)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'picture': self.picture
        }


class Catagory(Base):
    __tablename__ = 'catagory'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            'user_id' : self.user_id,
        }


class Item(Base):
    __tablename__ = 'item'

    name = Column(String(100), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(400))
    catagory_id = Column(Integer, ForeignKey('catagory.id'))
    catagory = relationship("Catagory", backref=backref("item", cascade="all, delete-orphan"))
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship(User)


    @property
    def serialize(self):
        return{
            'name' : self.name,
            'description' : self.description,
            'id' : self.id,
            'catagory_id' : self.catagory_id,
            'user_id' : self.user_id,
        }


engine = create_engine('sqlite:///catalog.db')


Base.metadata.create_all(engine)