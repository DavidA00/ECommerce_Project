import customer_app
from db_config import db, init_db
import json
import pytest
from customer_app import app

@pytest.fixture
def test_client():
    with app.test_client() as client:
        yield client


def test_register_customer_success(test_client):
    customer = {
        "full_name": "John Doe",
        "username": "johndoe",
        "password": "password123",
        "age": 30,
        "address": "123 Main St",
        "gender": "Male",
        "marital_status": "Single"
    }
    response = test_client.post('/customers/new', json=customer)
    assert response.status_code == 201
    assert response.get_json() == {"message": "Customer registered successfully"}

def test_register_customer_missing_fields(test_client):
    customer = {
        "username": "johndoe",
        "password": "password123"
    }
    response = test_client.post('/customers/new', json=customer)
    assert response.status_code == 400
    assert response.get_json() == {"error": "Missing required fields"}

def test_register_customer_username_taken(test_client):
    customer = {
        "full_name": "John Doe",
        "username": "johndoe",
        "password": "password123",
        "age": 30,
        "address": "123 Main St",
        "gender": "Male",
        "marital_status": "Single"
    }
    response = test_client.post('/customers/new', json=customer)
    assert response.status_code == 400
    assert response.get_json() == {"error": "Username already taken"}

def test_register_customer_invalid_password(test_client):
    customer = {
        "full_name": "John Doe",
        "username": "newUsername",
        "password": "password",
        "age": 30,
        "address": "123 Main St",
        "gender": "Male",
        "marital_status": "Single"
    }
    response = test_client.post('/customers/new', json=customer)
    assert response.status_code == 400
    assert response.get_json() == {"error": "Password must be at least 8 characters long and contain a number."}

def test_get_individual_customer(test_client):
    test_client.post('/customers/new', json={
        "full_name": "John Doe",
        "username": "getjohndoe",
        "password": "password123",
        "age": 30,
        "address": "123 Main St",
        "gender": "Male",
        "marital_status": "Single"
    })
    response = test_client.get('/customers/getjohndoe')
    data = response.get_json()
    assert response.status_code == 200
    neededData = {"full_name": "John Doe",
        "username": "getjohndoe",
        "age": 30,
        "address": "123 Main St",
        "gender": "Male",
        "marital_status": "Single",
        "wallet_balance": 0
        }
    assert data["customer"] == neededData

def test_get_customer_nonexistent(test_client):
    response = test_client.get('/customers/nonexistentuser')
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == "Customer not found"

def test_delete_customer(test_client):
    test_client.post('/customers/new', json={
        "full_name": "John Doe",
        "username": "deletejohndoe",
        "password": "password123",
        "age": 30,
        "address": "123 Main St",
        "gender": "Male",
        "marital_status": "Single"
    })
    response = test_client.delete('/customers/deletejohndoe')
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == "Customer deleted successfully"
    response = test_client.get('/customers/johndoe')

def test_delete_customer_nonexistent(test_client):
    response = test_client.delete('/customers/nonexistentuser')
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == "Customer not found"

def test_update_customer(test_client):
    test_client.post('/customers/new', json={
        "full_name": "John Doe",
        "username": "editjohndoe",
        "password": "password123",
        "age": 30,
        "address": "123 Main St",
        "gender": "Male",
        "marital_status": "Single"
    })
    response = test_client.put('/customers/editjohndoe', json={"age": 35})
    assert response.status_code == 200
    assert response.get_json() == {"message": "Customer updated successfully"}
    customer = test_client.get('/customers/editjohndoe')
    updatedData = {
        "full_name": "John Doe",
        "username": "editjohndoe",
        "age": 35,
        "address": "123 Main St",
        "gender": "Male",
        "marital_status": "Single",
        "wallet_balance": 0.0
    }
    assert json.loads(customer.get_data(as_text=True))["customer"] == updatedData

def test_update_customer_invalid(test_client):
    response = test_client.put('/customers/editjohndoe5000', json={"age": 35})
    assert response.status_code == 404
    assert response.get_json() == {"error": "Customer not found"}

def test_charge_customer(test_client):
    test_client.post('/customers/new', json={
        "full_name": "John Doe",
        "username": "chargejohndoe",
        "password": "password123",
        "age": 30,
        "address": "123 Main St",
        "gender": "Male",
        "marital_status": "Single"
    })
    response = test_client.post('/customers/chargejohndoe/charge', json={"amount": 100})
    assert response.status_code == 200
    data = response.get_json()
    assert data['wallet_balance'] == 100
    assert data['message'] == "Wallet charged with $100"
    response = test_client.get('/customers/chargejohndoe')
    data = json.loads(response.get_data(as_text=True))
    assert data['customer']['wallet_balance'] == 100

def test_charge_customer_negative(test_client):
    test_client.post('/customers/new', json={
        "full_name": "John Doe",
        "username": "chargenegativejohndoe",
        "password": "password123",
        "age": 30,
        "address": "123 Main St",
        "gender": "Male",
        "marital_status": "Single"
    })
    response = test_client.post('/customers/chargenegativejohndoe/charge', json={"amount": -100})
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == "Amount must be positive"

def test_charge_customer_not_included(test_client):
    test_client.post('/customers/new', json={
        "full_name": "John Doe",
        "username": "chargenovaluejohndoe",
        "password": "password123",
        "age": 30,
        "address": "123 Main St",
        "gender": "Male",
        "marital_status": "Single"
    })
    response = test_client.post('/customers/chargenovaluejohndoe/charge', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == "Missing amount"

def test_charge_customer_non_existent(test_client):
    response = test_client.post('/customers/nonexistent/charge', json={"amount": 100})
    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == "Customer not found"

def test_deduct_customer(test_client):
    test_client.post('/customers/new', json={
        "full_name": "John Doe",
        "username": "deductjohndoe",
        "password": "password123",
        "age": 30,
        "address": "123 Main St",
        "gender": "Male",
        "marital_status": "Single"
    })
    response1 = test_client.post('/customers/deductjohndoe/charge', json={"amount": 100})
    response = test_client.post('/customers/deductjohndoe/deduct', json={"amount": 50})
    assert response.status_code == 200
    data = response.get_json()
    assert data['wallet_balance'] == 50
    assert data['message'] == "$50 deducted from wallet"
    response = test_client.get('/customers/deductjohndoe')
    data = json.loads(response.get_data(as_text=True))
    assert data['customer']['wallet_balance'] == 50

def test_deduct_customer_negative(test_client):
    test_client.post('/customers/new', json={
        "full_name": "John Doe",
        "username": "deductnegativejohndoe",
        "password": "password123",
        "age": 30,
        "address": "123 Main St",
        "gender": "Male",
        "marital_status": "Single"
    })
    response1 = test_client.post('/customers/deductnegativejohndoe/charge', json={"amount": 100})
    response = test_client.post('/customers/deductnegativejohndoe/deduct', json={"amount": -100})
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == "Amount must be positive"

def test_deduct_customer_not_included(test_client):
    test_client.post('/customers/new', json={
        "full_name": "John Doe",
        "username": "chargenovaluejohndoe",
        "password": "password123",
        "age": 30,
        "address": "123 Main St",
        "gender": "Male",
        "marital_status": "Single"
    })
    response = test_client.post('/customers/chargenovaluejohndoe/deduct', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == "Missing amount"

def test_deduct_customer_non_existent(test_client):
    response = test_client.post('/customers/nonexistent/deduct', json={"amount": 100})
    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == "Customer not found"

def test_deduct_customer_too_much(test_client):

    test_client.post('/customers/new', json={
        "full_name": "John Doe",
        "username": "deducttoomuchjohndoe",
        "password": "password123",
        "age": 30,
        "address": "123 Main St",
        "gender": "Male",
        "marital_status": "Single"
    })
    response1 = test_client.post('/customers/deducttoomuchjohndoe/charge', json={"amount": 100})
    response2 = test_client.post('/customers/deducttoomuchjohndoe/deduct', json={"amount": 2000})
    assert response2.status_code == 400
    assert response2.json['error'] == 'Insufficient funds'

    response = test_client.get('/customers/deducttoomuchjohndoe')
    data = json.loads(response.get_data(as_text=True))
    assert data['customer']['wallet_balance'] == 100

def test_get_all_customers(test_client):
    response1 = test_client.get('/customers')
    assert response1.status_code == 200
    original = len(response1.json['customers'])

    customer = {
        "full_name": "John Doe",
        "username": "getalljohndoe",
        "password": "password123",
        "age": 30,
        "address": "123 Main St",
        "gender": "Male",
        "marital_status": "Single"
    }
    response = test_client.post('/customers/new', json=customer)

    response2 = test_client.get('/customers')
    assert response2.status_code == 200
    new = len(response2.json['customers'])

    assert new == original + 1

