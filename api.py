from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
from datetime import datetime
import json
import random
import os

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
    if request.args.get("error") is not None:
        return render_template('cart.html', page="cart", name=username, id=userID, tab=tab, error=request.args.get("error"))
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
        
        totalPrice = request.args.get("totalPrice")

        # Get the current date
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Load cart and order data
        with open('cart.json', 'r') as cart_file, open('order.json', 'r') as order_file:
            cart_data = json.load(cart_file)
            order_data = json.load(order_file)
        with open('user.json', 'r') as f:
            user = json.load(f)

    

        # Check if there is an existing order for the customer
        customer_id = session['id']
        existing_order = next((o for o in order_data if o['customer'] == customer_id), None)

        # If there is an existing order, add the cart to it
        if existing_order:
            existing_order['order'].append({
                'orderId': existing_order['order'][-1]['orderId'] + 1,
                'orderFood': cart_data,
                'status': 'pending',
                "total": totalPrice,
                "raating": "",
                "deliveryAddress": address,
                "orderDate": current_date,
                "deliveryPersonID": None
            })
        # If there is no existing order, create a new one
        else:
            order_data.append({
                'customer': customer_id,
                'order': [{
                    'orderId': 1,
                    'orderFood': cart_data,
                    'status': 'pending',
                    "total": totalPrice,
                    "raating": "",
                    "deliveryAddress": address,
                    "orderDate": current_date,
                    "deliveryPersonID": None
                }]
            })

        # Save the updated order data
        with open('order.json', 'w') as order_file:
            json.dump(order_data, order_file)

        # Clear the cart
        with open('cart.json', 'w') as cart_file:
            json.dump([], cart_file)

        # Redirect to the cart page
        return redirect(url_for('orderStatus'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/checkout')
def checkout():
    if not all(key in session for key in ['id', 'name', 'tab']) and session['tab'] != "customer":
        return redirect(url_for('login'))
    userID, username, tab = session['id'], session['name'], session['tab']
    with open('cart.json', 'r') as f:
        cart = json.load(f)
    with open('food.json', 'r') as f:
        foods = json.load(f)
    if cart is None or len(cart) == 0:
        return redirect(url_for('cart') + "?error=Please add food to cart")
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
    return render_template('checkout.html', page="checkout", name=session["name"], user_address=user_address, cart=cartFood, total_price=total_price, id=userID, tab=tab)


@app.route('/orderStatus')
def orderStatus():
    if not all(key in session for key in ['id', 'name', 'tab']):
        return redirect(url_for('login'))
    userID, username, tab = session['id'], session['name'], session['tab']
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
                    "total": 0,
                    "deliveryAddress": order["deliveryAddress"]
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
    return render_template('orderstatus.html', page="orderStatus", name=username, id=userID, tab=tab, orders=order, foods=food,
                                    orderFoods=orderfood)

@app.route('/user', methods=['GET', 'POST'])
def get_customer_by_id():
    with open('user.json', 'r') as f:
        data = json.load(f)
    customers = data[session["tab"]]
    for customer in customers:
        if customer["id"] == session['id']:
            if session['tab'] != "deliveryPersonnel":
                return render_template('user.html', tab=session['tab'], userName=customer["name"],
                                       id=customer["id"], userEmail=customer["email"], name=session["name"], userPhone=customer["phone"],
                                       userAddress=customer.get("address"))
            else:
                return render_template('user.html', tab=session['tab'], userName=customer["name"],
                                       id=customer["id"], userEmail=customer["email"], name=session["name"], userPhone=customer["phone"])
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
            return render_template('restaurantManagement.html', customers=user["customer"], foods=food,
                                   orderFoods=result, name=username, id=userID, tab=tab, page="restaurantManagement")
    return redirect(url_for('login'))

@app.route('/deliveryPersonnel', methods=['GET', 'POST'])
def deliveryPersonnel():
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
            "food": [],
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
                "orderDate": order["orderDate"],
                "total": order["total"],
                "deliveryPersonID": order["deliveryPersonID"]
            })

        result.append(customer_detail)
    return render_template('deliveryPersonnel.html', page="deliveryPersonnel", tab=session['tab'], id=session["id"], name=session["name"],
                                customers=user["customer"], foods=food, orderFoods=result)

@app.route('/getDelivery', methods=['GET', 'POST'])
def getDeliveryOrder():
    with open('food.json', 'r') as f:
        food = json.load(f)
    with open('order.json', 'r') as f:
        order = json.load(f)
    with open('user.json', 'r') as f:
        user = json.load(f)
    data = request.get_json()
    customerID = data['customerID']
    orderID = data['orderID']
    if request.method == 'POST':
        for customer_order in order:
            if customer_order["customer"] == customerID:
                for order_entry in customer_order["order"]:
                    if order_entry["orderId"] == orderID:
                        if order_entry["status"] == "getDelivery":
                            order_entry["status"] = "confirmed"
                            break
                        elif order_entry["status"] == "sentDelivery":
                            order_entry["status"] = "getDelivery"
                            break
    with open('order.json', 'w') as f:
        json.dump(order, f)
    return "Order status updated successfully"
    

@app.route('/setDelivery', methods=['GET', 'POST'])
def setDeliveryOrder():
    if request.method == 'POST':
        data = request.get_json()
        customerID = data['customerID']
        orderID = data['orderID']
        deliveryPersonID = data['deliveryPersonID']
        
        with open('order.json', 'r') as f:
            order = json.load(f)
        
        for customer_order in order:
            if customer_order["customer"] == customerID:
                for order_entry in customer_order["order"]:
                    if order_entry["orderId"] == orderID:
                        # Update the status of the order to "confirmed"
                        order_entry["status"] = "sentDelivery"
                        order_entry["deliveryPersonID"] = deliveryPersonID
        
        # Save the updated order back to the file
        with open('order.json', 'w') as f:
            json.dump(order, f)
        
        return jsonify({'message': 'Order has been assigned to the delivery person'})

@app.route('/deliveryOrder', methods=['GET', 'POST'])
def deliveryOrder():
    with open('order.json', 'r') as f:
        order = json.load(f)
    with open('food.json', 'r') as f:
        food = json.load(f)
    with open('user.json', 'r') as f:
        user = json.load(f)
    deliveryPerson = [user for user in user["deliveryPersonnel"]]
    if request.method == 'POST':
        print(request.form)
        print(request)
        for customer_order in order:
            if customer_order["customer"] == request.form["customerID"]:
                for order_entry in customer_order["order"]:
                    if order_entry["orderId"] == request.form["orderID"]:
                        # Update the status of the order to "confirmed"
                        order_entry["status"] = "sentDelivery"
                        order_entry["deliveryPersonID"] = request.form["deliveryPersonID"]
    # Save the updated order back to the file
        with open('order.json', 'w') as f:
            json.dump(order, f)
        return "Order has been assigned to the delivery person"
    elif request.method == 'GET':
        order_id = request.args.get("orderId")
        for customer_order in order:
            if customer_order["customer"] == request.args.get("userId"):
                for order_entry in customer_order["order"]:
                    if order_entry["orderId"] == int(order_id):
                        food_list = []
                        for order_food in order_entry["orderFood"]:
                            for food_id, quantity in order_food.items():
                                food_list.append({
                                    "foodId": int(food_id),
                                    "quantity": quantity
                                })
                        order_entry["orderFood"] = food_list
                        return render_template('setDeliveryOrder.html', page="deliveryOrder", tab=session['tab'], id=session["id"], name=session["name"],
                                orderId=order_id, foods=food, order=order_entry, deliveryPersons=deliveryPerson, message=request.args.get("message"), customer=request.args.get("userId"))
    return redirect(url_for('restaurantManagement'))

@app.route('/confirmOrder', methods=['GET', 'POST'])
def confirmOrder():
    if 'tab' in session:
        userID = session['id']
    with open('order.json', 'r') as f:
        order = json.load(f)

    deliveryPersonID = request.args.get("deliveryPersonID")
    order_id = request.args.get("orderId")

    # Find the order with the given order_id
    for customer_order in order:
        if customer_order["customer"] == request.args.get("userId"):
            for order_entry in customer_order["order"]:
                if order_entry["orderId"] == int(order_id):
                    # Update the status of the order to "confirmed"
                    order_entry["status"] = "delivery"
                    order_entry["deliveryPersonID"] = deliveryPersonID
                    break
    
    # Save the updated order back to the file
    with open('order.json', 'w') as f:
        json.dump(order, f)
    
    # Return a response indicating the order has been confirmed
    return redirect(url_for('restaurantManagement'))

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
                    "total": 0,
                    "orderDate": order["orderDate"],
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

@app.route('/modifyMenuItems', methods=['GET', 'POST'])
def modifyMenuItems():
    message = request.args.get("message")
    with open('food.json', 'r') as f:
        food = json.load(f)
    return render_template('modifyMenuItems.html', page="modifyOrder", tab=session['tab'], id=session["id"], name=session["name"], foods=food, message=message)

@app.route('/modifyFoodItem', methods=['GET', 'POST'])

def modifyFoodItems():
    with open('food.json', 'r') as f:
        foods = json.load(f)
    if request.method == 'POST':
        image = None
        print(request.form)
        for food in foods:
            if food['id'] == int(request.form['foodId']):
                food['name'] = request.form['foodName']
                food['category'] = request.form['foodCategory']
                food['price'] = request.form['foodPrice']
                if 'image' in request.files:
                    image = food["image"]
                    food["image"] = request.files['image'].filename
                food['description'] = request.form['foodDescription']
                break
        with open('food.json', 'w') as f:
            json.dump(foods, f)
        if 'image' in request.files:
            # Save the uploaded image to a specific directory
            request.files['image'].save('image/' + request.files['image'].filename)
            # Remove the old image file
            # os.remove('image/' + image)
        return "Food item updated successfully"

@app.route('/addFoodItem', methods=['GET', 'POST'])
def addFoodItem():
    if request.method == 'POST':
        with open('food.json', 'r') as f:
            foods = json.load(f)
        food = {
            "id": len(foods) + 1,
            "name": request.form['foodName'],
            "category": request.form['foodCategory'],
            "price": request.form['foodPrice'],
            "description": request.form['foodDescription'],
            "image": request.files['image'].filename,  # Get the filename of the uploaded image
            "inStock": 1,
            "restaurant": request.form['restaurant']
        }
        foods.append(food)
        with open('food.json', 'w') as f:
            json.dump(foods, f)
        if 'image' in request.files:
            # Save the uploaded image to a specific directory
            request.files['image'].save('image/' + request.files['image'].filename)
        return redirect(url_for('addFoodItem')+"?message=Food item added successfully")
    else:
        return render_template('addFoodItem.html', page="modifyOrder", tab=session['tab'], id=session["id"], name=session["name"], message=request.args.get("message"))

@app.route('/deleteFoodItem', methods=['GET', 'POST'])
def deleteFoodItem():
    with open('food.json', 'r') as f:
        foods = json.load(f)
    for food in foods:
        if food['id'] == int(request.form['foodId']):
            foods.remove(food)
            break
    with open('food.json', 'w') as f:
        json.dump(foods, f)
    with open('cart.json', 'w') as f:
        json.dump([], f)
    return "Food item deleted successfully"

if __name__ == '__main__':
    app.run(debug=True)