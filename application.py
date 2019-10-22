# Catalog project for Udacity

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catagory, Item

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/catalog/<string:sport_name>/<string:item_name>/JSON')
def itemJSON(sport_name, item_name):
    equipment = session.query(Item).filter_by(name = item_name).one()
    return jsonify(Item=[equipment.serialize])




if __name__ == '__main__':
    app.secret_key= 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)