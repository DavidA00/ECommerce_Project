from flask import Flask, request, jsonify
from datetime import datetime
from db_config import db, init_db
import logging

app = Flask(__name__)
init_db(app)
app.config['SECRET_KEY'] = "222222222233333333"


# Configure logging
logging.basicConfig(
    filename='logs.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_operation(endpoint, method, username=None, status=None, data=None):
    """
    Logs API operations to a file.

    :param endpoint: The API endpoint accessed
    :type endpoint: str
    :param method: The HTTP method used
    :type method: str
    :param username: The username of the user performing the operation (optional)
    :type username: str
    :param status: The HTTP status code returned
    :type status: int
    :param data: Additional data to log (optional)
    :type data: dict
    """
    log_entry = {
        "endpoint": endpoint,
        "method": method,
        "username": username,
        "status": status,
        "data": data
    }
    logging.info(log_entry)


class Product(db.Model):
    """
    Represents a product in the inventory system.

    :param name: Name of the product (primary key)
    :type name: str
    :param description: Description of the product
    :type description: str
    :param category: Category of the product
    :type category: str
    :param price: Price of the product
    :type price: float
    :param stock: Stock quantity of the product (default: 0)
    :type stock: int
    :param created_at: Timestamp of product creation (default: current UTC time)
    :type created_at: datetime
    :param updated_at: Timestamp of last product update (default: current UTC time, auto-updates on modification)
    :type updated_at: datetime
    """
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
    """
    Adds a new product to the inventory.

    :return: JSON response with a success or error message
    :rtype: flask.Response
    """
    data = request.get_json()
    required_fields = ['name', 'category', 'price']
    if not all(field in data for field in required_fields):
        log_operation('/products/new', 'POST', None, 400, {"error": "Missing required fields"})
        return jsonify({'error': 'Missing required fields'}), 400

    if Product.query.filter_by(name=data['name']).first():
        log_operation('/products/new', 'POST', None, 400, {"error": "Product name already exists"})
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
    log_operation('/products/new', 'POST', None, 201, {"message": "Product added successfully"})
    return jsonify({'message': 'Product added successfully'}), 201


@app.route('/products/update/<string:name>', methods=['PUT'])
def update_product(name):
    """
    Updates the details of an existing product.

    :param name: Name of the product to update
    :type name: str
    :return: JSON response with a success or error message
    :rtype: flask.Response
    """
    product = Product.query.get(name)
    if not product:
        log_operation(f'/products/update/{name}', 'PUT', None, 404, {"error": "Product not found"})
        return jsonify({'error': 'Product not found'}), 404

    data = request.get_json()
    for field in ['name', 'description', 'category', 'price', 'stock']:
        if field in data:
            setattr(product, field, data[field])

    db.session.commit()
    log_operation(f'/products/update/{name}', 'PUT', None, 200, {"message": "Product updated successfully"})
    return jsonify({'message': 'Product updated successfully'}), 200


@app.route('/products/<string:name>', methods=['DELETE'])
def delete_product(name):
    """
    Deletes a product from the inventory.

    :param name: Name of the product to delete
    :type name: str
    :return: JSON response with a success or error message
    :rtype: flask.Response
    """
    product = Product.query.get(name)
    if not product:
        log_operation(f'/products/{name}', 'DELETE', None, 404, {"error": "Product not found"})
        return jsonify({'error': 'Product not found'}), 404

    db.session.delete(product)
    db.session.commit()
    log_operation(f'/products/{name}', 'DELETE', None, 200, {"message": "Product deleted successfully"})
    return jsonify({'message': 'Product deleted successfully'}), 200


@app.route('/products', methods=['GET'])
def get_all_products():
    """
    Retrieves a list of all products in the inventory.

    :return: JSON response with a list of products
    :rtype: flask.Response
    """
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

    log_operation('/products', 'GET', None, 200)

    return jsonify({'products': output}), 200

@app.route('/products/<string:name>', methods=['GET'])
def get_product(name):
    """
    Retrieves the details of a specific product.

    :param name: Name of the product to retrieve
    :type name: str
    :return: JSON response with product details or an error message
    :rtype: flask.Response
    """
    product = Product.query.get(name)
    if not product:
        log_operation(f'/products/{name}', 'GET', None, 404, {"error": "Product not found"})
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
    log_operation(f'/products/{name}', 'GET', None, 200)
    return jsonify({'product': prod_data}), 200


@app.route('/products/stock/<string:name>', methods=['POST'])
def deducting_stock(name):
    """
    Deducts 1 unit of stock for a specific product.

    :param name: Name of the product
    :type name: str
    :return: JSON response with a success or error message and updated stock quantity
    :rtype: flask.Response
    """
    product = Product.query.get(name)
    if not product:
        log_operation(f'/products/stock/{name}', 'POST', None, 404, {"error": "Product not found"})
        return jsonify({'error': 'Product not found'}), 404

    if product.stock <= 0:
        log_operation(f'/products/stock/{name}', 'POST', None, 400, {"error": "Stock quantity cannot be negative"})
        return jsonify({'error': 'Stock quantity cannot be negative'}), 400

    product.stock -= 1
    db.session.commit()
    log_operation(f'/products/stock/{name}', 'POST', None, 200, {"message": "Removed 1 item from Stock successfully"})
    return jsonify({'message': 'Removed 1 item from Stock successfully', 'stock': product.stock}), 200


if __name__ == '__main__':
    app.run(port=5000)

    