from db_config import db, init_db
import json
import pytest
from sales_app import app

@pytest.fixture
def test_client():
    with app.test_client() as client:
        yield client


def test_make_sale(test_client):
    data = {
        "username": "salesuser",
        "product_name": "sale",
        "quantity": 2
    }
    response = test_client.post('/sales', json=data)

    assert response.status_code == 201
    assert response.json['message'] == 'Sale completed successfully.'
    assert response.json['sale']['quantity'] == 2 
    assert response.json['sale']['total_price'] == 20 
    assert response.json['sale']['username'] == "salesuser"
    assert response.json['sale']['product_name'] == "sale"

def test_make_sale_customer_nonexistent(test_client):
    data = {
        "username": "nonexistentuser",
        "product_name": "sale",
        "quantity": 1
    }
    response = test_client.post('/sales', json=data)

    assert response.status_code == 404
    assert response.json['error'] == 'Customer not found.'

def test_make_sale_product_nonexistent(test_client):
    data = {
        "username": "salesuser",
        "product_name": "NonExistentProduct",
        "quantity": 1
    }
    response = test_client.post('/sales', json=data)

    assert response.status_code == 404
    assert response.json['error'] == 'Product not found.'

def test_make_sale_insufficient_stock(test_client):
    data = {
        "username": "testuser",
        "product_name": "sale",
        "quantity": 101
    }
    response = test_client.post('/sales', json=data)

    assert response.status_code == 400
    assert response.json['error'] == 'Not enough stock available.'

def test_make_sale_insufficient_balance(test_client):
    data = {
        "username": "testuser",
        "product_name": "sale",
        "quantity": 1
    }
    response = test_client.post('/sales', json=data)

    assert response.status_code == 400
    assert response.json['error'] == 'Insufficient wallet balance.'

def test_make_sale_invalid_input(test_client):
    data = {
        "product_name": "sale"
    }
    response = test_client.post('/sales', json=data)

    assert response.status_code == 400
    assert response.json['error'] == 'Invalid input. Provide username, product_name, and valid quantity.'

# GETTING SALES

def test_get_user_sales(test_client):
    data = {
        "username": "salesuser",
        "product_name": "Laptop",
        "quantity": 1
    }
    response = test_client.post('/sales', json=data)
    response = test_client.get('/sales/history/salesuser')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) > 0
    assert data[-1]['product_name'] == 'Laptop'

def test_get_user_without_sales(test_client):
    response = test_client.get('/sales/history/nosales')
    assert response.status_code == 404
    assert response.json['error'] == "No sales found for the customer."

def test_get_nonexitent_user_sales(test_client):
    response = test_client.get('/sales/history/nonexistentuser')
    assert response.status_code == 404
    assert response.json['error'] == "No sales found for the customer."

def test_get_all_products(test_client):
    response = test_client.get('/sales/products')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) > 0
    assert {"name": "Laptop", "price": 1000} in data
    assert {"name": "nostock", "price": 100} not in data

def test_get_product_info(test_client):
    response = test_client.get('/sales/products/sale')
    data = response.get_json()
    assert response.status_code == 200

    data_compare = {
        "name": 'sale',
        "price": 10,
        "description": 'sale',
        "category": 'Test',
        "stock": 98
    }
    assert data == data_compare

def test_get_product_info_nonexistent(test_client):
    response = test_client.get('/sales/products/nonexistent_product')
    data = response.get_json()
    assert response.status_code == 404
    assert data == {"error": "Product not found."}
