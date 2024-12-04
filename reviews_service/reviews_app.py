from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import datetime
from db_config import db, init_db
from customer_service.customer_app import User
from inventory_service.inventory_app import Product
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import logging
app = Flask(__name__)
init_db(app)
app.config['SECRET_KEY'] = "222222222233333333"
jwt = JWTManager(app)


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


class Review(db.Model):
    """
    Represents a review submitted by a customer for a product.

    :param id: Unique identifier for the review (primary key)
    :type id: int
    :param username: Username of the customer who submitted the review
    :type username: str
    :param product_name: Name of the product being reviewed
    :type product_name: str
    :param rating: Rating given to the product
    :type rating: int
    :param comment: Review comment
    :type comment: str
    :param created_at: Timestamp when the review was created
    :type created_at: datetime
    :param is_flagged: Indicates if the review has been flagged (default: False)
    :type is_flagged: bool
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), db.ForeignKey('User.username'), nullable=False)
    product_name = db.Column(db.String(120), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    is_flagged = db.Column(db.Boolean, default=False)

    def as_dict(self):
        """
        Converts the Review object into a dictionary.

        :return: Dictionary representation of the review
        :rtype: dict
        """
        return {
            "review_id": self.id,
            "username": self.username,
            "product_name": self.product_name,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at,
            "is_flagged": self.is_flagged
        }

def admin_required(fn):
    """
    Decorator to ensure only admins can access a route.

    :param fn: The route function being wrapped
    :type fn: function
    :return: Wrapper function
    :rtype: function
    """
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        if not user or not user.isadmin:
            log_operation(request.path, request.method, username, 403)
            return jsonify({"error": "Admins only!"}), 403
        return fn(*args, **kwargs)
    return wrapper




@app.route('/login', methods=['POST'])
def login():
    """
    Authenticates a user and returns a JWT token.

    :return: JSON response with a success message and token, or error message
    :rtype: flask.Response
    """
    data = request.json
    username = data.get('username')
    if not 'password' in data:
        return jsonify({"error": "Invalid username or password"}), 401
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        log_operation('/login', 'POST', username, 401)
        return jsonify({"error": "Invalid username or password"}), 401

    token = create_access_token(identity=username, additional_claims={"isadmin": user.isadmin})
    log_operation('/login', 'POST', username, 200)
    return jsonify({"message": "Login successful", "token": token})

@app.route('/reviews', methods=['POST'])
@jwt_required()
def submit_review():
    """
    Submits a new review for a product.

    :return: JSON response with a success message and review details, or an error message
    :rtype: flask.Response
    """
    username = get_jwt_identity()
    try:
        data = request.json
        product = Product.query.filter_by(name=data['product_name']).first()
        if not product:
            log_operation('/reviews', 'POST', username, 401)
            return jsonify({"error": "Product does not exist"}), 400
        review = Review(
            username=username,
            product_name=data['product_name'],
            rating=data['rating'],
            comment=data['comment']
        )
        db.session.add(review)
        db.session.commit()
        log_operation('/reviews', 'POST', username, 201, data)
        return jsonify({"message": "Review submitted successfully", "review": review.as_dict()}), 201
    except KeyError as e:
        log_operation('/reviews', 'POST', username, 400, {"error": f"Missing field: {e}"})
        return jsonify({"error": f"Missing field: {e}"}), 400
    except IntegrityError:
        log_operation('/reviews', 'POST', username, 500)
        return jsonify({"error": "Database error"}), 500

@app.route('/reviews/update/<int:review_id>', methods=['PUT'])
@jwt_required()
def update_review(review_id):
    """
    Updates an existing review.

    :param review_id: ID of the review to update
    :type review_id: int
    :return: JSON response with a success message and updated review details
    :rtype: flask.Response
    """
    username = get_jwt_identity()
    review = Review.query.get_or_404(review_id)
    if review.username != username:
        log_operation(f'/reviews/update/{review_id}', 'PUT', username, 403)
        return jsonify({"error": "Unauthorized to update this review"}), 403

    data = request.json
    review.rating = data.get('rating', review.rating)
    review.comment = data.get('comment', review.comment)
    db.session.commit()
    log_operation(f'/reviews/update/{review_id}', 'PUT', username, 200, data)
    return jsonify({"message": "Review updated successfully", "review": review.as_dict()})

    

@app.route('/reviews/delete/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    """
    Deletes a review.

    :param review_id: ID of the review to delete
    :type review_id: int
    :return: JSON response with a success message or an error message
    :rtype: flask.Response
    """
    username = get_jwt_identity()
    review = Review.query.get_or_404(review_id)
    if review.username != username:
        log_operation(f'/reviews/delete/{review_id}', 'DELETE', username, 403)
        return jsonify({"error": "Unauthorized to delete this review"}), 403

    db.session.delete(review)
    db.session.commit()
    log_operation(f'/reviews/delete/{review_id}', 'DELETE', username, 200)
    return jsonify({"message": "Review deleted successfully"})

@app.route('/reviews/product/<string:product_name>', methods=['GET'])
def get_product_reviews(product_name):
    """
    Retrieves all reviews for a specific product.

    :param product_name: Name of the product
    :type product_name: str
    :return: JSON response with a list of reviews
    :rtype: flask.Response
    """
    reviews = Review.query.filter_by(product_name=product_name, is_flagged=False).all()
    log_operation(f'/reviews/product/{product_name}', 'GET', None, 200)

    return jsonify([review.as_dict() for review in reviews])

@app.route('/reviews/customer/<string:username>', methods=['GET'])
@admin_required
def get_customer_reviews(username):
    """
    Retrieves all reviews submitted by a specific customer.

    :param username: Username of the customer
    :type username: str
    :return: JSON response with a list of reviews
    :rtype: flask.Response
    """
    reviews = Review.query.filter_by(username=username).all()
    log_operation(f'/reviews/customer/{username}', 'GET', get_jwt_identity(), 200)

    return jsonify([review.as_dict() for review in reviews])

@app.route('/reviews/details/<int:review_id>', methods=['GET'])
@admin_required
def get_review_details(review_id):
    """
    Retrieves detailed information about a specific review.

    :param review_id: ID of the review
    :type review_id: int
    :return: JSON response with review details
    :rtype: flask.Response
    """
    review = Review.query.get_or_404(review_id)
    log_operation(f'/reviews/details/{review_id}', 'GET', get_jwt_identity(), 200)

    return jsonify(review.as_dict())

@app.route('/reviews/flag/<int:review_id>', methods=['PUT'])
@admin_required
def flag_review(review_id):
    """
    Flags a review as inappropriate.

    :param review_id: ID of the review to flag
    :type review_id: int
    :return: JSON response with a success message and flagged review details
    :rtype: flask.Response
    """
    review = Review.query.get_or_404(review_id)
    review.is_flagged = True
    db.session.commit()
    log_operation(f'/reviews/flag/{review_id}', 'PUT', get_jwt_identity(), 200)
    return jsonify({"message": "Review flagged successfully", "review": review.as_dict()})

if __name__ == '__main__':
    app.run(port=7000)

