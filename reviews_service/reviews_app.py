from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import datetime
from db_config import db, init_db
from customer_service.customer_app import User
from inventory_service.inventory_app import Product
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity


app = Flask(__name__)
init_db(app)
app.config['SECRET_KEY'] = "222222222233333333"
jwt = JWTManager(app)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), db.ForeignKey('user.username'), nullable=False)
    product_name = db.Column(db.String(120), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    is_flagged = db.Column(db.Boolean, default=False)

    def as_dict(self):
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
    @jwt_required()
    def wrapper(*args, **kwargs):
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        if not user or not user.isadmin:
            return jsonify({"error": "Admins only!"}), 403
        return fn(*args, **kwargs)
    return wrapper


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    inputed_password_hash= generate_password_hash(password, method='bcrypt') 
    if not user or (inputed_password_hash!= user.password):
        return jsonify({"error": "Invalid username or password"}), 401

    token = create_access_token(identity=username, additional_claims={"isadmin": user.isadmin})
    return jsonify({"message": "Login successful", "token": token})



@app.route('/reviews', methods=['POST'])
@jwt_required()
def submit_review():
    username = get_jwt_identity()
    try:
        data = request.json
        review = Review(
            username=username,
            product_name=data['product_name'],
            rating=data['rating'],
            comment=data['comment']
        )
        db.session.add(review)
        db.session.commit()
        return jsonify({"message": "Review submitted successfully", "review": review.as_dict()}), 201
    except KeyError as e:
        return jsonify({"error": f"Missing field: {e}"}), 400
    except IntegrityError:
        return jsonify({"error": "Database error"}), 500


@app.route('/reviews/<int:review_id>', methods=['PUT'])
@jwt_required()
def update_review(review_id):
    username = get_jwt_identity()
    review = Review.query.get_or_404(review_id)
    if review.username != username:
        return jsonify({"error": "Unauthorized to update this review"}), 403

    data = request.json
    review.rating = data.get('rating', review.rating)
    review.comment = data.get('comment', review.comment)
    db.session.commit()
    return jsonify({"message": "Review updated successfully", "review": review.as_dict()})


@app.route('/reviews/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    username = get_jwt_identity()
    review = Review.query.get_or_404(review_id)
    if review.username != username:
        return jsonify({"error": "Unauthorized to delete this review"}), 403
    db.session.delete(review)
    db.session.commit()
    return jsonify({"message": "Review deleted successfully"})


@app.route('/reviews/product/<string:product_name>', methods=['GET'])
def get_product_reviews(product_name):
    reviews = Review.query.filter_by(product_name=product_name, is_flagged= False).all()
    return jsonify([review.as_dict() for review in reviews])

#admin
@app.route('/reviews/customer/<string:username>', methods=['GET'])
@admin_required
def get_customer_reviews(username):
    reviews = Review.query.filter_by(username=username).all()
    return jsonify([review.as_dict() for review in reviews])


@app.route('/reviews/<int:review_id>', methods=['GET'])
@admin_required
def get_review_details(review_id):
    review = Review.query.get_or_404(review_id)
    return jsonify(review.as_dict())


@app.route('/reviews/flag/<int:review_id>', methods=['PUT'])
@admin_required
def flag_review(review_id):
    review = Review.query.get_or_404(review_id)
    review.is_flagged = True
    db.session.commit()
    return jsonify({"message": "Review flagged successfully", "review": review.as_dict()})

if __name__ == '__main__':
    app.run(port=7000)
