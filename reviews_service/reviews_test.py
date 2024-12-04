from db_config import db, init_db
import json
import pytest
from reviews_app import app

@pytest.fixture
def test_client():
    with app.test_client() as client:
        yield client

# REQUIRES A TESTUSER
def generate_token(test_client):
    data = {"username": "testuser", "password": "password123"}
    response = test_client.post('/login', json=data)
    token = response.json.get('token')
    return token

def generate_unauthorized_token(test_client):
    new_user_data = {"username": "unauthorized", "password": "password123"}
    response = test_client.post('/login', json=new_user_data)
    token = response.json.get('token')
    return token

def generate_admin_header(test_client):
    data = {"username": "admin1", "password": "password1"}
    response = test_client.post('/login', json=data)
    token = response.json.get('token')
    headers = {'Authorization': f'Bearer {token}'}
    return headers

# LOGGING IN

def test_login_valid(test_client):
    data = {"username": "testuser", "password": "password123"}
    response = test_client.post('/login', json=data)
    assert response.status_code == 200
    assert 'token' in response.json
    assert response.json['message'] == "Login successful"

def test_login_invalid_username(test_client):
    data = {"username": "invaliduser", "password": "password123"}
    response = test_client.post('/login', json=data)
    assert response.status_code == 401
    assert response.json["error"] == "Invalid username or password"

def test_login_invalid_password(test_client):
    data = {"username": "testuser", "password": "wrongpassword"}
    response = test_client.post('/login', json=data)
    assert response.status_code == 401
    assert response.json["error"] == "Invalid username or password"

def test_login_missing_username(test_client):
    data = {"password": "password123"} 
    response = test_client.post('/login', json=data)   
    assert response.status_code == 401
    assert response.json['error'] == "Invalid username or password"


def test_login_missing_password(test_client):
    data = {"username": "testuser"} 
    response = test_client.post('/login', json=data)
    assert response.status_code == 401
    assert response.json['error'] == "Invalid username or password"

# CREATING A REVIEW

# REQUIRES A LAPTOP PRODUCT
def test_submit_review_valid(test_client):
    token = generate_token(test_client)
    headers = {'Authorization': f'Bearer {token}'}
    data = {
        "product_name": "Laptop",
        "rating": 5,
        "comment": "Excellent product!"
    }
    response = test_client.post('/reviews', json=data, headers=headers)
    
    assert response.status_code == 201
    assert response.json['message'] == "Review submitted successfully"
    assert 'review_id' in response.json['review']

def test_submit_review_missing_field(test_client):
    token = generate_token(test_client)
    headers = {'Authorization': f'Bearer {token}'}
    data = {
        "product_name": "Laptop",
        "rating": 5
    }
    response = test_client.post('/reviews', json=data, headers=headers)
    
    assert response.status_code == 400
    assert 'error' in response.json
    assert response.json['error'].startswith('Missing field')

def test_create_review_nonexistent_product(test_client):
    token = generate_token(test_client)
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "product_name": "nonexistent",
        "rating": 5,
        "comment": "Excellent product!"
    }
    
    response = test_client.post('/reviews', json=data, headers=headers)
    
    assert response.status_code == 400
    assert response.json['error'] == "Product does not exist"

# UPDATING A REVIEW
def test_update_review_valid(test_client):
    token = generate_token(test_client)
    headers = {'Authorization': f'Bearer {token}'}
    data = {
        "product_name": "Laptop",
        "rating": 5,
        "comment": "Excellent product!"
    }
    
    response = test_client.post('/reviews', json=data, headers=headers)
    review_id = response.json['review']['review_id']

    update_data = {
        "rating": 4,
        "comment": "Good product!"
    }
    response = test_client.put(f'/reviews/update/{review_id}', json=update_data, headers=headers)
    
    assert response.status_code == 200
    assert response.json['message'] == "Review updated successfully"
    assert response.json['review']['rating'] == 4
    assert response.json['review']['comment'] == "Good product!"

    get_response = test_client.get(f'/reviews/details/{review_id}', headers=generate_admin_header(test_client))
    assert get_response.status_code == 200
    updated_review = get_response.json
    assert updated_review['rating'] == 4
    assert updated_review['comment'] == "Good product!"


def test_update_review_unauthorized(test_client):
    unauthorized_token = generate_unauthorized_token(test_client)
    token = generate_token(test_client)

    headers = {'Authorization': f'Bearer {token}'}
    data = {
        "product_name": "Laptop",
        "rating": 5,
        "comment": "Excellent product!"
    }
    responseGenerateReview = test_client.post('/reviews', json=data, headers=headers)

    review_id = responseGenerateReview.json['review']['review_id']

    unauthorized_headers = {'Authorization': f'Bearer {unauthorized_token}'}
    update_data = {
        "rating": 3,
        "comment": "This should fail"
    }
    
    response = test_client.put(f'/reviews/update/{review_id}', json=update_data, headers=unauthorized_headers)
    
    assert response.status_code == 403
    assert response.json['error'] == "Unauthorized to update this review"

    get_response = test_client.get(f'/reviews/details/{review_id}', headers=generate_admin_header(test_client))
    assert get_response.status_code == 200
    updated_review = get_response.json
    assert updated_review['rating'] == 5
    assert updated_review['comment'] == "Excellent product!"

def test_delete_review_valid(test_client):
    token = generate_token(test_client)
    headers = {'Authorization': f'Bearer {token}'}
    review_data = {
        "product_name": "Laptop",
        "rating": 5,
        "comment": "Excellent product!"
    }
    
    response = test_client.post('/reviews', json=review_data, headers=headers)
    review_id = response.json['review']['review_id']

    response = test_client.delete(f'/reviews/delete/{review_id}', headers=headers)
    
    assert response.status_code == 200
    assert response.json['message'] == "Review deleted successfully"

def test_delete_review_unauthorized(test_client):
    token = generate_token(test_client)
    headers = {'Authorization': f'Bearer {token}'}
    review_data = {
        "product_name": "Laptop",
        "rating": 5,
        "comment": "Excellent product!"
    }
    
    response = test_client.post('/reviews', json=review_data, headers=headers)
    review_id = response.json['review']['review_id']

    unauthorized_token = generate_unauthorized_token(test_client)
    unauthorized_headers = {'Authorization': f'Bearer {unauthorized_token}'}
    
    response = test_client.delete(f'/reviews/delete/{review_id}', headers=unauthorized_headers)
    
    assert response.status_code == 403
    assert response.json['error'] == "Unauthorized to delete this review"

    get_response = test_client.get(f'/reviews/details/{review_id}', headers=generate_admin_header(test_client))
    assert get_response.status_code == 200
    updated_review = get_response.json
    assert updated_review['rating'] == 5
    assert updated_review['comment'] == "Excellent product!"

def test_get_product_reviews(test_client):
    token = generate_token(test_client)
    headers = {'Authorization': f'Bearer {token}'}
    response = test_client.get(f'/reviews/product/Laptop', headers=headers)
    
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_get_customer_reviews_admin(test_client):
    data = {"username": "admin1", "password": "password1"}
    response = test_client.post('/login', json=data)
    token = response.json.get('token')

    headers = {'Authorization': f'Bearer {token}'}
    
    response = test_client.get(f'/reviews/customer/testuser', headers=headers)
    
    assert response.status_code == 200
    assert isinstance(response.json, list)

    assert len(response.json) > 0

def test_get_customer_reviews_non_admin(test_client):
    token = generate_token(test_client)
    headers = {'Authorization': f'Bearer {token}'}
    
    response = test_client.get(f'/reviews/customer/testuser', headers=headers)
    
    assert response.status_code == 403
    assert response.json['error'] == "Admins only!"

def test_get_customer_reviews_invalid_username(test_client):
    response = test_client.get(f'/reviews/customer/invalidusername', headers=generate_admin_header(test_client))
    assert response.status_code == 403

# ADMIN ACCESSING A REVIEW

def test_get_review_details(test_client):
    review_data = {
        "product_name": "Test Product",
        "rating": 4,
        "comment": "This is a test review."
    }
    token = generate_token(test_client)
    headers = {'Authorization': f'Bearer {token}'}
    response = test_client.post('/reviews', json=review_data, headers=headers)
    review_id = response.json['review']['review_id']

    admin_headers = generate_admin_header(test_client)
    response = test_client.get(f'/reviews/details/{review_id}', headers=generate_admin_header(test_client))
    assert response.status_code == 200
    review_data = response.json
    assert review_data['review_id'] == review_id
    assert review_data['product_name'] == "Test Product"
    assert review_data['rating'] == 4
    assert review_data['comment'] == "This is a test review."

def test_get_review_details_no_access(test_client):
    review_data = {
        "product_name": "Test Product",
        "rating": 4,
        "comment": "This is a test review."
    }
    token = generate_token(test_client)
    headers = {'Authorization': f'Bearer {token}'}
    response = test_client.post('/reviews', json=review_data, headers=headers)
    review_id = response.json['review']['review_id']

    response = test_client.get(f'/reviews/details/{review_id}', headers=headers)
    assert response.status_code == 403

def test_get_review_details_invalidid(test_client):
    response = test_client.get(f'/reviews/details/1000000', headers=generate_admin_header(test_client))
    assert response.status_code == 404

# TODO TEST FLAG

