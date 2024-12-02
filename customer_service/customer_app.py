from flask import Flask, request, jsonify
from db_config import db, init_db

app = Flask(__name__)
init_db(app)
app.config['SECRET_KEY'] = "222222222233333333"

class User(db.Model):
    __tablename__ = 'User'
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), primary_key=True, nullable=False)
    password = db.Column(db.String(100), nullable=False) 
    isadmin = db.Column(db.Boolean, default = False)
    age = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    marital_status = db.Column(db.String(10), nullable=False)
    wallet_balance = db.Column(db.Float, default=0.0)


@app.route('/customers/new', methods=['POST'])
def register_customer():

    data = request.get_json()
    required_fields = ['full_name', 'username', 'password', 'age', 'address', 'gender', 'marital_status']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already taken'}), 400


    if len(data['password']) < 8 or not any(char.isdigit() for char in data['password']):
        logger.warning("Registration failed: Weak password.")
        return jsonify({'error': 'Password must be at least 8 characters long and contain a number.'}), 400

    hashed_password = generate_password_hash(data['password'], method='bcrypt')

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
    customer = User.query.filter_by(username=username).first()
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': 'Customer deleted successfully'}), 200

@app.route('/customers/<string:username>', methods=['PUT'])
def update_customer(username):
    customer = User.query.filter_by(username=username).first()
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    data = request.get_json()
    for field in ['full_name', 'password', 'age', 'address', 'gender', 'marital_status']:
        if field in data:
            if field == 'password':  
                data[field] = generate_password_hash(data[field], method='bcrypt')
            setattr(customer, field, data[field])

    db.session.commit()
    return jsonify({'message': 'Customer updated successfully'}), 200

@app.route('/customers', methods=['GET'])
def get_all_customers():
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
