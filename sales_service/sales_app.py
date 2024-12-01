from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
from db_config import db, init_db
from customer_service.customer_app import Customer
from inventory_service.inventory_app import Product

app = Flask(__name__)
init_db(app)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), db.ForeignKey('customer.username'), nullable=False)
    product_name = db.Column(db.Integer, db.ForeignKey('product.name'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

@app.route('/sales', methods=['POST'])
def make_sale():
    data = request.json
    username = data.get('username')
    product_name = data.get('product_name')
    quantity = data.get('quantity', 1)

    if not username or not product_name or quantity <= 0:
        return jsonify({"error": "Invalid input. Provide username, product_name, and valid quantity."}), 400

    customer = Customer.query.get(username)
    product = Product.query.filter_by(name=product_name).first()

    if not customer:
        return jsonify({"error": "Customer not found."}), 404
    if not product:
        return jsonify({"error": "Product not found."}), 404
    if product.stock < quantity:
        return jsonify({"error": "Not enough stock available."}), 400

    total_price = product.price * quantity

    if customer.wallet < total_price:
        return jsonify({"error": "Insufficient wallet balance."}), 400

    product.stock -= quantity
    customer.wallet -= total_price

    sale = Sale(username=username, product_name=product.name, quantity=quantity, total_price=total_price)
    db.session.add(sale)
    db.session.commit()

    return jsonify({"message": "Sale completed successfully.", "sale": {
        "username": username,
        "product_name": product_name,
        "quantity": quantity,
        "total_price": total_price
    }}), 201


@app.route('/sales/history/<string:username>', methods=['GET'])
def get_sales_history(username):
    sales = Sale.query.filter_by(username=username).all()
    if not sales:
        return jsonify({"error": "No sales found for the customer."}), 404
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
    products = Product.query.filter(Product.stock > 0).all()
    return jsonify([{"name": product.name, "price": product.price} for product in products])


@app.route('/sales/products/<string:product_name>', methods=['GET'])
def get_product_details(product_name):
    product = Product.query.filter_by(name=product_name).first()
    if not product:
        return jsonify({"error": "Product not found."}), 404
    return jsonify({
        "name": product.name,
        "price": product.price,
        "description": product.description,
        "category": product.category,
        "stock": product.stock
    })



if __name__ == '__main__':
    app.run( port=6000)
