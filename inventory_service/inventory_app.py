from flask import Flask, request, jsonify
from datetime import datetime
from db_config import db, init_db

app = Flask(__name__)
init_db(app)
app.config['SECRET_KEY'] = "222222222233333333"


class Product(db.Model):
    __tablename__ = 'Product'
    name = db.Column(db.String(100), primary_key=True)
    description = db.Column(db.String(500))
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@app.route('/products/new', methods=['POST'])
def add_product():
    data = request.get_json()
    required_fields = ['name', 'category', 'price']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    if Product.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Product name already exists'}), 400

    new_product = Product(
        name=data['name'],
        description=data.get('description', ''),
        category=data['category'],
        price=data['price'],
        stock=data.get('stock', 0)
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message': 'Product added successfully'}), 201

@app.route('/products/update/<string:name>', methods=['PUT'])
def update_product(name):
    product = Product.query.get(name)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    data = request.get_json()
    for field in ['name', 'description', 'category', 'price', 'stock']:
        if field in data:
            setattr(product, field, data[field])

    db.session.commit()
    return jsonify({'message': 'Product updated successfully'}), 200

@app.route('/products/<string:name>', methods=['DELETE'])
def delete_product(name):
    product = Product.query.get(name)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'}), 200

@app.route('/products', methods=['GET'])
def get_all_products():
    products = Product.query.all()
    output = []
    for product in products:
        prod_data = {
            'name': product.name,
            'description': product.description,
            'category': product.category,
            'price': product.price,
            'stock': product.stock,
            'created_at': product.created_at,
            'updated_at': product.updated_at
        }
        output.append(prod_data)
    return jsonify({'products': output}), 200

@app.route('/products/<string:name>', methods=['GET'])
def get_product(name):
    product = Product.query.get(name)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    prod_data = {
        'name': product.name,
        'description': product.description,
        'category': product.category,
        'price': product.price,
        'stock': product.stock,
        'created_at': product.created_at,
        'updated_at': product.updated_at
    }
    return jsonify({'product': prod_data}), 200

@app.route('/products/stock/<string:name>', methods=['POST'])
def deducting_stock(name):
    product = Product.query.get(name)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    if product.stock <= 0:
        return jsonify({'error': 'Stock quantity cannot be negative'}), 400

    product.stock -= 1
    db.session.commit()
    return jsonify({'message': 'Removed 1 item from Stock successfully', 'stock': product.stock}), 200

if __name__ == '__main__':
    app.run(port=5000)
