from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

#BASE_DIR = os.path.abspath(os.path.dirname(__file__))
#DATABASE_PATH = os.path.join(BASE_DIR, 'instance', 'ecommerce.db')

DATABASE_PATH = os.path.join('/app', 'instance', 'ecommerce.db')


def init_db(app):
    """
    Initializes the database configuration for the Flask application.

    :param app: The Flask application instance
    :type app: Flask
    :return: None
    :rtype: None
    """
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    db.init_app(app)
