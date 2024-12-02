from flask import Flask
from db_config import db
from customer_service.customer_app import User 
from inventory_service.inventory_app import Product   
from sales_service.sales_app import Sale  
from reviews_service.reviews_app import Review 
from werkzeug.security import generate_password_hash, check_password_hash
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'instance', 'ecommerce.db')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    print("Creating database tables...")
    db.metadata.create_all(db.engine, tables=[
        User.__table__,
        Product.__table__,
        Sale.__table__,
        Review.__table__
    ])

    admin_username = "admin1"
    existing_admin = User.query.filter_by(username=admin_username).first()
    
    if not existing_admin:
        print("Creating admin user...")
        admin_user = User(
            full_name="Admin User",
            username=admin_username,
            password=generate_password_hash("password1"),
            isadmin=True,
            age=30,
            address="Admin Headquarters",
            gender="Other",
            marital_status="Single",
            wallet_balance=0.0
        )
        db.session.add(admin_user)
        db.session.commit()
        print(f"Admin user '{admin_username}' created successfully.")
    else:
        print(f"Admin user '{admin_username}' already exists.")


    print("Database initialized successfully.")
