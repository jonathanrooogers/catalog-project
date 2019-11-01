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

@app.route('/catalog/<string:catagory_name>/<int:catagory_id>/<string:item_name>/<int:item_id>/JSON')
def itemJSON(catagory_name, item_name,catagory_id,item_id):
    equipment = session.query(Item).filter_by(name = item_name).one()
    return jsonify(Item=[equipment.serialize])

@app.route('/')
@app.route('/catalog')
def catalog():
    catalog = session.query(Catagory).all()
    items = session.query(Item).all()
    return render_template('homecatalog.html', catalog=catalog, items = items)


@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCategory():

    if request.method == 'POST':
        newCatagory = Catagory(name=request.form['name'])
        session.add(newCatagory)
        session.commit()
        return redirect(url_for('catalog'))
    else:
        return render_template('new_catagory.html')


@app.route('/catalog/<string:catagory_name>/<int:catagory_id>/edit/', methods=['GET', 'POST'])
def editCatagory(catagory_name,catagory_id):

    catagory = session.query(Catagory).filter_by(id=catagory_id).one()

    if request.method == 'POST':
        if request.form['name']:
            catagory.name = request.form['name']
            return redirect(url_for('catalog'))
    else:
        return render_template('edit_category.html', catagory=catagory)

@app.route('/catalog/<string:catagory_name>/<int:catagory_id>/delete/', methods=['GET', 'POST'])
def deleteCatagory(catagory_name,catagory_id):
        
    catagory = session.query(Catagory).filter_by(id=catagory_id).one()

    if request.method == 'POST':
        session.delete(catagory)
        session.commit()


        return redirect(url_for('viewitems', catagory_id=catagory_id))
    else:
        return render_template('delete_catagory.html', catagory=catagory)

@app.route('/catalog/<string:catagory_name>/<int:catagory_id>')
@app.route('/catalog/<string:catagory_name>/<int:catagory_id>/item/')
def viewitems(catagory_name,catagory_id):
    catagory = session.query(Catagory).filter_by(id=catagory_id).one()
    items = session.query(Item).filter_by(catagory_id=catagory_id)
    return render_template('items.html', items=items, catagory=catagory)


@app.route('/catalog/<string:catagory_name>/<int:catagory_id>/item/new', methods=['GET', 'POST'])
def newItem(catagory_name,catagory_id):
    

    if request.method == 'POST':
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       catagory_id=catagory_id)
        session.add(newItem)
        session.commit()
        
        return redirect(url_for('viewitems',catagory_name= catagory_name, catagory_id=catagory_id))
    else:
        return render_template('item_new.html',catagory_name= catagory_name, catagory_id=catagory_id)

    return render_template('item_new.html', catagory_name= catagory_name, catagory_id=catagory_id)


@app.route('/catalog/<string:catagory_name>/<int:catagory_id>/item/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editItem(catagory_name,catagory_id, item_id):
   
    item = session.query(Item).filter_by(id=item_id).one()

    if request.method == 'POST':
        if request.form['name']:
            item.name = request.form['name']
        if request.form['description']:
            item.description = request.form['description']
        session.add(item)
        session.commit()
        
        return redirect(url_for('viewitems', catagory_id=catagory_id))
    else:
        return render_template('item_edit.html',
                               catagory_id=catagory_id,
                               item_id=item_id,
                               item=item)

@app.route('/catalog/<string:catagory_name>/<int:catagory_id>/item/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(catagory_name,catagory_id, item_id):
    
    item = session.query(Item).filter_by(id=item_id).one()


    if request.method == 'POST':
        session.delete(item)
        session.commit()
        
        return redirect(url_for('viewitems', catagory_name=catagory_name, catagory_id=catagory_id))
    else:
        return render_template('delete_item.html',
                               catagory_name=catagory_name,
                               catagory_id=catagory_id,
                               item=item)


if __name__ == '__main__':
    app.secret_key= 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)