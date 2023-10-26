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
        return render_template('login.html', error="Invalid email or password")
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


@app.route('/cart')
def cart():
    if not all(key in session for key in ['id', 'name', 'tab']):
        return redirect(url_for('login'))
    userID, username, tab = session['id'], session['name'], session['tab']
    with open('cart.json', 'r') as f:
        cart = json.load(f)
    with open('food.json', 'r') as f:
        foods = json.load(f)
    cartFood = [{"id": food['id'], "name": food['name'], "quantity": quantity, "price": food['price']}
                for foodCart in cart
                for foodId, quantity in foodCart.items()
                for food in foods
                if int(food['id']) == int(foodId)]
    return render_template('cart.html', page="cart", cart=cartFood, name=username, id=userID, tab=tab)

@app.route('/editCart', methods=['GET','POST'])
def editCart():
    with open('cart.json', 'r') as f:
        cart = json.load(f)
    id = request.args.get("id")
    quantity = request.args.get("quantity")
    action = request.args.get("action")
    if action == "edit":
        for item in cart:
            if id in item:
                item[id] = quantity
                break
        with open('cart.json', 'w') as f:
            json.dump(cart, f)
    elif action == "delete":
        cart = [item for item in cart if id not in item]
        with open('cart.json', 'w') as f:
            json.dump(cart, f)
    return redirect(url_for('cart'))

@app.route('/clearCart', methods=['GET', 'POST'])
def clearCart():
    with open('cart.json', 'w') as f:
        json.dump([], f)
    return redirect(url_for('cart'))

@app.route('/cartSubmit', methods=['GET','POST'])
def cart_submit():
    try:
        address = request.args.get("address")
        # Load cart and order data
        with open('cart.json', 'r') as cart_file, open('order.json', 'r') as order_file:
            cart_data = json.load(cart_file)
            order_data = json.load(order_file)

        # Check if there is an existing order for the customer
        customer_id = session['id']
        existing_order = next((o for o in order_data if o['customer'] == customer_id), None)

        # If there is an existing order, add the cart to it
        if existing_order:
            existing_order['order'].append({
                'orderId': existing_order['order'][-1]['orderId'] + 1,
                'orderFood': cart_data,
                'status': 'pending',
                "raating": "",
                "deliveryAddress": address
            })
        # If there is no existing order, create a new one
        else:
            order_data.append({
                'customer': customer_id,
                'order': [{
                    'orderId': 1,
                    'orderFood': cart_data,
                    'status': 'pending',
                    "raating": "",
                    "deliveryAddress": address
                }]
            })

        # Save the updated order data
        with open('order.json', 'w') as order_file:
            json.dump(order_data, order_file)

        # Clear the cart
        with open('cart.json', 'w') as cart_file:
            json.dump([], cart_file)

        # Redirect to the cart page
        return redirect(url_for('home'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/checkout')
def checkout():
    if not all(key in session for key in ['id', 'name', 'tab']):
        return redirect(url_for('login'))
    userID, username, tab = session['id'], session['name'], session['tab']
    with open('cart.json', 'r') as f:
        cart = json.load(f)
    with open('food.json', 'r') as f:
        foods = json.load(f)
    cartFood = [{"id": food['id'], "name": food['name'], "quantity": int(quantity), "price": float(food['price'])}
                for foodCart in cart
                for foodId, quantity in foodCart.items()
                for food in foods
                if int(food['id']) == int(foodId)]
    total_price = sum([item['price'] * item['quantity'] for item in cartFood])
    with open('user.json', 'r') as f:
        data = json.load(f)
    customers = data[session["tab"]]
    for customer in customers:
        if customer["id"] == session['id']:
            user_address = customer.get("address")
            break
    return render_template('checkout.html', page="checkout", user_address=user_address, cart=cartFood, total_price=total_price)


@app.route('/user', methods=['GET', 'POST'])
def get_customer_by_id():
    with open('user.json', 'r') as f:
        data = json.load(f)
    customers = data[session["tab"]]
    for customer in customers:
        if customer["id"] == session['id']:
            if session['tab'] != "deliveryPersonnel":
                return render_template('user.html', tab=session['tab'], userName=customer["name"],
                                       id=customer["id"], userEmail=customer["email"], userPhone=customer["phone"],
                                       userAddress=customer.get("address"))
            else:
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
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            user_type = request.form['user']
            user_data = {
                "id": request.form['id'],
                "name": request.form['name'],
                "email": request.form['email'],
                "phone": request.form['phone'],
                "password": request.form['password']
            }
            if user_type != 'deliveryPersonnel':
                user_data["address"] = request.form['address']
            with open('user.json', 'r') as f:
                data = json.load(f)
            data[user_type].append(user_data)
            with open('user.json', 'w') as f:
                json.dump(data, f)
            return redirect(url_for('login'))
        except Exception as e:
            return jsonify({'error': str(e)})
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
            result = []

            for order_entry in order:
                customer_detail = {
                    "customer": order_entry["customer"],
                    "food": []
                }

                for order in order_entry["order"]:
                    food_list = []

                    for order_food in order["orderFood"]:
                        for food_id, quantity in order_food.items():
                            food_list.append({
                                "foodId": int(food_id),
                                "quantity": quantity
                            })

                    customer_detail["food"].append({
                        "orderId": order["orderId"],
                        "orderFood": food_list,
                        "status": order["status"],
                        "raating": order["raating"],
                        "total": order["total"]
                    })

                result.append(customer_detail)
            print(result)
            return render_template('restaurantManagement.html', customers=user["customer"], foods=food,
                                   orderFoods=result, name=username, id=userID, tab=tab, page="restaurantManagement")
    return redirect(url_for('login'))

@app.route('/history')
def history():
    userID = session['id']  # get user dictionary from session
    username = session['name']  # get user dictionary from session
    tab = session['tab']  # get user dictionary from session
    with open('food.json', 'r') as f:
        food = json.load(f)
    with open('order.json', 'r') as f:
        order = json.load(f)
    orderfood = []
    for customer_order in order:
        if str(customer_order["customer"]) == str(username):
            for order in customer_order["order"]:
                order_details = {
                    "orderId": order["orderId"],
                    "food": [],
                    "status": order["status"],
                    "total": 0
                }
                for order_food in order["orderFood"]:
                    food_id, quantity = list(order_food.items())[0]
                    food_price = next((item for item in food if item["id"] == int(food_id)), None)["price"]
                    order_details["food"].append({
                        "foodId": int(food_id),
                        "quantity": quantity,
                        "price": float(food_price) # convert price to float
                    })
                    order_details["total"] += float(food_price) * int(quantity) # convert price to float
                orderfood.append(order_details)
    return render_template('orderhistory.html', name=username, id=userID, tab=tab, orders=order, foods=food,
                                    orderFoods=orderfood, page="history")

if __name__ == '__main__':
    app.run(debug=True)
