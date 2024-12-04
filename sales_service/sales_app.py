from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
from db_config import db, init_db
from customer_service.customer_app import User
from inventory_service.inventory_app import Product
import logging

app = Flask(__name__)
init_db(app)
app.config['SECRET_KEY'] = "222222222233333333"



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



class Sale(db.Model):
    """
    Represents a sales transaction.

    :param id: Unique identifier for the sale (primary key)
    :type id: int
    :param username: Username of the customer who made the purchase
    :type username: str
    :param product_name: Name of the product purchased
    :type product_name: str
    :param quantity: Quantity of the product purchased
    :type quantity: int
    :param total_price: Total price of the sale
    :type total_price: float
    :param timestamp: Timestamp when the sale was made
    :type timestamp: datetime
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), db.ForeignKey('User.username'), nullable=False)
    product_name = db.Column(db.String(120), db.ForeignKey('Product.name'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

@app.route('/sales', methods=['POST'])
def make_sale():
    """
    Processes a sale by deducting stock, updating the customer's wallet balance, and recording the sale.

    :return: JSON response with sale details or error message
    :rtype: flask.Response
    """
    data = request.json
    username = data.get('username')
    product_name = data.get('product_name')
    quantity = data.get('quantity', 1)

    if not username or not product_name or quantity <= 0:
        log_operation('/sales', 'POST', username, 400, {"error": "Invalid input."})
        return jsonify({"error": "Invalid input. Provide username, product_name, and valid quantity."}), 400

    customer = User.query.get(username)
    product = Product.query.filter_by(name=product_name).first()

    if not customer:
        log_operation('/sales', 'POST', username, 404, {"error": "Customer not found."})
        return jsonify({"error": "Customer not found."}), 404
    if not product:
        log_operation('/sales', 'POST', username, 404, {"error": "Product not found."})
        return jsonify({"error": "Product not found."}), 404
    if product.stock < quantity:
        log_operation('/sales', 'POST', username, 400, {"error": "Not enough stock available."})
        return jsonify({"error": "Not enough stock available."}), 400

    total_price = product.price * quantity

    if customer.wallet_balance < total_price:
        log_operation('/sales', 'POST', username, 400, {"error": "Insufficient wallet balance."})
        return jsonify({"error": "Insufficient wallet balance."}), 400

    product.stock -= quantity
    customer.wallet_balance -= total_price

    sale = Sale(username=username, product_name=product.name, quantity=quantity, total_price=total_price)
    db.session.add(sale)
    db.session.commit()
    log_operation('/sales', 'POST', username, 201, {"message": "Sale completed successfully."})

    return jsonify({"message": "Sale completed successfully.", "sale": {
        "username": username,
        "product_name": product_name,
        "quantity": quantity,
        "total_price": total_price
    }}), 201

@app.route('/sales/history/<string:username>', methods=['GET'])
def get_sales_history(username):
    """
    Retrieves the sales history of a specific customer.

    :param username: Username of the customer
    :type username: str
    :return: JSON response with sales history or error message
    :rtype: flask.Response
    """
    sales = Sale.query.filter_by(username=username).all()
    if not sales:
        log_operation(f'/sales/history/{username}', 'GET', username, 404, {"error": "No sales found."})
        return jsonify({"error": "No sales found for the customer."}), 404

    log_operation(f'/sales/history/{username}', 'GET', username, 200)
    return jsonify(
        [
            {
                "product_name": sale.product_name,
                "quantity": sale.quantity,
                "total_price": sale.total_price,
                "timestamp": sale.timestamp
            } 
        for sale in sales
        ]
    )

@app.route('/sales/products', methods=['GET'])
def display_available_products():
    """
    Displays all available products with stock greater than zero.

    :return: JSON response with product details
    :rtype: flask.Response
    """
    products = Product.query.filter(Product.stock > 0).all()
    log_operation('/sales/products', 'GET', None, 200)
    
    return jsonify([{"name": product.name, "price": product.price} for product in products])

@app.route('/sales/products/<string:product_name>', methods=['GET'])
def get_product_details(product_name):
    """
    Retrieves the details of a specific product.

    :param product_name: Name of the product
    :type product_name: str
    :return: JSON response with product details or error message
    :rtype: flask.Response
    """
    product = Product.query.filter_by(name=product_name).first()
    if not product:
        log_operation(f'/sales/products/{product_name}', 'GET', None, 404, {"error": "Product not found."})
        return jsonify({"error": "Product not found."}), 404

    log_operation(f'/sales/products/{product_name}', 'GET', None, 200)
    return jsonify({
        "name": product.name,
        "price": product.price,
        "description": product.description,
        "category": product.category,
        "stock": product.stock
    })

if __name__ == '__main__':
    app.run(port=6000)

