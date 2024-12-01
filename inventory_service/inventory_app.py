from flask import Flask, request, jsonify
from datetime import datetime
from db_config import db, init_db

app = Flask(__name__)
init_db(app)


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Initialize the database
@app.before_first_request
def create_tables():
    db.create_all()


@app.route('/products', methods=['POST'])
def add_product():
    data = request.json
    new_product = Product(
        name=data['name'],
        description=data.get('description', ''),
        price=data['price'],
        stock_quantity=data.get('stock_quantity', 0)
    )
    db.session.add(new_product)
    db.session.commit()

    return jsonify({'message': 'Product added successfully'}), 201


@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    data = request.json
    for key, value in data.items():
        setattr(product, key, value)
    db.session.commit()
    return jsonify({'message': 'Product updated successfully'}), 200


@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):

    product = Product.query.get(product_id)
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
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'stock_quantity': product.stock_quantity
        }
        output.append(prod_data)

    return jsonify({'products': output}), 200


@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    prod_data = {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'stock_quantity': product.stock_quantity
    }
    return jsonify({'product': prod_data}), 200


@app.route('/products/<int:product_id>/stock', methods=['POST'])
def update_stock(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    amount = request.json.get('amount')
    if not isinstance(amount, int):
        return jsonify({'error': 'Amount must be an integer'}), 400
    product.stock_quantity += amount
    if product.stock_quantity < 0:
        return jsonify({'error': 'Stock quantity cannot be negative'}), 400
    db.session.commit()
    return jsonify({'message': 'Stock updated successfully', 'stock_quantity': product.stock_quantity}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
