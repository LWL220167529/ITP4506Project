from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
import json
    
app = Flask(__name__, template_folder='templates')
app.secret_key = 'id'
app.secret_key = 'name'
app.secret_key = 'tab'
CORS(app)

@app.route('/login/<string:user>', methods=['GET', 'POST'])
def customerLogin(user):
    print(request)
    if request.method == 'POST':
        with open('user.json', 'r') as f:
            data = json.load(f)
        for customer in data[user]:
            if customer['id'] == request.form['email'] or customer['email'] == request.form['email'] and customer['password'] == request.form['password']:
                session['id'] = customer['id']
                session['name'] = customer['name']
                session['tab'] = user
                return redirect(url_for('home'))
        return render_template('login.html')
    else:
        return render_template('login.html')

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
        return render_template('YummyRestaurant.html', data=data[:6], page="home") # display first 5 data
    else:
        userID = session['id']  # get user dictionary from session
        username = session['name']  # get user dictionary from session
        tab = session['tab']  # get user dictionary from session
        return render_template('YummyRestaurant.html', data=data[:6], name=username, id=userID, tab=tab, page="home") # display first 5 data


@app.route('/page/<int:page>')
def page_home(page):
    page *= 6
    with open('food.json', 'r') as f:
        data = json.load(f)
    if 'id' and 'name' and 'tab' not in session:
        return render_template('YummyRestaurant.html', data=data[page:page+6], page="home")
    else:
        userID = session['id']  # get user dictionary from session
        username = session['name']  # get user dictionary from session
        tab = session['tab']  # get user dictionary from session
        return render_template('YummyRestaurant.html', data=data[page:page+6], name=username, id=userID, tab=tab, page="home")
    
@app.route('/search/<string:search>/<int:page>')
def search_home(search, page):
    if page == 1 or page == None:
        page = 0
    else:
        page *= 6
    food = search_food(search)
    if 'id' and 'name' and 'tab' not in session:
        return render_template('YummyRestaurant.html', data=food[page:page+6], search=search, page="home")
    else:
        userID = session['id']  # get user dictionary from session
        username = session['name']  # get user dictionary from session
        tab = session['tab']  # get user dictionary from session
        return render_template('YummyRestaurant.html', data=food[page:page+6], name=username, id=userID, tab=tab, search=search, page="home")
    
def search_food(keyword):
        results = []
        with open('food.json', 'r') as f:
            data = json.load(f)
        for food in data:
            if keyword.lower() in food['name'].lower() or keyword.lower() in food['category'].lower():
                results.append(food)
        return results

@app.route('/savefood', methods=['GET', 'POST'])
def savefood():
    data = json.loads(request.data)
    id = data['id']
    quantity = data['quantity']
    with open('cart.json', 'r') as f:
        itemInCart = json.load(f)
    cart = []
    for item in itemInCart:
        cart.append(item)
    data = {
        id: quantity
    }
    cart.append(data)
    # open a file for writing
    with open('cart.json', 'w') as f:
        # write the list to the file in JSON format
        json.dump(cart, f)
    return jsonify({'mas': 'success'})

@app.route('/user')
def get_customer_by_id():
    print(session['id'])
    with open('user.json', 'r') as f:
        data = json.load(f)
    customers = data["customer"]
    for customer in customers:
        if customer["id"] == session['id']:
            return render_template('user.html', tab=session['tab'], customerName=customer["name"], id=customer["id"], customerEmail=customer["email"], customerPhone=customer["phone"], customerAddress=customer["address"])
    return jsonify({"error": "Customer not found"})


if __name__ == '__main__':
    app.run(debug=True)