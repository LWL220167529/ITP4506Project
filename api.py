from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
import json

app = Flask(__name__, template_folder='templates', static_folder='image')
app.secret_key = 'id'
app.secret_key = 'name'
app.secret_key = 'tab'
CORS(app)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        with open('user.json', 'r') as f:
            data = json.load(f)
        for customer in data[request.form['user']]:
            if customer['id'] == request.form['email'] or customer['email'] == request.form['email'] and customer['password'] == request.form['password']:
                session['id'] = customer['id']
                session['name'] = customer['name']
                session['tab'] = request.form['user']
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
    page_count = len(data) // 6
    if 'id' and 'name' and 'tab' not in session:
        # display first 5 data
        return render_template('YummyRestaurant.html', data=data[:6], page="home", dataPage=page_count)
    else:
        userID = session['id']  # get user dictionary from session
        username = session['name']  # get user dictionary from session
        tab = session['tab']  # get user dictionary from session
        return render_template('YummyRestaurant.html', data=data[:6], name=username, id=userID,
                               tab=tab, page="home", dataPage=page_count)  # display first 5 data


@app.route('/page/<int:page>')
def page_home(page):
    page *= 6
    with open('food.json', 'r') as f:
        data = json.load(f)
    page_count = len(data) // 6
    if 'id' not in session:
        return render_template('YummyRestaurant.html', data=data[page:page+6], page="home", dataPage=page_count)
    else:
        userID = session['id']  # get user dictionary from session
        username = session['name']  # get user dictionary from session
        tab = session['tab']  # get user dictionary from session
        return render_template('YummyRestaurant.html', data=data[page:page+6], name=username, id=userID, tab=tab,
                               page="home", dataPage=page_count)


@app.route('/search/<string:search>/<int:page>')
def search_home(search, page):
    if page == 1 or page == None:
        page = 0
    else:
        page *= 6
    food = search_food(search)
    page_count = len(food) // 6
    if 'id' and 'name' and 'tab' not in session:
        return render_template('YummyRestaurant.html', data=food[page:page+6], search=search, page="home", dataPage=page_count)
    else:
        userID = session['id']  # get user dictionary from session
        username = session['name']  # get user dictionary from session
        tab = session['tab']  # get user dictionary from session
        return render_template('YummyRestaurant.html', data=food[page:page+6], name=username, id=userID, tab=tab,
                               search=search, page="home", dataPage=page_count)


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
    try:
        data = json.loads(request.data)
        id = str(data['id'])  # convert id to integer
        quantity = data['quantity']
        with open('cart.json', 'r') as f:
            itemInCart = json.load(f)
        for item in itemInCart:
            if id in item:
                item[id] = str(int(item[id]) + int(quantity))
                break
        else:
            itemInCart.append({id: quantity})
        # open a file for writing
        with open('cart.json', 'w') as f:
            # write the list to the file in JSON format
            json.dump(itemInCart, f)
        return jsonify({'message': 'success'})
    except:
        return jsonify({'error': 'Please login first'})


@app.route('/cartSubmit')
def cartSubmit():
    with open('cart.json', 'r') as f:
        cart = json.load(f)
    if 'id' and 'name' and 'tab' not in session:
        return render_template('cart.html', cart=cart, page="cart")
    else:
        userID = session['id']
        with open('order.json', 'r') as f:
            order = json.load(f)
        # add cart to existing order
        for userID in order:
            if userID["customer"] == session['id']:
                for orderID in order["order"]:
                    orderID.append({
                        "orderId": order[-1]['orderId'],
                        "orderFood": [cart],
                        "status": "pending"
                    })
        else:
            order.append({session['id']: {"orderId": 1, "order": {cart}}})


@app.route('/user', methods=['GET', 'POST'])
def get_customer_by_id():
        with open('user.json', 'r') as f:
            data = json.load(f)
        customers = data[session["tab"]]
        for customer in customers:
            if session['tab'] != "deliveryPersonnel":
                if customer["id"] == session['id']:
                    return render_template('user.html', tab=session['tab'], userName=customer["name"],
                                           id=customer["id"], userEmail=customer["email"], userPhone=customer["phone"],
                                             userAddress=customer["address"])
            else:
                if customer["id"] == session['id']:
                    return render_template('user.html', tab=session['tab'], userName=customer["name"],
                                           id=customer["id"], userEmail=customer["email"], userPhone=customer["phone"])
        return jsonify({"error": "Customer not found"})


@app.route('/editProfile', methods=['POST'])
def editUser():
    try:
        if 'id' not in session:
            return redirect(url_for('login'))
        data = json.loads(request.data)
        user = data['user']
        id = data['id']
        userName = data['userName']
        userEmail = data['userEmail']
        userPhone = data['userPhone']

        with open('user.json', 'r') as f:
            data = json.load(f)
        for editUser in data[user]:
            if editUser['id'] == id:
                editUser['name'] = userName
                editUser['email'] = userEmail
                editUser['phone'] = userPhone
                if user != "deliveryPersonnel":
                    userAddress = data['userAddress']
                    editUser['address'] = userAddress
        with open('user.json', 'w') as f:
            json.dump(data, f)

        return jsonify({'message': 'User updated successfully'})
    except:
        return jsonify({'error': 'Something went wrong'})


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print(request.form['user'])
        if request.form['user'] != 'deliveryPersonnel':
            with open('user.json', 'r') as f:
                data = json.load(f)
            new_user = {
                "id": request.form['id'],
                "name": request.form['name'],
                "email": request.form['email'],
                "phone": request.form['phone'],
                "address": request.form['address'],
                "password": request.form['password']
            }
            data[request.form['user']].append(new_user)
            with open('user.json', 'w') as f:
                json.dump(data, f)
        else:
            with open('user.json', 'r') as f:
                data = json.load(f)
            new_user = {
                "id": request.form['id'],
                "name": request.form['name'],
                "email": request.form['email'],
                "phone": request.form['phone'],
                "password": request.form['password']
            }
            data[request.form['user']].append(new_user)
            with open('user.json', 'w') as f:
                json.dump(data, f)
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/restaurantManagement')
def restaurantManagement():
    if 'tab' in session:
        userID = session['id']  # get user dictionary from session
        username = session['name']  # get user dictionary from session
        tab = session['tab']  # get user dictionary from session
        if tab == "restaurant":
            with open('food.json', 'r') as f:
                food = json.load(f)
            with open('order.json', 'r') as f:
                order = json.load(f)
            with open('user.json', 'r') as f:
                user = json.load(f)
            return render_template('restaurantManagement.html', customers=user["customer"], orders=order, foods=food, name=username, id=userID,
                                   tab=tab, page="restaurantManagement")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
