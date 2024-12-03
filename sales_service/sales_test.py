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
    assert response.json['sale']['total_price'] == 100 
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
        "product_name": "GetOneProduct",
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
        "username": "salesuser",
        "product_name": "sale"
    }
    response = test_client.post('/sales', json=data)

    assert response.status_code == 400
    assert response.json['error'] == 'Invalid input. Provide username, product_name, and valid quantity.'