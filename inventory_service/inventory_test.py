from db_config import db, init_db
import json
import pytest
from inventory_app import app

@pytest.fixture
def test_client():
    with app.test_client() as client:
        yield client


# CREATING THE PRODUCT

# TODO creating a product with a non-integer stock

def test_create_product(test_client):
    product_data = {
        "name": "TestProduct",
        "description": "This is a test product.",
        "category": "Electronics",
        "price": 99.99,
        "stock": 10
    }
    response = test_client.post('/products/new', json=product_data)
    assert response.status_code == 201
    assert response.json["message"] == "Product added successfully"

def test_create_product_missing_fields(test_client):
    incomplete_data = {
        "name": "TestProductMissing",
        "price": 99.99
    }
    response = test_client.post('/products/new', json=incomplete_data)
    assert response.status_code == 400
    assert "error" in response.json
    assert response.json["error"] == "Missing required fields"

def test_create_product_duplicate_name(test_client):
    product_data = {
        "name": "TestDuplicateProduct",
        "description": "This is a test product.",
        "category": "Electronics",
        "price": 99.99,
        "stock": 10
    }

    response = test_client.post('/products/new', json=product_data)
    assert response.status_code == 201

    response1 = test_client.post('/products/new', json=product_data)
    assert response1.status_code == 400
    assert "error" in response1.json
    assert response1.json["error"] == "Product name already exists"

# EDITING A PRODUCT

# TODO didnt test the update time, need to check how
def test_edit_product(test_client):
    product_data = {
        "name": "EditTestProduct",
        "description": "This is the original description.",
        "category": "Books",
        "price": 15.99,
        "stock": 5
    }
    test_client.post('/products/new', json=product_data)

    updated_data = {
        "description": "Updated description",
        "category": "Stationery",
        "price": 12.99,
        "stock": 10
    }
    response = test_client.put('/products/update/EditTestProduct', json=updated_data)
    assert response.status_code == 200
    assert response.json["message"] == "Product updated successfully"

    response1 = test_client.get('/products/EditTestProduct')
    product = response1.json["product"]
    assert product["description"] == "Updated description"
    assert product["category"] == "Stationery"
    assert product["price"] == 12.99
    assert product["stock"] == 10

    assert response1.status_code == 200
    
def test_edit_product_nonexistent(test_client):
    updated_data = {
        "description": "This should fail.",
        "category": "Toys",
        "price": 9.99,
        "stock": 2
    }
    response = test_client.put('/products/update/NonExistentProduct', json=updated_data)
    assert response.status_code == 404
    assert response.json["error"] == "Product not found"

def test_edit_product_missing_values(test_client):
    product_data = {
        "name": "EditMissingProduct",
        "description": "Initial description.",
        "category": "Gadgets",
        "price": 49.99,
        "stock": 20
    }
    test_client.post('/products/new', json=product_data)

    incomplete_data = {
        "category": "Home Appliances"
    }
    response = test_client.put('/products/update/EditMissingProduct', json=incomplete_data)
    # assert response.status_code == 400
    # assert response.json["error"] == "Missing required fields"

    response1 = test_client.get('/products/EditMissingProduct')
    product = response1.json["product"]
    assert product["description"] == "Initial description."
    assert product["category"] == "Home Appliances"
    assert product["price"] == 49.99
    assert product["stock"] == 20

# DELETING PRODUCTS

def test_delete_product(test_client):
    product_data = {
        "name": "DeleteTestProduct",
        "description": "This is a test product.",
        "category": "Electronics",
        "price": 19.99,
        "stock": 10
    }
    test_client.post('/products/new', json=product_data)

    response = test_client.delete('/products/DeleteTestProduct')
    assert response.status_code == 200
    assert response.json["message"] == "Product deleted successfully"

    response_get = test_client.get('/products/DeleteTestProduct')
    assert response_get.status_code == 404
    assert response_get.json["error"] == "Product not found"

def test_delete_product_nonexistent(test_client):
    response = test_client.delete('/products/NonExistentProduct')
    assert response.status_code == 404
    assert response.json["error"] == "Product not found"

# GETTING ALL PRODUCTS

def test_get_all_products(test_client):
    response = test_client.get('/products')
    original = len(response.json['products'])

    product_data = {
        "name": "GetAllTestProduct",
        "description": "This is a test product.",
        "category": "Electronics",
        "price": 19.99,
        "stock": 10
    }

    response1 = test_client.post('/products/new', json=product_data)

    response2 = test_client.get('/products')
    new = len(response2.json['products'])

    assert new == original + 1
    product = response2.json['products']
    assert product[new - 1]['name'] == 'GetAllTestProduct'
    assert product[new - 1]['description'] == "This is a test product."
    assert product[new - 1]['category'] == "Electronics"
    assert product[new - 1]['price'] == 19.99
    assert product[new - 1]['stock'] == 10

def test_get_product(test_client):
    product_data = {
        "name": "GetOneProduct",
        "description": "This is a test product.",
        "category": "Electronics",
        "price": 19.99,
        "stock": 10
    }

    test_client.post('/products/new', json=product_data)

    response = test_client.get('/products/GetOneProduct')

    product = response.json["product"]
    assert product["name"] == product_data["name"]
    assert product["description"] == product_data["description"]
    assert product["category"] == product_data["category"]
    assert product["price"] == product_data["price"]
    assert product["stock"] == product_data["stock"]

def test_get_nonexistent_product(test_client):
    response = test_client.get('/products/nonexitentproduct')
    
    assert response.status_code == 404
    assert response.json['error'] == "Product not found"

# REMOVING STOCK

def test_deduct_stock(test_client):
    product_data = {
        "name": "DeductTestProduct",
        "description": "This is a test product.",
        "category": "Electronics",
        "price": 19.99,
        "stock": 10
    }
    response = test_client.post('/products/new', json=product_data)

    response1 = test_client.post('/products/stock/DeductTestProduct')
    assert response1.status_code == 200

    response1 = test_client.get('/products/DeductTestProduct')
    assert response1.json['product']['stock'] == 9

def test_deduct_stock_nonexistent(test_client):
    response = test_client.post('/products/stock/nonexitentproduct')
    assert response.status_code == 404
    assert response.json["error"] == "Product not found"