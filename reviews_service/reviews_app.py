from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import datetime
from db_config import db, init_db

app = Flask(__name__)
init_db(app)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), db.ForeignKey('customer.username'), nullable=False)
    product_name = db.Column(db.String(120), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    is_moderated = db.Column(db.Boolean, default=False)

    def as_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "product_name": self.product_name,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at,
            "is_moderated": self.is_moderated,
        }

@app.route('/reviews', methods=['POST'])
def submit_review():
    try:
        data = request.json
        review = Review(
            username=data['username'],
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
def update_review(review_id):
    review = Review.query.get_or_404(review_id)
    data = request.json
    review.rating = data.get('rating', review.rating)
    review.comment = data.get('comment', review.comment)
    db.session.commit()
    return jsonify({"message": "Review updated successfully", "review": review.as_dict()})

@app.route('/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    return jsonify({"message": "Review deleted successfully"})

@app.route('/reviews/product/<string:product_name>', methods=['GET'])
def get_product_reviews(product_name):
    reviews = Review.query.filter_by(product_name=product_name).all()
    return jsonify([review.as_dict() for review in reviews])

@app.route('/reviews/customer/<string:username>', methods=['GET'])
def get_customer_reviews(username):
    reviews = Review.query.filter_by(username=username).all()
    return jsonify([review.as_dict() for review in reviews])

@app.route('/reviews/<int:review_id>', methods=['GET'])
def get_review_details(review_id):
    review = Review.query.get_or_404(review_id)
    return jsonify(review.as_dict())

@app.route('/reviews/<int:review_id>/moderate', methods=['PUT'])
def moderate_review(review_id):
    review = Review.query.get_or_404(review_id)
    review.is_moderated = True
    db.session.commit()
    return jsonify({"message": "Review moderated successfully", "review": review.as_dict()})

if __name__ == '__main__':
    app.run(debug=True, port=5004)
