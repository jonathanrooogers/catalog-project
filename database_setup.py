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
    username = Column(String(40), index=true)
    password_hash =  Column(String(64))


class Catagory(Base):
    __tablename__ = 'catagory'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return object data"""
        return {
            'name': self.name,
            'id': self.id,
        }


class Item(Base):
    __tablename__ = 'item'

    name = Column(String(100), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(400))
    catagory_id = Column(Integer, ForeignKey('catagory.id'))
    catagory = relationship("Catagory", backref=backref("item", cascade="all, delete-orphan"))


    @property
    def serialize(self):
        return{
            'name' : self.name,
            'description' : self.description,
            'id' : self.id,
            'catagory_id' : self.catagory_id,
        }


engine = create_engine('sqlite:///catalog.db')


Base.metadata.create_all(engine)