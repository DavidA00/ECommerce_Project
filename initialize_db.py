from flask import Flask
from db_config import db
from customer_service.models import User 
from inventory_service.models import Product  
from reviews_service.models import Review  
from sales_service.models import Sale  


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    print("Creating database tables...")
    db.create_all()

    admin_username = "admin1"
    existing_admin = User.query.filter_by(username=admin_username).first()
    
    if not existing_admin:
        print("Creating admin user...")
        admin_user = User(
            full_name="Admin User",
            username=admin_username,
            password=generate_password_hash("password1", method='bcrypt'),
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
