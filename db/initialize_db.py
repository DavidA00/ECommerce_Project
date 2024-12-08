from flask import Flask
from db_config import db
from customer_service.customer_app import User
from inventory_service.inventory_app import Product
from sales_service.sales_app import Sale
from reviews_service.reviews_app import Review
from werkzeug.security import generate_password_hash
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'instance', 'ecommerce.db')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    """
    Initializes the database by creating all required tables and setting up an admin user.

    - Creates tables for `User`, `Product`, `Sale`, and `Review` models.
    - Checks if an admin user exists; if not, creates a default admin user.

    :raises RuntimeError: If app context is not properly set up.
    """

    print("Creating database tables...")
    db.metadata.create_all(db.engine, tables=[
        User.__table__,
        Product.__table__,
        Sale.__table__,
        Review.__table__
    ])

    admin_username = "admin1"
    existing_admin = User.query.filter_by(username=admin_username).first()
    existing_test = User.query.filter_by(username='testuser').first()
    existing_unauthorized = User.query.filter_by(username='unauthorized').first()
    salesuser = User.query.filter_by(username='salesuser').first()
    nosales = User.query.filter_by(username='nosales').first()

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
    
    if not existing_test:
        print("Creating admin user...")
        test_user = User(
            full_name="Test User",
            username='testuser',
            password=generate_password_hash("password123"),
            isadmin=False,
            age=30,
            address="address",
            gender="male",
            marital_status="single",
            wallet_balance=0
        )
        db.session.add(test_user)
        db.session.commit()
        print(f"Test user '{test_user}' created successfully.")
    else:
        print(f"user 'testuser' already exists.")
    
    if not existing_unauthorized:
        print("Creating admin user...")
        unauthorized_user = User(
            full_name="Unauthorized User",
            username='unauthorized',
            password=generate_password_hash("password123"),
            isadmin=False,
            age=30,
            address="address",
            gender="male",
            marital_status="single",
            wallet_balance=0
        )
        db.session.add(unauthorized_user)
        db.session.commit()
        print(f"Unauthorized user 'unauthorized' created successfully.")
    else:
        print(f"user 'unauthorized' already exists.")
    
    if not salesuser:
        print("Creating admin user...")
        sales_user = User(
            full_name="Test User",
            username='salesuser',
            password=generate_password_hash("password1"),
            isadmin=False,
            age=30,
            address="address",
            gender="male",
            marital_status="single",
            wallet_balance=100000
        )
        db.session.add(sales_user)
        db.session.commit()
        print(f"Test user '{sales_user}' created successfully.")
    else:
        print(f"user 'salesuser' already exists.")
    
    if not nosales:
        print("Creating admin user...")
        no_sales_user = User(
            full_name="No Sales",
            username='nosales',
            password=generate_password_hash("password1"),
            isadmin=False,
            age=30,
            address="address",
            gender="male",
            marital_status="single",
            wallet_balance=0
        )
        db.session.add(no_sales_user)
        db.session.commit()
        print(f"Test user '{no_sales_user}' created successfully.")
    else:
        print(f"user 'nosales' already exists.")
    
    existing_laptop = Product.query.filter_by(name='Laptop').first()
    existing_sale = Product.query.filter_by(name='sale').first()
    existing_no_stock = Product.query.filter_by(name='nostock').first()

    if not existing_laptop:
        laptop = Product(
            name="Laptop",
            description='Laptop',
            category='Technology',
            price=1000,
            stock=1000,
        )
        db.session.add(laptop)
        db.session.commit()
    
    if not existing_sale:
        sale_product = Product(
            name="sale",
            description='sale',
            category='Test',
            price=10,
            stock=100,
        )
        db.session.add(sale_product)
        db.session.commit()
    
    if not existing_no_stock:
        laptop = Product(
            name="nostock",
            description='no stock',
            category='Test',
            price=100,
            stock=0,
        )
        db.session.add(laptop)
        db.session.commit()
    
    print("Database initialized successfully.")
