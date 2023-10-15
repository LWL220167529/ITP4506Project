from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

def databaseConnect():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="itp4506"
    )

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/login', methods=['POST'])
def login():
    with databaseConnect() as db:
        cursor = db.cursor()
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        query = 'SELECT COUNT(*) FROM user WHERE userName = %s OR email = %s'
        values = (username, username)
        cursor.execute(query, values)
        count = cursor.fetchone()[0]
        if count == 1:
            query = 'SELECT password, userID FROM user WHERE userName = %s OR email = %s'
            cursor.execute(query, values)
            result = cursor.fetchone()
            if result and (result[0] == password):
                return jsonify({'message': 'Login successful!', 'login': True, 'id': result[1]})
        return jsonify({'message': 'Invalid username or password.', 'login': False})

@app.route('/getItem', methods=['GET'])
def getItem():
    try:
        with databaseConnect() as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM item")
            results = cursor.fetchall()
            items = []
            for result in results:
                item = {
                    'id': result[0],
                    'name': result[1],
                    'stock': result[2],
                    'description': result[3],
                    'category': result[4],
                    'price': result[5],
                    'image': result[6]
                }
                items.append(item)
            return jsonify(items), 200
    except mysql.connector.Error as error:
        print(error)
        return jsonify({'message': 'Internal server error'}), 500
    
@app.route('/getUser/<string:id>')
def getUser(id):
    try:
        if (id != None):
            with databaseConnect() as db:
                cursor = db.cursor()
                query = 'SELECT * FROM user WHERE userID = %s'
                cursor.execute(query, (id,))
                results = cursor.fetchall()
                if len(results) > 0:
                    user = {'id': results[0][0], 'name':results[0][1], 'email':results[0][2], 'createTime':results[0][5]}
                    return jsonify({'get': True},user), 200
                else:
                    return jsonify({'get': False}), 404
        else:
            return jsonify({'get': False}), 404
    except mysql.connector.Error as error:
        print(error)
        return jsonify({'message': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
