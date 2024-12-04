from flask import Flask, request, jsonify
from db_config import db, init_db
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
init_db(app)
app.config['SECRET_KEY'] = "222222222233333333"

class User(db.Model):
    """
    Represents a user in the database.

    :param full_name: Full name of the user
    :type full_name: str
    :param username: Unique username (acts as primary key)
    :type username: str
    :param password: Hashed password of the user
    :type password: str
    :param isadmin: Indicates whether the user is an administrator (default: False)
    :type isadmin: bool
    :param age: Age of the user
    :type age: int
    :param address: Address of the user
    :type address: str
    :param gender: Gender of the user
    :type gender: str
    :param marital_status: Marital status of the user
    :type marital_status: str
    :param wallet_balance: Wallet balance of the user (default: 0.0)
    :type wallet_balance: float
    """
    __tablename__ = 'User'
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), primary_key=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    isadmin = db.Column(db.Boolean, default=False)
    age = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    marital_status = db.Column(db.String(10), nullable=False)
    wallet_balance = db.Column(db.Float, default=0.0)

@app.route('/customers/new', methods=['POST'])
def register_customer():
    """
    Registers a new customer in the system.

    :return: JSON response with a success or error message
    :rtype: flask.Response
    """
    data = request.get_json()
    required_fields = ['full_name', 'username', 'password', 'age', 'address', 'gender', 'marital_status']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already taken'}), 400

    if len(data['password']) < 8 or not any(char.isdigit() for char in data['password']):
        return jsonify({'error': 'Password must be at least 8 characters long and contain a number.'}), 400

    hashed_password = generate_password_hash(data['password'])

    new_customer = User(
        full_name=data['full_name'],
        username=data['username'],
        password=hashed_password,
        age=data['age'],
        address=data['address'],
        gender=data['gender'],
        marital_status=data['marital_status']
    )
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({'message': 'Customer registered successfully'}), 201

@app.route('/customers/<string:username>', methods=['DELETE'])
def delete_customer(username):
    """
    Deletes a customer from the system.

    :param username: The username of the customer to delete
    :type username: str
    :return: JSON response with a success or error message
    :rtype: flask.Response
    """
    customer = User.query.filter_by(username=username).first()
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': 'Customer deleted successfully'}), 200

@app.route('/customers/<string:username>', methods=['PUT'])
def update_customer(username):
    """
    Updates customer details.

    :param username: The username of the customer to update
    :type username: str
    :return: JSON response with a success or error message
    :rtype: flask.Response
    """
    customer = User.query.filter_by(username=username).first()
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    data = request.get_json()
    for field in ['full_name', 'password', 'age', 'address', 'gender', 'marital_status']:
        if field in data:
            if field == 'password':
                data[field] = generate_password_hash(data[field])
            setattr(customer, field, data[field])

    db.session.commit()
    return jsonify({'message': 'Customer updated successfully'}), 200

@app.route('/customers', methods=['GET'])
def get_all_customers():
    """
    Retrieves all customers.

    :return: JSON response with a list of all customers
    :rtype: flask.Response
    """
    customers = User.query.all()
    output = []
    for customer in customers:
        customer_data = {
            'full_name': customer.full_name,
            'username': customer.username,
            'age': customer.age,
            'address': customer.address,
            'gender': customer.gender,
            'marital_status': customer.marital_status,
            'wallet_balance': customer.wallet_balance
        }
        output.append(customer_data)
    return jsonify({'customers': output}), 200

@app.route('/customers/<string:username>', methods=['GET'])
def get_customer(username):
    """
    Retrieves details of a specific customer.

    :param username: The username of the customer to retrieve
    :type username: str
    :return: JSON response with customer details or an error message
    :rtype: flask.Response
    """
    customer = User.query.filter_by(username=username).first()
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    customer_data = {
        'full_name': customer.full_name,
        'username': customer.username,
        'age': customer.age,
        'address': customer.address,
        'gender': customer.gender,
        'marital_status': customer.marital_status,
        'wallet_balance': customer.wallet_balance
    }
    return jsonify({'customer': customer_data}), 200

@app.route('/customers/<string:username>/charge', methods=['POST'])
def charge_customer(username):
    """
    Charges a specified amount to the customer's wallet.

    :param username: The username of the customer
    :type username: str
    :return: JSON response with a success or error message
    :rtype: flask.Response
    """
    customer = User.query.filter_by(username=username).first()
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    data = request.get_json()
    if 'amount' not in data:
        return jsonify({'error': 'Missing amount'}), 400

    amount = data['amount']
    if amount <= 0:
        return jsonify({'error': 'Amount must be positive'}), 400

    customer.wallet_balance += amount
    db.session.commit()
    return jsonify({
        'message': f'Wallet charged with ${amount}',
        'wallet_balance': customer.wallet_balance
    }), 200

@app.route('/customers/<string:username>/deduct', methods=['POST'])
def deduct_from_customer(username):
    """
    Deducts a specified amount from the customer's wallet.

    :param username: The username of the customer
    :type username: str
    :return: JSON response with a success or error message
    :rtype: flask.Response
    """
    customer = User.query.filter_by(username=username).first()
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    data = request.get_json()
    if 'amount' not in data:
        return jsonify({'error': 'Missing amount'}), 400

    amount = data['amount']
    if amount <= 0:
        return jsonify({'error': 'Amount must be positive'}), 400
    if customer.wallet_balance < amount:
        return jsonify({'error': 'Insufficient funds'}), 400

    customer.wallet_balance -= amount
    db.session.commit()
    return jsonify({
        'message': f'${amount} deducted from wallet',
        'wallet_balance': customer.wallet_balance
    }), 200

if __name__ == '__main__':
    app.run(port=4000)
