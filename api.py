from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
import json
from customer import Customer
from user import User
from restaurant import Restaurant
from deliveryPersonnel import DeliveryPersonnel

class main:
    app = Flask(__name__, template_folder='templates')
    app.secret_key = 'user' # set your secret key here
    user = None
    CORS(app)

    @app.route('/')
    def home(user=None):
        user = session.get('user')
        with open('food.json', 'r') as f:
            data = json.load(f)
        if user is None:
            return render_template('YummyRestaurant.html', data=data)
        else:
            return render_template('YummyRestaurant.html', data=data)


    @app.route('/login', methods=['GET', 'POST'])
    def customerLogin():
        if request.method == 'POST':
            with open('user.json', 'r') as f:
                data = json.load(f)
            for customer in data["customer"]:
                if customer['id'] == request.form['email'] or customer['email'] == request.form['email'] and customer['password'] == request.form['password']:
                    user = Customer(customer['name'], customer['email'], customer['id'], customer['password'], customer['address'])
                    session['user'] = user
                return redirect(url_for('home'), user=user)
        else:
            return render_template('login.html')

    if __name__ == '__main__':
        app.run(debug=True)
