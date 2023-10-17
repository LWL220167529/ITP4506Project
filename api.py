from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
import json
    
app = Flask(__name__, template_folder='templates')
app.secret_key = 'id' # set your secret key here
app.secret_key = 'name' # set your secret key here

CORS(app)
@app.route('/login', methods=['GET', 'POST'])
def customerLogin():
    if request.method == 'POST':
        with open('user.json', 'r') as f:
            data = json.load(f)
        for customer in data["customer"]:
            if customer['id'] == request.form['email'] or customer['email'] == request.form['email'] and customer['password'] == request.form['password']:
                session['id'] = customer['id']
                session['name'] = customer['name']
                session['tab'] = 'customer'
                return redirect(url_for('home'))
        return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/login/restaurant', methods=['GET', 'POST'])
def restaurantLogin():
    if request.method == 'POST':
        with open('user.json', 'r') as f:
            data = json.load(f)
        for customer in data["restaurant"]:
            if customer['id'] == request.form['email'] or customer['email'] == request.form['email'] and customer['password'] == request.form['password']:
                session['id'] = customer['id']
                session['name'] = customer['name']
                session['tab'] = 'restaurant'
                return redirect(url_for('home'))
        return render_template('loginRestaurant.html')
    else:
        return render_template('loginRestaurant.html')

@app.route('/login/deliveryPersonnel', methods=['GET', 'POST'])
def deliveryPersonnelLogin():
    if request.method == 'POST':
        with open('user.json', 'r') as f:
            data = json.load(f)
        for customer in data["restaurant"]:
            if customer['id'] == request.form['email'] or customer['email'] == request.form['email'] and customer['password'] == request.form['password']:
                session['id'] = customer['id']
                session['name'] = customer['name']
                session['tab'] = 'deliveryPersonnel'
                return redirect(url_for('home'))
        return render_template('loginDeliveryPersonnel.html')
    else:
        return render_template('loginDeliveryPersonnel.html')

@app.route('/logout')
def logout():
    session.pop('id', None)
    session.pop('name', None)
    session.pop('tab', None)
    return redirect(url_for('home'))

@app.route('/')
def home():
    with open('food.json', 'r') as f:
        data = json.load(f)
    
    if 'id' and 'name' and 'tab' not in session:
        return render_template('YummyRestaurant.html', data=data[:6]) # display first 5 data
    else:
        userID = session['id']  # get user dictionary from session
        username = session['name']  # get user dictionary from session
        tab = session['tab']  # get user dictionary from session
        return render_template('YummyRestaurant.html', data=data[:6], name=username, id=userID, tab=tab) # display first 5 data


@app.route('/page/<int:page>')
def page_home(page):
    page *= 6
    with open('food.json', 'r') as f:
        data = json.load(f)
    if 'id' and 'name' and 'tab' not in session:
        return render_template('YummyRestaurant.html', data=data[page:page+6])
    else:
        userID = session['id']  # get user dictionary from session
        username = session['name']  # get user dictionary from session
        tab = session['tab']  # get user dictionary from session
        return render_template('YummyRestaurant.html', data=data[page:page+6], name=username, id=userID, tab=tab)
    
@app.route('/savefood', methods=['POST'])
def savefood():
    data = json.loads(request.data)
    id = data['id']
    quantity = data['quantity']
    if int(quantity) == 0:
        return jsonify({'error': 'Please enter a quantity'})
    if session['food'][id] is None:
        session['food'] = [{id: int(quantity)}]
    elif id in session['food']:
        session['food'][id] += int(quantity)
    else:
        session['food'].append({id: int(quantity)})
    return jsonify({'message': 'success'})

        
if __name__ == '__main__':
    app.run(debug=True)