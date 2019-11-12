# Catalog project for Udacity

from flask import Flask, make_response, render_template
from flask import request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Catagory, Item

from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += ''
    flash("you are now logged in as %s" % login_session['username'])
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % login_session['access_token'])
    h = httplib2.Http()
    result = \
        h.request(uri=url, method='POST', body=None,
                   headers={'content-type':'application/x-www-form-urlencoded'})[0]

    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Successfully logged out")
        return redirect(url_for('catalog'))
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/catalog/user/JSON')
def userJSON():
    user = session.query(User).all()
    return jsonify(User=[i.serialize for i in user])


@app.route('/catalog/JSON')
def catagoryJSON():
    catagory = session.query(Catagory).all()
    return jsonify(Catagory=[i.serialize for i in catagory])


@app.route("/catalog/<string:catagory_name>/<int:catagory_id>/"
           "<string:item_name>/<int:item_id>/JSON")
def itemJSON(catagory_name, item_name, catagory_id, item_id):
    equipment = session.query(Item).filter_by(name=item_name).one()
    return jsonify(Item=[equipment.serialize])


@app.route('/')
@app.route('/catalog')
def catalog():
    catalog = session.query(Catagory).all()
    items = session.query(Item).all()
    if 'username' not in login_session:
        return render_template('public_homecatalog.html', catalog=catalog,
                               items=items)
    else:
        return render_template('homecatalog.html', catalog=catalog,
                               items=items)


@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCategory():

    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        newCatagory = Catagory(name=request.form['name'],
                               user_id=login_session['user_id'])
        session.add(newCatagory)
        session.commit()
        flash("new catagory has been created")
        return redirect(url_for('catalog'))
    else:
        return render_template('new_catagory.html')


@app.route('/catalog/<string:catagory_name>/<int:catagory_id>/edit/',
           methods=['GET', 'POST'])
def editCatagory(catagory_name, catagory_id):

    catagory = session.query(Catagory).filter_by(id=catagory_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if catagory.user_id != login_session['user_id']:
        flash("You are not authorised to delete this")
        return redirect(url_for('catalog'))

    if request.method == 'POST':
        if request.form['name']:
            catagory.name = request.form['name']
        session.add(catagory)
        session.commit()
        flash("Catalog has been edited")
        return redirect(url_for('catalog'))
    else:
        return render_template('edit_category.html', catagory=catagory)


@app.route('/catalog/<string:catagory_name>/<int:catagory_id>/delete/',
           methods=['GET', 'POST'])
def deleteCatagory(catagory_name, catagory_id):

    catagory = session.query(Catagory).filter_by(id=catagory_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if catagory.user_id != login_session['user_id']:
        flash("You are not authorised to delete this")
        return redirect(url_for('catalog'))

    if request.method == 'POST':
        session.delete(catagory)
        session.commit()
        flash("catagory has been deleted")
        return redirect(url_for('catalog'))
    else:
        return render_template('delete_catagory.html', catagory=catagory)


@app.route('/catalog/<string:catagory_name>/<int:catagory_id>')
@app.route('/catalog/<string:catagory_name>/<int:catagory_id>/item/')
def viewitems(catagory_name, catagory_id):
    catagory = session.query(Catagory).filter_by(id=catagory_id).one()
    items = session.query(Item).filter_by(catagory_id=catagory_id)
    creator = getUserInfo(catagory.user_id)

    if ('username' not in login_session or
       creator.id != login_session['user_id']):
            return render_template('public_items.html', items=items,
                                   catagory=catagory)
    else:
        return render_template('items.html', items=items, catagory=catagory)


@app.route('/catalog/<string:catagory_name>/<int:catagory_id>/item/new',
           methods=['GET', 'POST'])
def newItem(catagory_name, catagory_id):

    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       catagory_id=catagory_id,
                       user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash("New item added!")
        return redirect(url_for('viewitems', catagory_name=catagory_name,
                                catagory_id=catagory_id))
    else:
        return render_template('item_new.html', catagory_name=catagory_name,
                               catagory_id=catagory_id)

    return render_template('item_new.html', catagory_name=catagory_name,
                           catagory_id=catagory_id)


@app.route("/catalog/<string:catagory_name>/<int:catagory_id>/item/"
           "<int:item_id>/edit", methods=['GET', 'POST'])
def editItem(catagory_name, catagory_id, item_id):

    item = session.query(Item).filter_by(id=item_id).one()

    if 'username' not in login_session:
        return redirect('/login')
    if item.user_id != login_session['user_id']:
        flash("You are not authorised to delete this")
        return redirect(url_for('viewitems', catagory_name=catagory_name,
                                catagory_id=catagory_id))

    if request.method == 'POST':
        if request.form['name']:
            item.name = request.form['name']
        if request.form['description']:
            item.description = request.form['description']
        session.add(item)
        session.commit()
        flash("item has been edited")
        return redirect(url_for('viewitems', catagory_name=catagory_name,
                                catagory_id=catagory_id))
    else:
        return render_template('item_edit.html', catagory_id=catagory_id,
                               catagory_name=catagory_name,
                               item_id=item_id, item=item)


@app.route('/catalog/<string:catagory_name>/<int:catagory_id>'
           '/item/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteItem(catagory_name, catagory_id, item_id):

    item = session.query(Item).filter_by(id=item_id).one()

    if 'username' not in login_session:
        return redirect('/login')
    if item.user_id != login_session['user_id']:
        flash("You are not authorised to delete this")
        return redirect(url_for('viewitems', catagory_name=catagory_name,
                                catagory_id=catagory_id))

    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("Item has been deleted")
        return redirect(url_for('viewitems', catagory_name=catagory_name,
                                catagory_id=catagory_id))
    else:
        return render_template('delete_item.html',
                               catagory_name=catagory_name,
                               catagory_id=catagory_id,
                               item=item)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000, threaded=False)
