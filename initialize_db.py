from flask import Flask
from db_config import db
from customer_service.models import Customer  # Import models from all services





app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    print("Creating database tables...")
    db.create_all()
    print("Database initialized successfully.")
